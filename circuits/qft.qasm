OPENQASM 3;
include "stdgates.inc";


// QFT on n-qubits
const int n = 10;

qubit[n] qbts;

for int i in [0:n-1] {
    h qbts[i];
    for int j in [i+1:n-1] {
        cp(2 * π / (2**(j-i+1))) qbts[j], qbts[i];
    }
}

for int i in [0:n/2-1] {
    swap qbts[i], qbts[n-1-i];
}