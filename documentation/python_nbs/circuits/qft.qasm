OPENQASM 3;
include "stdgates.inc";


const int n = 4;

qubit[n] qbts;

// general solution for n-qubits
// for int i in [0:n-1] {
//     h qbts[i];
//     for int j in [i+1:n-1] {
//         cp(2 * π / (2**(j-i+1))) qbts[j], qbts[i];
//     }
// }

// for int i in [0:n/2-1] {
//     swap qbts[i], qbts[n-1-i];
// }

// qft on 4 qubits

gate qft q0, q1, q2, q3 {
    h q0;
    cp(π / 2) q0, q1;
    cp(π / 4) q1, q2;
    cp(π / 8) q2, q3;

    h q1;
    cp(π / 2) q1, q2;
    cp(π / 4) q2, q3;

    h q2;
    cp(π / 2) q2, q3;
    
    h q3;
}

qft qbts[0], qbts[1], qbts[2], qbts[3];