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

This can be derived from the local hamiltonian, $H_L$, specifically the inner portion, $ 1/n sum_j^n ketbra(0_j) times.o II_macron(j) $ where j is the qubit and $macron(j)$ is all other qubits.
$ ketbra(0) = (II - Z) / 2  &=> 1/n sum_j^n (II_j - Z_j) / 2 times.o II_macron(j) \
  &= 1/n (sum_j^n 1/2 II_j times.o II_macron(j) - 1/2 Z_j times.o II_macron(j)) \
  &= 1/n (sum_j^n 1/2 II - sum_j^n 1/2 Z_j) \
  &= 1/n (n/2 II - 1/2 sum_j^n Z_j) \
  &= 1/2 - 1/(2n) sum_j^n Z_j quad "(where" II "is assumed)" 
$
Any cost function can be evaluated using a Hadamard-Test Circuit, where the real part of an expectation value of any hamiltonian can be extracted with some classical postprocessing.

#block(
  fill: luma(230),
  inset: 10pt,
  radius: 4pt
)[ 
  For some observable, U, the *Hadamard-Test*, is a way to extract the expectation value of some observable by directly measuring a circuit by use of controlled gates and an ancilla (extra) qubit

  #quill.quantum-circuit(
      quill.lstick($ket(psi)$, n: 2), 1, quill.mqgate($U$, n: 2, target: 2), 1, [\ ],
      quill.lstick($$), [\ ],
      quill.lstick($ket(0)$), $H$, quill.ctrl(), $H$, 1, quill.meter(), quill.setwire(2), quill.rstick($$)
  )

  Meauring the bottom qubit of this circuit you get $ P(0) = 1/4 (2 + expval(U + U^dagger, psi)) $ and $ P(1) = 1/4 (2 - expval(U + U^dagger, psi)) $ where the expectation value is $ EE = P(0) - P(1) &= 1/2 expval(U + U^dagger, psi) \ &= 1/2 Re(expval(U, psi)) $ The imaginary part of the expectation value can also be extracted by applying a phase gate of $e^(-i pi/2)$ to $ket(psi)$ before the control.
]

=== Ansatz

In the VQLS algorithm, $ket(x)$ is prepared by acting on the zero state with a trainable gate sequence, $V(#params)$, with *$arrow(alpha)$* being a vector of continuous parameters. Typically the ansatz is dependent on gate overhead in the hardware that the algorithm is implemented on, known as a Hardware-Efficient Ansatz.

#block(
  fill: luma(230),
  inset: 10pt,
  radius: 4pt,
)[In addition to the HEA, you can also use the Quantum Alternating Operator Ansatz (QAOA), which takes the $H^(times.o n) ket(0)$ state (equal superposition over all qubits) and evolve it by some two hamiltonians  for a number of layers. 
\ To evolve a state by a hamiltonian means to use the unitary gates generated by the hamiltonians, $H_D, H_M$ $ e^(-i alpha_i H_D), e^(-i alpha_j H_M) $ where $alpha_i$ is a continuous parameter and $i$ is the round in total rounds, $p$, where the ansatz is $ V(arrow(bold(alpha))) = product_l^(2p)  e^(-i alpha_l H_D) e^(-i alpha_(l+1) H_M)  $ where the generated unitaries alternate hamiltonians to form an ansatz. ]
// ket(+)^(times.o n)
=== Training algorithm

In the paper they mention that there are multiple different classical optimizers you could use to train $V(#params)$. One of these algorithms (which I later implement for the 10-qubit VQLS) uses a method that, at each iteration, chooses a random direction, $arrow(bold(w))$ in the parameter space and performs a line search, solving $min_(s in RR) C(arrow(bold(alpha)) + s arrow(bold(w)))$. 