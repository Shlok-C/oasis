import qiskit
import qiskit.algorithms.optimizers as qiskit_opt
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as sp_opt


class VQLS:

    def __init__(self, ansatz, qubits=1, optimizer=qiskit_opt.COBYLA):

        self.ansatz = ansatz
        self.optimizer = optimizer
        self.num_qubits = qubits

    def matrix_decomposition(self, A):
        pass

    def construct_circuit(self):
        pass

    def compute_expectation_values(self):
        pass

    def cost_function(self):
        pass

    def optimize(self):
        pass

    def solve(self, A, b):
        pass

