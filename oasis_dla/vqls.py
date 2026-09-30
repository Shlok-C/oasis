import qiskit
from qiskit.circuit import Parameter
# from qiskit_algorithms import optimizers as qiskit_opt
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt

import quantum_info as qi

import random


class VQLS:

    def __init__(self, ansatz_type='hardware-efficient', qubits=1, optimizer="COBYLA"):

        self.ansatz = self.construct_ansatz(ansatz_type)

        self.optimizer = optimizer
        self.num_qubits = qubits

        self.circuit = self.construct_circuit()

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

        return ansatz

    def construct_circuit(self):
        circuit = qiskit.QuantumCircuit(self.num_qubits)

        circuit.compose(self.ansatz, inplace=True)

        return circuit

    def compute_expectation_values(self):
        if self.num_qubits == 1:
            estimator = StatevectorEstimator()
                
            # measure the numerator observable
            N = np.conj(self.A.T) @ (self.b @ np.conj(self.b.T)) @ self.A
            D = np.conj(self.A.T) @ self.A

            Ni = self.pauli_decomposition(N)
            Di = self.pauli_decomposition(D)

            observable = [[SparsePauliOp(qi.pauli_matrices, Ni)]]
            estimator = StatevectorEstimator()
        
            pub = (self.circuit, observable, self.parameters)
            job = estimator.run([pub])
        
            evs = job.result()[0].data.evs
            ev_n = evs[0][0]
        
            # measure the denominator observable (norm)
            observable = [[SparsePauliOp(qi.pauli_matrices, Di)]]
            estimator = StatevectorEstimator()
        
            pub = (self.circuit, observable, self.parameters)
            job = estimator.run([pub])
        
            evs = job.result()[0].data.evs
            ev_d = evs[0][0]
        
            return ev_n, ev_d

    def cost_function(self):
        if self.num_qubits == 1:

            exp_val, normalization = self.compute_expectation_values()

            return 1 - (exp_val/normalization)

    def optimize(self):
        parameters_0 = [random.random()]
        history = []
        def log_step(xk):
            cost = self.cost_function(xk)
            history.append(np.copy(cost))

        # history.append(np.copy())
        log_step(parameters_0)

        self.res = opt.minimize(self.cost_function, parameters_0, method="COBYQA", callback=log_step)

        xs = np.linspace(0, 2, len(history))

        plt.plot(xs, [h for h in history])
        plt.xlabel("steps")
        plt.ylabel("global_cost")
        print(history)


    def extract_generators():
        pass

    def output(self):
        self.circuit.draw('mpl')

    def solve(self, A, b):
        self.A = A
        self.b = b

        self.optimize()
        print(self.res)


class VQLSResult:

    def __init__(self):
        pass

