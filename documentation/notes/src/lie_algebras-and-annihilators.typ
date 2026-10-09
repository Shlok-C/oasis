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

== Stabilizers to Annihilators

In group theory, a stabilizer subgroup is a subgroup where all elements have a trivial action on a certain element of the space being acted on. 

For example, with the dihedral group, $D_5$, the group of rotations and reflections acting on the vertices of a pentagon, the stabilizer subgroup of a certain vertex of the pentagon is the set of group elements in $D_5$ that keep the vertex constant. 

This concept continues when going from Lie groups to Lie algebras. Since Lie algebras are the tangent space at the identity of a Lie group, like a sort of 'derivative' of a Lie group, the idea of a stabilizer, where the action of a group is constant, leaving the element unchanged, turns into the annihilator, where the action of the algebra takes the element to zero. 

I think of stabilizers and annihilators like this: A stabilizer is like multiplying by 1. Any group action in a stabilizer is the identity. Differentiating this, since there is no change, makes sense to go to zero, AKA the annihilator.

Exercises:

=== Find the annihilator subalgebra

Let $frak(g) = frak("sl")_2(bb(C))$. Find $"Ann"_frak(g)(ket(0))$.

This means, find the subalgebra of $frak("sl")_2$ that 'annihilate' the vector $ket(0) = vec(1, 0, delim: "[")$

First, choose a basis for $frak("sl")_2$. The typical basis is: $ e = mat(0, 1; 0, 0), f = mat(0, 0; 0, 1), h = mat(1, 0; 0, -1) $

So all elements of the Lie algebra are $ g = a mat(0, 1; 0, 0) + b mat(0, 0; 0, 1) + c mat(1, 0; 0, -1) $

Using this, it turns into a linear system of equations, where $ mat(c, a; b, -c) vec(1, 0) = vec(0, 0) $

Solving this you get that the first column of the matrix is 0, so $c=b=0$ and $a$ is a free variable in $bb(C)$

So $ "Ann"_frak(g)(ket(0)) = {mat(0, a; 0, 0) mid(|) a in bb(C)} = "span"{mat(0, 1; 0, 0)} $

Now, let $frak(h) = "Ann"_frak(g)(ket(0))$. There exists some $frak(h)$ and $frak(h)'$ s/t $ frak(h) plus.o frak(h)' = frak("sl")_2(bb(C)) $

This is a simple case where since the annihilator is the linear span of a single basis element of $frak("sl")_2$, you can easily guess the complement of the annihilator by taking the span of the other two basis elements. So $ frak(h)' = "span"{mat(0, 0; 1, 0), mat(1, 0; 0, -1)} $

where $"dim"(frak(h)) = 1$ and $"dim"(frak(h)') = 2$ so $ "dim"(frak(h)) + "dim"(frak(h)') &= "dim"(frak("sl")_2(bb(C))) \  1+ 2 &= 3 $ 
== Find the annihilator subalgebra

Let $frak(g) = frak("sl")_2(bb(C)) plus.o frak("sl")_2(bb(C))$ acting on $bb(C)^2 times.o bb(C)^2$. Find $"Ann"_frak(g)(ket(psi) times.o ket(0))$ where $ket(psi) = alpha ket(0) + beta ket(1)$