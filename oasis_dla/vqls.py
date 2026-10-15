import qiskit
from qiskit.circuit import Parameter
from qiskit.circuit.library import StatePreparation
# from qiskit_algorithms import optimizers as qiskit_opt
from qiskit.primitives import StatevectorEstimator, StatevectorSampler
from qiskit.quantum_info import SparsePauliOp, Statevector
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt

from . import quantum_info as qi

from itertools import product
from functools import reduce

import random


class VQLS:

    def __init__(self, ansatz_type=0, qubits=1, optimizer="COBYQA", cost="local"):

        if qubits > 3:
            raise ValueError("only up to 3 qubits are supported")
        if cost not in ["local", "global", "direct"]:
            raise ValueError("cost must be 'local', 'global' or 'direct'")

        self.optimizer = optimizer
        self.num_qubits = qubits
        self.cost = cost

        # ancilla for the hadamard tests sits above the system qubits
        self.ancilla_idx = qubits

        self.ansatz_type = ansatz_type
        self.ansatz = self.construct_ansatz(ansatz_type)
        self.circuit = self.ansatz

        self.estimator = StatevectorEstimator()
        self.sampler = StatevectorSampler()


    def pauli_decomposition(self, A):
        # X, Y, Z Pauli matrices in the proper basis for n-qubits
        paulis = qi.pauli_matrices
        basis = []
        self.labels = []
        # every n-tuple of length n
        for perm, label in zip(product(paulis, repeat=self.num_qubits), product("IXYZ", repeat=self.num_qubits)):
            pauli = reduce(np.kron, perm) # collapse the tuple into left action kronecker products
            basis.append(pauli)
            self.labels.append("".join(label))

        self.coefficients = [(1/(2**self.num_qubits)) * np.trace(P @ A) for P in basis]

        return self.coefficients

    def prepare_lcu(self, A):
        # A = sum c_l A_l with each A_l a pauli string 
        coefficients = self.pauli_decomposition(A)

        self.lcu_coefficients = []
        self.lcu_labels = []
        for c, label in zip(coefficients, self.labels):
            if abs(c) > 1e-12:
                self.lcu_coefficients.append(c)
                self.lcu_labels.append(label)

        return self.lcu_coefficients, self.lcu_labels

    def construct_ansatz(self, ansatz_type):
        ansatz = qiskit.QuantumCircuit(self.num_qubits)

        num_params = self.num_qubits * (ansatz_type+1)
        self.parameters = [Parameter(f'alpha_{i}') for i in range(num_params)]

        # layer of h gates
        for i in range(self.num_qubits):
            ansatz.h(i)
            ansatz.ry(self.parameters[i], i)
            if ansatz_type == 1:
                ansatz.rz(self.parameters[self.num_qubits + i], i)

        return ansatz

    def construct_controlled_ansatz(self):
        # same gates as the ansatz but each one controlled on the ancilla
        circuit = qiskit.QuantumCircuit(self.num_qubits + 1)

        for i in range(self.num_qubits):
            circuit.ch(self.ancilla_idx, i)
            circuit.cry(self.parameters[i], self.ancilla_idx, i)
            if self.ansatz_type == 1:
                circuit.crz(self.parameters[self.num_qubits + i], self.ancilla_idx, i)

        return circuit

    def construct_U_b(self):
        # U_b|0> = |b>
        self.U_b = qiskit.QuantumCircuit(self.num_qubits)
        self.U_b.append(StatePreparation(self.b), range(self.num_qubits))

        return self.U_b

    def controlled_A(self, circuit, l):
        # apply the pauli string A_l controlled on the ancilla
        for k, p in enumerate(self.lcu_labels[l]):
            qubit = self.num_qubits - 1 - k # leftmost char acts on the highest qubit
            match p:
                case "X":
                    circuit.cx(self.ancilla_idx, qubit)
                case "Y":
                    circuit.cy(self.ancilla_idx, qubit)
                case "Z":
                    circuit.cz(self.ancilla_idx, qubit)

        return circuit

    def hadamard_test(self, l=0, lp=0, j=-1, part="re", kind="local"):
        circuit = qiskit.QuantumCircuit(self.num_qubits + 1)
        system = list(range(self.num_qubits))

        # first hadamard for the hadamard test
        circuit.h(self.ancilla_idx)

        if part == "im":
            # phase shift by -pi/2 to pick out the imaginary part
            circuit.sdg(self.ancilla_idx)

        if kind == "global":
            # γ_l = <0|U_b^dag A_l V|0>, so V and U_b^dag need controls too
            circuit.compose(self.construct_controlled_ansatz(), inplace=True)
            self.controlled_A(circuit, l)
            circuit.append(self.U_b.inverse().to_gate().control(1), [self.ancilla_idx, *system])
        else:
            # apply ansatz
            circuit.compose(self.ansatz, qubits=system, inplace=True)

            self.controlled_A(circuit, l)

            if j != -1:
                # U_b Z_j U_b^dag, the U_b's cancel when the ancilla is 0 so only Z_j is controlled
                circuit.compose(self.U_b.inverse(), qubits=system, inplace=True)
                circuit.cz(self.ancilla_idx, j)
                circuit.compose(self.U_b, qubits=system, inplace=True)

            self.controlled_A(circuit, lp)

        circuit.h(self.ancilla_idx)

        return circuit

    def construct_circuits(self):
        # build every hadamard test once, parameters get bound at each cost evaluation
        self.keys = []
        self.hadamard_circuits = []
        L = len(self.lcu_coefficients)

        # β_{l,lp} for the norm, β_{lp,l} = β_{l,lp}* and β_{l,l} = 1
        for l in range(L):
            for lp in range(l + 1, L):
                for part in ["re", "im"]:
                    self.keys.append(("norm", l, lp, -1, part))
                    self.hadamard_circuits.append(self.hadamard_test(l, lp, -1, part))

        if self.cost == "local":
            # δ_{l,lp,j}, also hermitian in l <-> lp and real on the diagonal
            for l in range(L):
                for lp in range(l, L):
                    for j in range(self.num_qubits):
                        for part in (["re"] if l == lp else ["re", "im"]):
                            self.keys.append(("local", l, lp, j, part))
                            self.hadamard_circuits.append(self.hadamard_test(l, lp, j, part))

        if self.cost == "global":
            for l in range(L):
                for part in ["re", "im"]:
                    self.keys.append(("global", l, -1, -1, part))
                    self.hadamard_circuits.append(self.hadamard_test(l, part=part, kind="global"))

        # measure Z on the ancilla
        self.ancilla_observable = SparsePauliOp("Z" + "I" * self.num_qubits)

        return self.hadamard_circuits

    def run_hadamard_tests(self, parameters):
        # run all the hadamard tests in one batch, μ = re + i*im
        pubs = [(circuit, self.ancilla_observable, parameters) for circuit in self.hadamard_circuits]
        results = self.estimator.run(pubs).result()

        self.mu = {}
        for (kind, l, lp, j, part), result in zip(self.keys, results):
            ev = float(result.data.evs)
            if part == "im":
                ev = 1j * ev
            self.mu[(kind, l, lp, j)] = self.mu.get((kind, l, lp, j), 0) + ev

        return self.mu

    def get_mu(self, kind, l, lp, j=-1):
        if kind == "norm" and l == lp:
            return 1.0 # A_l A_l = I
        if lp < l:
            return np.conj(self.mu[(kind, lp, l, j)])
        return self.mu[(kind, l, lp, j)]

    def norm(self):
        c = self.lcu_coefficients
        norm = 0.0

        for l in range(len(c)):
            for lp in range(len(c)):
                norm += c[l] * np.conj(c[lp]) * self.get_mu("norm", l, lp)

        return np.real(norm)

    def local_cost(self, parameters):
        self.run_hadamard_tests(parameters)
        c = self.lcu_coefficients
        mu_sum = 0.0

        for l in range(len(c)):
            for lp in range(len(c)):
                for j in range(self.num_qubits):
                    mu_sum += c[l] * np.conj(c[lp]) * self.get_mu("local", l, lp, j)

        # mu_sum is real since U_b Z_j U_b^dag is hermitian
        # no abs() here, otherwise A|x> in the -1 eigenspace of Z_j would also give 0 cost
        return 0.5 - 0.5 * np.real(mu_sum) / (self.num_qubits * self.norm())

    def global_cost(self, parameters):
        self.run_hadamard_tests(parameters)
        c = self.lcu_coefficients

        overlap = 0.0
        for l in range(len(c)):
            overlap += c[l] * self.mu[("global", l, -1, -1)]

        return 1 - abs(overlap)**2 / self.norm()

    def compute_expectation_values(self, parameters):
        # measure the numerator observable
        N = np.conj(self.A.T) @ np.outer(self.b, np.conj(self.b)) @ self.A
        D = np.conj(self.A.T) @ self.A

        Ni = self.pauli_decomposition(N)
        Di = self.pauli_decomposition(D)

        observable = [[SparsePauliOp(self.labels, Ni)]]

        pub = (self.circuit, observable, parameters)

        job = self.estimator.run([pub])

        evs = job.result()[0].data.evs
        ev_n = evs[0][0]

        # measure the denominator observable (norm)
        observable = [[SparsePauliOp(self.labels, Di)]]

        pub = (self.circuit, observable, parameters)
        job = self.estimator.run([pub])

        evs = job.result()[0].data.evs
        ev_d = evs[0][0]

        return ev_n, ev_d

    def cost_function(self, parameters):
        match self.cost:
            case "local":
                return self.local_cost(parameters)
            case "global":
                return self.global_cost(parameters)
            case "direct":
                exp_val, normalization = self.compute_expectation_values(parameters)
                return np.real(1 - (exp_val/normalization))

    def optimize(self):
        initial_point = [random.random() for _ in self.parameters]

        self.history = []
        def log_step(intermediate_result):
            self.history.append(intermediate_result.fun)

        self.res = opt.minimize(self.cost_function, initial_point, method=self.optimizer, callback=log_step)

    def plot_history(self):
        plt.plot(range(len(self.history)), self.history)
        plt.xlabel("steps")
        plt.ylabel(f"{self.cost}_cost")

    def extract_generators(self):
        pass

    def readout(self, parameters, shots):
        # exact statevector V(α)|0> = |x>
        bound = self.ansatz.assign_parameters(parameters)
        x = Statevector(bound).data

        # norm <x|A^dag A|x> to rescale with
        if self.cost == "direct":
            _, norm = self.compute_expectation_values(parameters)
        else:
            self.run_hadamard_tests(parameters)
            norm = self.norm()

        # sample in the z basis for the probabilities
        qc = bound.copy()
        qc.measure_all()
        counts = self.sampler.run([qc], shots=shots).result()[0]

        return VQLSResult(self.A, self.b, self.b_norm, norm, x, counts, shots, parameters)

    def output(self):
        self.circuit.draw('mpl')

    def solve(self, A, b, shots=10_000):
        # flatten so column vectors and 1-D arrays both work
        self.A = np.asarray(A)
        self.b = np.asarray(b).reshape(-1)

        dim = 2 ** self.num_qubits
        if self.A.shape != (dim, dim) or len(self.b) != dim:
            raise ValueError(f"A must be {dim}x{dim} and b must have length {dim} for {self.num_qubits} qubits")

        if not np.any(self.b):
            raise ValueError("b must be nonzero")

        # normalize b into a state |b>
        self.b_norm = np.linalg.norm(self.b)
        self.b = self.b / self.b_norm

        if self.cost != "direct":
            # split A into pauli strings and build the hadamard tests
            self.prepare_lcu(self.A)
            self.construct_U_b()
            self.construct_circuits()

        self.optimize()
        print(self.res)

        self.results = self.readout(self.res.x, shots)

        return self.results

    ## testing suite for VQLS:
    def rand(self, real=1):
        return random.random() + (1j * random.random() * (1-real))

    def compute_accuracy(self, qs, cs):
        return 1 - (np.linalg.norm(cs - qs) / np.linalg.norm(cs))

    def compute_fidelity(self, qs, cs):
        qs, cs = np.reshape(qs, -1), np.reshape(cs, -1)
        return abs(np.vdot(qs, cs))**2 / np.real(np.vdot(qs, qs) * np.vdot(cs, cs))

    def generate_dataset(self, random_entries=[1], shots=100):
        Ai = []

        for _ in range(shots):
            # one 2x2 block per qubit
            blocks = [np.ones((2, 2), dtype=complex) for _ in range(self.num_qubits)]

            # insert random entries w/ real or complex numbers
            for A in blocks:
                # entry is 1-4
                for entry in random_entries:

                    binary = bin(int(entry.real) - 1)[2:]
                    if len(binary) == 1: binary = "0" + binary
                    # print(binary)
                    A[int(binary[0])][int(binary[1])] = self.rand(1-entry.imag)

            Ai.append(reduce(np.kron, blocks))

        return Ai

    def accuracy_test(self, dataset, b=None):
        if b is None:
            # uniform superposition
            b = np.ones((2 ** self.num_qubits, 1)) / np.sqrt(2 ** self.num_qubits)

        accuracies = []

        for A in dataset:
            q_soln = self.solve(A, b).solution()
            c_soln = np.linalg.solve(A, b)
            # print(q_soln)
            # print(c_soln)
            acc = self.compute_accuracy(q_soln, c_soln)
            print(acc)
            accuracies.append(acc)

        return accuracies


    def plot_tests(self, accuracies):
        avg_acc = sum(accuracies) / len(accuracies)
        print(f"Average Accuracy = {avg_acc}")
        plt.plot(np.linspace(0, len(accuracies), len(accuracies)), accuracies)
        plt.axhline(avg_acc, linestyle='--', color='black', label="Average Accuracy")
        plt.xlabel("Test Number")
        plt.ylabel("Accuracy")
        plt.legend()

