#import "@preview/quill:0.8.0": *
#import "@preview/cetz:0.5.2"
#import "@preview/physica:0.9.8": *
#import "@preview/cheq:0.4.0": checklist
#import "@preview/numty:0.1.0" as nt

// #set page(width: auto, height: auto, margin: 2em)

#show: checklist

#title[1 Qubit VQLS Implementation]

Goal: The goal for this implementation is to try and make the smallest VQLS possible and show a process that can solve a 2x2 matrix and understand the outputs that come from it

First I'll outline the framework that I'm working back from, my goal with this is to:

- [ ] Get a refresher on the VQLS algorithm (alr partially done by reviewing the paper)
- [ ] Understand the outputs that come from VQLS #math.arrow so after I'll revisit the 3-qubit and then the 10-qubit to better understand

First I'm gonna take some random A and $ket(b)$, so lets say that $ A &= II + 0.5X + 0.5Z \ ket(b) &= H ket(0) $

So in matrix form this means that $ A = mat(1.5, 0.5; 0.5, 0.5, delim: "[") "and" ket(b) = vec(1/sqrt(2), 1/sqrt(2)) $


So the solution to this equation is: $ ket(x) = A^(-1) ket(b) = vec(0, sqrt(2)) $


I'm starting with trying to build this circuit without a hadamard test. Since it's only 1-qubit, it makes sense that I should just be able to calculate the expectation value directly for the cost function. 

In this implementation I'm using a simple ansatz of just a hadamard gate and a single rotation gate around the y-axis.

#quantum-circuit(
  lstick($ket(0)$), $H$, $R_y (theta)$, rstick($$)
)

So only 1 parameter is being optimized in this algorithm. 

From here we use the Pauli decomposition of A to find out what measurement data we need from the circuit, so with $A = II + 0.5X + 0.5Z$, we need expectation values, $ expval(A) = 1 + 0.5 expval(X) + 0.5 expval(Z) $ So two measurements #expval($X$) and #expval($Z$) (since #expval($II$) is constant)

Using these expectation values and some Pauli decomposition we can build the cost function: $ C(theta) = 1 - abs(braket(b, A, x))^2 / expval(A^dagger A, x) $ where the numerator comes out to $ braket(x, A^dagger, b) braket(b, A, x) $ So the two expectation values we care about are, $ N &= A^dagger ketbra(b) A \ D &= A^dagger A $ Where both can be decomposed into $ N &= alpha_0 I + alpha_1 X + alpha_2 Z \ D &= beta_0 I + beta_1 X + beta_2 Z $ Where $alpha$ and $beta$ can be extracted via the formula: $ alpha_i &= 1/2 "Tr"(N P) \ beta_i &= 1/2 "Tr"(D P), P in {I, X, Z} $

Using this pauli string decomposition of the two observables we care about, we can directly measure for the observables using Qiskit's SparsePauliString() function. Doing this we can get the expectation value of the numerator and denominator and then calculate the cost function.

With this computation we can then optimize the cost function of the single parameter $theta$. In this example I used scipy's minimize method in its optimize library, and eventually get to the optimal solution. To extract the classical vector answer though some postprocessing is necessary with the value that we get for the norm, aka the expectation value of D, $expval(A^dagger A, x)$

The answer that is measured from the optimal parameters is a normalized statevector, $ket(x)$ of the probabilities of each bitstring, which in the case of 1 qubit is just 0 and 1. We can expand this measurement and retrieve the answer x as follows, $ x/(||x||) = ket(x) \ x = ||x|| ket(x) $ So when I got the final measurement as $vec(0, 1)$ this makes sense as a normalized output, which we can un-normalize using the norm, $||x|| = 1/sqrt(2)$. With this we get our final answer, $ x = vec(0, sqrt(2)) $

== DLA Analysis

To compute the dynamical Lie algebra (DLA) we take the ansatz, $V(alpha) = R_y (theta) H$ and extract the generators from each gate. The generators of a gate $ U = e^(-i theta H/2) $ where $ H in [sigma_1, sigma_2, sigma_3] $ The sigmas being pauli matrices X, Y, and Z. This representation of the Lie group $"SU"(2)$ gives way for the idea of the euler parameterization of a special unitary, $ U(phi, theta, psi) = e^(-i phi/2 sigma_1) e^(-i theta/2 sigma_2) e^(-i psi/2 sigma_3) $ Also showing that $"SU"(2)$ is isomorphic to the three-sphere, $S^3$