import qiskit
from qiskit.circuit import Parameter
# from qiskit_algorithms import optimizers as qiskit_opt
from qiskit.primitives import StatevectorEstimator, StatevectorSampler
from qiskit.quantum_info import SparsePauliOp
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt

#from . 
import quantum_info as qi

import random


class VQLS:

    def __init__(self, ansatz_type='hardware-efficient', qubits=1, optimizer="COBYQA"):

        self.optimizer = optimizer
        self.num_qubits = qubits

        self.ansatz = self.construct_ansatz(ansatz_type)
        self.circuit = self.construct_circuit()

        self.estimator = StatevectorEstimator()
        self.sampler = StatevectorSampler()


    def pauli_decomposition(self, A):
        # I, X, Y, Z Pauli matrices
        paulis = qi.pauli_matrices

        self.coefficients = [0.5 * np.trace(P @ A) for P in paulis]

        return self.coefficients



    def construct_ansatz(self, ansatz_type):

        if self.num_qubits == 1:
            self.parameters = [Parameter('alpha_0')]

            ansatz = qiskit.QuantumCircuit(1)
            ansatz.h(0)
            ansatz.ry(self.parameters[0], 0)
            # ansatz.rz(self.parameters[1], 0)
        
        return ansatz

    def construct_circuit(self):
        circuit = qiskit.QuantumCircuit(self.num_qubits)

        circuit.compose(self.ansatz, inplace=True)

        return circuit

    def compute_expectation_values(self, parameters):
        if self.num_qubits == 1:
            estimator = StatevectorEstimator()
                
            # measure the numerator observable
            N = np.conj(self.A.T) @ np.outer(self.b, np.conj(self.b)) @ self.A
            D = np.conj(self.A.T) @ self.A

            Ni = self.pauli_decomposition(N)
            Di = self.pauli_decomposition(D)

            observable = [[SparsePauliOp(["I", "X", "Y", "Z"], Ni)]]

            pub = (self.circuit, observable, parameters)
                
            job = self.estimator.run([pub])
        
            evs = job.result()[0].data.evs
            ev_n = evs[0][0]
        
            # measure the denominator observable (norm)
            observable = [[SparsePauliOp(["I", "X", "Y", "Z"], Di)]]
        
            pub = (self.circuit, observable, parameters)
            job = self.estimator.run([pub])
        
            evs = job.result()[0].data.evs
            ev_d = evs[0][0]
        
            return ev_n, ev_d

    def cost_function(self, parameters):
        if self.num_qubits == 1:

            exp_val, normalization = self.compute_expectation_values(parameters)

            return 1 - (exp_val/normalization)

    def optimize(self):
        initial_point = [random.random() for _ in self.parameters]
        # history = []
        # def log_step(xk):
        #     cost = self.cost_function()
        #     history.append(np.copy(cost))

        # history.append(np.copy())
        # log_step(parameters_0)

        self.res = opt.minimize(self.cost_function, initial_point, method=self.optimizer)

        # xs = np.linspace(0, 2, len(history))

        # plt.plot(xs, [h for h in history])
        # plt.xlabel("steps")
        # plt.ylabel("global_cost")


    def extract_generators(self):
        pass

    def state_tomography(self, parameters, shots):
        # state tomography to recover relative phase
        pubs = []
        for basis in ["X", "Y", "Z"]:
            qc = self.circuit.copy()
            if basis == "X": # rotate to X basis
                qc.h(0)
            elif basis == "Y": # rotate to Y basis
                qc.sdg(0)
                qc.h(0)
            qc.measure_all() # z basis needs no measurement
            pubs.append((qc, parameters))

        results = self.sampler.run(pubs, shots=shots).result()

        _, norm = self.compute_expectation_values(parameters)

        return VQLSResult(self.A, self.b, self.b_norm, norm, results, shots, parameters)

    def output(self):
        self.circuit.draw('mpl')

    def solve(self, A, b, shots=10_000):
        self.A = np.asarray(A)
        # flatten so column vectors and 1-D arrays both work
        self.b = np.asarray(b).reshape(-1)

        if not np.any(self.b):
            raise ValueError("b must be nonzero")

        # the cost function assumes |b> is a normalized state
        self.b_norm = np.linalg.norm(self.b)
        self.b = self.b / self.b_norm

        self.optimize()
        print(self.res)

        self.results = self.state_tomography(self.res.x, shots)

        return self.results

# take in the results and parse through to do some data analysis
class VQLSResult:

    def __init__(self, A, b, b_norm, norm, results, shots, parameters):
        self.A = A
        self.b = b # already normalized
        self.b_norm = b_norm
        self.norm = norm
        self.results = results
        self.shots = shots
        self.opt_parameters = parameters

    def rescale_answer(self):
        self.bloch = [] # bloch vector
        for result in self.results:
            counts = result.data.meas.get_counts()
            self.bloch.append((counts.get("0", 0) - counts.get("1", 0)) / self.shots) 
            # exp val P(0) - P(1)

        # ρ = 1/2 (I + <X>X + <Y>Y + <Z>Z); 
        self.ρ = 0.5 * (np.eye(2) + self.bloch[0] * qi.X + self.bloch[1] * qi.Y + self.bloch[2] * qi.Z)
        _, eigvecs = np.linalg.eigh(self.ρ)
        x = eigvecs[:, -1]

        # global phase is unobservable, so pick the one that makes A x point along b
        phase = np.vdot(self.b, self.A @ x)
        x = x * np.conj(phase) / abs(phase)

        # rescale
        self.x = x * self.b_norm / np.sqrt(np.real(self.norm))
        return self.x

    def get_probabilites(self):
        z_probs = self.results[-1]

        std_basis_counts = z_probs.data.meas.get_counts()
        return std_basis_counts

if __name__ == "__main__":
    vqls = VQLS()

    A = np.array([
        [1, 1],
        [0, 2]
    ], dtype=complex)

    b = np.array([
        [1],
        [-1]
    ], dtype=complex)

    # pauli_matrices = [np.eye(2), X, Y, Z]
    # coeffs = [0.5 * np.trace(P @ A) for P in pauli_matrices]

    # sum = np.zeros((2, 2), np.complex128)
    # for i, p in enumerate(pauli_matrices):
    #     sum += (coeffs[i] * p)
    # sum

    res = vqls.solve(A, b)
    print(res.get_probabilites())

    quantum_soln = res.rescale_answer()
    classical_soln = np.linalg.solve(A, b).reshape(-1)

    accuracy = abs(np.vdot(quantum_soln, classical_soln))**2 / (np.vdot(quantum_soln, quantum_soln) * np.vdot(classical_soln, classical_soln))
    print(accuracy)
