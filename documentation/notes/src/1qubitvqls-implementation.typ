#import "@preview/quill:0.8.0": *
#import "@preview/cetz:0.5.2"
#import "@preview/physica:0.9.8": *
#import "@preview/cheq:0.4.0": checklist
#import "@preview/numty:0.1.0" as nt
#import "@preview/lovelace:0.3.1": *

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

== Testing the algorithm with 2 different ansatzes

For proper testing, lets first determine an intuitive analysis of how the accuracy of this algorithm with the specific ansatz chosen should work. 

With the base algorithm we use the following ansatz:

#quantum-circuit(
  lstick($ket(0)$), $H$, $R_y (theta)$, rstick($$)
)

And for the second algorithm, we'll use a slightly modified one, with an added $R_z (theta)$ gate appended to the circuit

#quantum-circuit(
  lstick($ket(0)$), $H$, $R_y (theta_0)$, $R_z (theta_1)$, rstick($$)
)

Where the rotation matrices are defined as follows:

$ R_y (theta) = mat(cos(theta/2), -sin(theta/2); sin(theta/2), cos(theta/2), delim: "["), R_z (theta) = mat(1, 0; 0, e^(i theta), delim: "[") $

The intuition behind this is simple. If I want to test this 1 qubit VQLS on a suite of random matrices, then I should think about the possibility for the optimizer to reach the true solution. If the matrix is complex, then it makes sense that just an $R_y$ gate cannot reach the complex solutions, whearas if you add a phase rotation gate with $R_z$ then you get more expressivenss in the ansatz and the ability to 'see' relative phase with complex numbers. 

In testing the algorithm lets first look at what the output is and how the measurments are put together to form the solution.

#let plots_path = "../../../vqls/plots"
#figure(
  image(plots_path + "/1qbt_measurement_boxplot.png")
)

As seen in the above box and whisker plots, the measurement probabilities are properly concentrated near the classical solution 'probabilities', showing that measurements can be accurately 'recomposed' into classical solutions.

Next, we test the algorithm with the first ansatz on a suite of random real matrices. To do these we have to define a notion of 'correctness'.

In these tests, we define 'accuracy' as follows:

```python
def compute_accuracy(self, quantum_solution, classical_solution):
        return 1 - np.linalg.norm(classical_solution - quantum_solution)
```

Then to generate the random matrices, we use the built in random module to form a matrix with all four entries randomized to use as our A. In these tests we keep the $ket(b)$ constant as the $ket(plus)$ state. 

#figure(
  image(plots_path + "/real_tests.png")
)

This plot shows the results of testing 100 random real matrices with a constant $ket(b)$ in the single qubit VQLS algorithm with an ansatz of just $H$, $R_y (theta)$. For the YZ-ansatz, the same test performed yields similar results. 

As expected, the average accuracy compared to classical solutions is determined to be $>0.999$ for both ansatz types, with the Y-ansatz slightly winning out

$ "Average Accuracy for Y-ansatz" = 0.999958 \ "Average Accuracy for YZ-ansatz" = 0.999921 $

// It can be seen for this data set that both algorithms dropped in accuracy for the same matrix around the 50th iteration of testing. 

To extend this testing, we move to random complex matrices.

#figure(
  image(plots_path + "/complex_tests.png")
)

Now we're getting somewhere!

From this testing we determine $ "Average Accuracy for Y-ansatz" = 0.26117 \ "Average Accuracy for YZ-ansatz" = 0.99999 $

So we can see that the Y-ansatz is clearly underparameterized for this specific problem. Now it does put into question, why is the accuracy for the Y-ansatz not just 0? Especially when you look at the graph and can see that the accuracy is mostly driven down by some especially bad outliers. Maybe at some point in the DLA computations this root-cause can be found and addressed? Perhaps something in the algorithm itself. 

From here we want to move onto DLA analysis to characterize the Variance of the cost function, the dimension of the DLA, the $frak(g)$-Purities, and the annihilators of $ket(b)$ to try and interpret and understand the results we've found. 