# take in the results and parse through to do some data analysis
class VQLSResult:

    def __init__(self, A, b, b_norm, norm, state, counts, shots, parameters):
        self.A = A
        self.b = b # already normalized
        self.b_norm = b_norm
        self.norm = norm
        self.state = state # normalized |x> straight from the ansatz
        self.counts = counts
        self.shots = shots
        self.opt_parameters = parameters

        self.rescale_answer()

    def rescale_answer(self):
        x = self.state

        # global phase is unobservable, so pick the one that makes A x point along b
        phase = np.vdot(self.b, self.A @ x)
        x = x * np.conj(phase) / abs(phase)

        # rescale
        self.x = (x * self.b_norm / np.sqrt(np.real(self.norm))).reshape(-1, 1)
        return self.x

    def get_probabilities(self):
        std_basis_counts = self.counts.data.meas.get_counts()
        probs = {k: v / self.shots for k, v in std_basis_counts.items()}
        return probs

    def solution(self):
        return self.x

    def __repr__(self):
        return f"Scaled Solution: {self.solution()}\n"

if __name__ == "__main__":
    vqls = VQLS(qubits=3, cost="local")

    coefficients = [1, 0.2, 0.2]

    A_0 = np.eye(8) # 2^3
    A_1 = coefficients[1] * np.kron(np.kron(qi.X, qi.Z), np.eye(2))
    A_2 = coefficients[2] * np.kron(np.kron(qi.X, np.eye(2)), np.eye(2))
    A = A_0 + A_1 + A_2

    b = np.ones(8) / np.sqrt(8)

    res = vqls.solve(A, b)
    print(res.get_probabilities())

    quantum_soln = res.rescale_answer()
    classical_soln = np.linalg.solve(A, b).reshape(-1)

    print(vqls.compute_fidelity(quantum_soln, classical_soln))
