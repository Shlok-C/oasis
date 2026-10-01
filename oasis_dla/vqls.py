import qiskit
from qiskit.circuit import Parameter
# from qiskit_algorithms import optimizers as qiskit_opt
from qiskit.primitives import StatevectorEstimator, StatevectorSampler
from qiskit.quantum_info import SparsePauliOp
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt

from . import quantum_info as qi

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

    def compute_answer(self, parameters):
        self.circuit.measure_all()

        self.sampler = StatevectorSampler()


    def output(self):
        self.circuit.draw('mpl')

    def solve(self, A, b):
        self.A = np.asarray(A)
        # flatten so column vectors and 1-D arrays both work
        self.b = np.asarray(b).reshape(-1)

        if not np.any(self.b):
            raise ValueError("b must be a nonzero vector")

        self.optimize()
        print(self.res)

        self.compute_expectation_values() 


class VQLSResult:

    def __init__(self):
        pass