== DLA Analysis

To compute the dynamical Lie algebra (DLA) we take our ansatz, $V(arrow(theta)) = product U_i (theta_i)$ and extract the generators from each gate. The generators of a gate $ U = e^(-i theta H/2) $ where $ H in [sigma_1, sigma_2, sigma_3] $ The sigmas being pauli matrices X, Y, and Z. This representation of the Lie group $"SU"(2)$ gives way for the idea of the euler parameterization of a special unitary, $ U(phi, theta, psi) = e^(-i phi/2 sigma_1) e^(-i theta/2 sigma_2) e^(-i psi/2 sigma_3) $ Also showing that $"SU"(2)$ is isomorphic to the three-sphere, $S^3$ with three parameters. 

#table(
  columns: (5.5em, auto, auto),
  inset: 10pt,
  align: horizon,
  table.header(
    [$ U = e^(-i theta H/2) $], [*Special Unitary Gate, U*], [*Hermitian Generator, H*],
  ),
  $$,
  $ R_y (theta) $,
  $ Y $,
  $$,
  $ H $,
  $ (X+Z)/sqrt(2) $
)

So to compute the dynamical Lie algebra we take the Lie closure of the two 

#block(
  fill: luma(230),
  inset: 10pt,
  radius: 2pt,
)[Another aside, *the Lie Closure* of of a set of generators is the Lie subalgebra generated by those generators (trippy). Elements of the Lie algebra (which in the context of quantum is always $frak("su")(2)$) are called generators because they generate the Lie group $"SU"(2)$. The Lie subalgebra is generated by the Lie brackets of the elements and themselves until the set is closed, forming a subalgebra of $frak("su")(2)$ So for elements/generators X, Y $ X,Y in frak("su")(2) \ chevron.l X, Y chevron.r_"Lie" <= frak("su")(2) $]

The DLA computation algorithm as formalized in the paper goes as follows:

#figure(
  kind: "algorithm",
  supplement: [],

  pseudocode-list(
    booktabs: true, 
    title: [DLA Construction Algorithm]
  )[
    + compute_dla(generators: [] $in$ #math.frak($s u$)$(2)$):
      + \# Initialize the dynamical Lie algebra
      + #math.frak($g$) = {}
      + *for* gen $in$ generators:
        + *if* $frak(g) + {"gen"}$ is linearly independent *then*:
          + $frak(g) "+=" {"gen"}$
        + *end*
      + \# Now all of the linearly independent generators are in our DLA basis. 
      + From here we perform the Lie brackets of every element with itself and
      + check for linear independence to make sure that our subalgebra is closed \ the Lie bracket 
      
      + $l = 1, r = 0$
      + *while* $l < |frak(g)|$ *do*:
        + *for* m = $0 ... r$ *do*:
          + \# compute Lie bracket of the $l^("th")$ and $m^("th")$ elements
          + $h = [frak(g)[l], frak(g)[m]]$
          + *if* $frak(g) + {h}$ is linearly independent *then*:
            + $frak(g) "+=" {h}$
          + *end*

          
  ]
)

The movitation for studying the DLA of this 1-qubit algorithm comes from testing it on a suite of both real and complex matrices.

So with the current ansatz in the algorithm, $R_y(theta) H$, the intuition is that the single Y-rotation gate does not have the capability to reach certain states. The Y-rotation gate cannot reach complex numbers since its a purely real matrix, so intuitively, complex matrices should have much lower accuracy of being solved. 

So what I did was I took the VQLS algorithm and instantiated two versions of it. One with the same ansatz we've being talking about,

#quantum-circuit(
  lstick($ket(psi)$), 2, $H$, $R_y (theta)$, 1
)

And one of them with a different ansatz, including a Z-rotation gate, that varies the phase of the state, allowing complex amplitudes to be reachable

#quantum-circuit(
  lstick($ket(psi)$), 3, $H$, $R_y (theta_0)$, $R_z (theta_1)$
)