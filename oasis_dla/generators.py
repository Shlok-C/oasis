import numpy as np
import qiskit

I = np.array([[1, 0], [0, 1]], dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)

SINGLE_QUBIT_GENERATORS = {
    'x': X,
    'y': Y,
    'z': Z,
    'rx': X,
    'ry': Y,
    'rz': Z,
    'h': H,
}

TWO_QUBIT_GENERATORS = {
    'rxx': (X, X),
    'ryy': (Y, Y),
    'rzz': (Z, Z),
    'cx': (Z, X),
    'cnot': (Z, X),
    'cz': (Z, Z),
}


def extract_generators(circuit: qiskit.QuantumCircuit) -> list[np.ndarray]:
    n = circuit.num_qubits
    generators = []

    for inst in circuit.data:
        gate_name = inst.operation.name.lower()
        qubits = [circuit.find_bit(q).index for q in inst.qubits]

        if gate_name in SINGLE_QUBIT_GENERATORS:
            gen = SINGLE_QUBIT_GENERATORS[gate_name]
            op = np.eye(1, dtype=complex)
            for i in range(n):
                op = np.kron(op, gen if i == qubits[0] else I)
            generators.append(op)

        elif gate_name in TWO_QUBIT_GENERATORS:
            op1, op2 = TWO_QUBIT_GENERATORS[gate_name]
            op = np.eye(1, dtype=complex)
            for i in range(n):
                if i == qubits[0]:
                    op = np.kron(op, op1)
                elif i == qubits[1]:
                    op = np.kron(op, op2)
                else:
                    op = np.kron(op, I)
            generators.append(op)

    return generators
