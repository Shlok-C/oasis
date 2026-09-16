#import "@preview/quill:0.8.0"
#import "@preview/cetz:0.5.2"
#import "@preview/physica:0.9.8": *
#import "@preview/cheq:0.4.0": checklist

// #set page(width: auto, height: auto, margin: 2em)

#show: checklist

#title[Oasis]
= A study of variational quantum algorithms and their dynamical Lie algebras to analyze different ansatz and cost functions for barren plateau emergence and classical simulability
\
Studying and testing different variational quantum algorithms:
- [/] VQLS
- [ ] QAOA
- [ ] QC-PINN (some implementation for a PDE? Not sure but its pretty interesting to think about variational layers in PINNs )

= August - December

== Task 1: Implement smallest scale

Background: I implemented a 3-qubit VQLS over the summer using PennyLane's guide to understand, but that was awhile so I think the plan is to rederive some of the math by hand to get a better understanding of the paper, then try and implement a 2 qubit version. A main point of understand as well is how the measurements and shots work, and a way to calculate/understand variatiance and deviation

Lit review: Read over VQLS paper again, take notes-ish, re-derive cost function math

=== VQLS Paper notes: 

for a quantum linear systems problem (QLSP), $ A ket(0) = ket(b) $ 

Where A can be decomposed into unitary matrices, $ A = sum_(l=1)^(L) c_l A_l, "where" A_l in \SU(2) $ and $ket(b)$ can be composed by some unitary $ U ket(0) = ket(b) $

This is similar to the assumption with the Variational Quantum Eigensolver where the Hamiltonian (observable measured to get the energy eigenstates) is given as a linear combination of Pauli operators, $ H = sum c_l sigma_l $
Where L is a polynomial function of the \# of qubits (system size).

#let params = $bold(arrow(alpha))$

To solve this problem, VQLS uses an ansatz $V(#params)$ s/t $ V(#params) ket(0) = ket(x(#params)) = ket(x) $ #params is a parameter vector of the ansatz which, as an input to a quantum computer, prepares a potential solution state and runs an efficient circuit that estimates some cost function, $C(#params)$. In simple terms, $C(#params)$ measures how much the component $A ket(x)$ is orthogonal to $ket(b)$.

\
\
=== Cost functions

A simple cost function just measures the overlap of the projector $ ketbra(psi)", "ket(psi) = A ket(x) $ with $ket(b)$. AKA: $ hat(C)_G = "Tr"(ketbra(psi)(II - ketbra(b))) = expval(H_g, x) $ where $ H_g = A^dagger (II - ketbra(b))A $

#block(
  fill: luma(230),
  inset: 10pt,
  radius: 4pt,
)[*Aside for some nontrivial math*: the use of the matrix trace here takes in two density matrices ($ketbra(psi)$ and $ketbra(b)$) and outputs an overlap measure of the two states. This is known as the Hilbert-Schmidt inner product, $ innerproduct(rho, sigma)_("HS") = "Tr"(rho sigma) $ $ rho = ketbra(psi), sigma = ketbra(phi) $]

This cost function is small if $ket(psi)$ is nearly proportional to $ket(psi)$ or if the norm of $ket(psi)$ is small. This leads to the cost function being divided by the norm of $ket(psi)$ to get $ C_G = hat(C)_G \/ braket(psi) = 1 - abs(braket(b, bold(psi)))^2 $ 

Where bold psi is a normalized state. Global cost functions like this however tend to exhibit barren plateaus when training, so to improve, you can use local cost functions instead, using $H_L$ rather than $H_G$, where the effective local hamiltonian is $ H_L = A^dagger U (II - 1/n sum_(j=1)^(n) ketbra(0_j) times.o II_(macron(j))) U^dagger A  $

The global cost function can be broken down like the following: $ C_G = 1 - abs(braket(b, bold(psi)))^2 $ $ = 1 - abs(expval(U^dagger A space V, 0))^2 / expval(V^dagger A^dagger A space V,0) $ $ = 1 - (bra(0) U^dagger A V bold(ketbra(0)) V^dagger A U ket(0)) / expval(V^dagger A^dagger A space V,0) $

where P replaces the bolded $ketbra(0)$, $ P = 1/2 - 1/(2n) sum^(n-1)_j Z_j $

This can be derived from the local hamiltonin, $H_L$, specifically the inner portion, $ 1/n sum_j^n ketbra(0_j) times.o II_macron(j) $ where j is the qubit and $macron(j)$ is all other qubits.
$ ketbra(0) = (II - Z) / 2  &=> 1/n sum_j^n (II_j - Z_j) / 2 times.o II_macron(j) \
  &= 1/n (sum_j^n 1/2 II_j times.o II_macron(j) - 1/2 Z_j times.o II_macron(j)) \
  &= 1/n (sum_j^n 1/2 II - sum_j^n 1/2 Z_j) \
  &= 1/n (n/2 II - 1/2 sum_j^n Z_j) \
  &= 1/2 - 1/(2n) sum_j^n Z_j quad "(where" II "is assumed)" 
$
slkdajdlkajsd