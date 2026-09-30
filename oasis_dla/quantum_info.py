import numpy as np
import qiskit
import scipy as sp

# Pauli Matrices

X = np.array([
    [0, 1],
    [1, 0]
])

Y = np.array([
    [0, -1j],
    [1j, 0]
])

Z = np.array([
    [1, 0],
    [0, -1]
])

pauli_matrices = [np.eye(2), X, Y, Z]