#import "@preview/quill:0.8.0"
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

So in matrix form this means that $ A = mat(1.5, 0.5; 0.5, -0.5, delim: "[") "and" ket(b) = vec(1/sqrt(2), 1/sqrt(2)) $


So the solution to this equation is: $ ket(x) = A^(-1) ket(b) = vec(1/sqrt(2), -1/sqrt(2)) $
