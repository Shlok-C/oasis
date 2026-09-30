import qiskit
from qiskit.circuit import Parameter
from qiskit_algorithms import optimizers as qiskit_opt
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as sp_opt

import quantum_info as qi


class VQLS:

    def __init__(self, ansatz_type='hardware-efficient', qubits=1, optimizer=qiskit_opt.COBYLA):

        self.ansatz = self.construct_ansatz(ansatz_type)

        self.optimizer = optimizer
        self.num_qubits = qubits

        self.circuit = self.construct_circuit()

    def pauli_decomposition(self, A):
        # I, X, Y, Z Pauli matrices
        paulis = [np.eye(2), qi.X, qi.Y, qi.Z]

        self.coefficients = [0.5 * np.trace(P @ A) for P in paulis]

        return zip(self.coefficients, paulis)



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
            observable = [[SparsePauliOp(["I", "X", "Z"], Ni)]]
            estimator = StatevectorEstimator()
        
            pub = (self.circuit, observable, self.parameters)
            job = estimator.run([pub])
        
            evs = job.result()[0].data.evs
            ev_n = evs[0][0]
        
            # measure the denominator observable (norm)
            observable = [[SparsePauliOp(["I", "X", "Z"], Di)]]
            estimator = StatevectorEstimator()
        
            pub = (vqls, observable, [θ])
            job = estimator.run([pub])
        
            evs = job.result()[0].data.evs
            ev_d = evs[0][0]
        
            return ev_n, ev_d

    def cost_function(self):
        pass

    def optimize(self):
        pass

    def extract_generators():
        pass

    def output(self):
        self.circuit.draw('mpl')

    def solve(self, A, b):
        pass


class VQLSResult:

    def __init__(self):
        pass

