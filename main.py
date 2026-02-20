import oasis_dla
import qiskit
import qiskit.qasm3

def main():
    circuit = qiskit.qasm3.load("circuits/bell.qasm")
    generators = oasis_dla.extract_generators(circuit)
    dla = oasis_dla.compute_dla(*generators)

    print(dla)


if __name__ == "__main__":
    main()
