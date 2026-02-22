OPENQASM 3;
include "stdgates.inc";

// quantum fourier transform on n-qubits

// const int n = 3;

// def test(int[32] n, qubit q) {
//     for int i in [1:n] {
//         rx(π) q;
//     }
// }

qubit[2] qbt;
// test(1, qbt[0]);
ctrl @ rx(π / 3) qbt[0], qbt[1];
