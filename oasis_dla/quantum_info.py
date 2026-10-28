import numpy as np
import qiskit
import scipy as sp

# Pauli Matrices
I = np.eye(2)

X = np.array([
    [0, 1],
    [1, 0]
], dtype=complex)

Y = np.array([
    [0, -1j],
    [1j, 0]
], dtype=complex)

Z = np.array([
    [1, 0],
    [0, -1]
], dtype=complex)

H = np.array([
    [1, 1],
    [1, -1]
], dtype=complex) / np.sqrt(2)

pauli_matrices = [np.eye(2), X, Y, Z]