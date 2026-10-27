OPENQASM 3;
include "stdgates.inc";

qubit[2] q_reg;
bit[2] c_reg;

h q_reg[0];
cx q_reg[0], q_reg[1];

// c_reg[0] = measure q_reg[0];
// c_reg[1] = measure q_reg[1];