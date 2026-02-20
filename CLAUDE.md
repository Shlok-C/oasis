# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**oasis** — Lie algebraic approach to predicting Barren Plateaus in VQA (Variational Quantum Algorithm) training. The core computation is building the Dynamical Lie Algebra (DLA) from a set of quantum gate generators via iterative commutator closure.

## Commands

This project uses `uv` for dependency management (Python 3.12).

```bash
# Run the main entry point
uv run python main.py

# Launch Jupyter for notebook work
uv run jupyter lab

# Add a new dependency
uv add <package>

# Sync dependencies
uv sync

# Stage all changes
git add .
```

## Architecture

### Core Algorithm (notebooks/dla.ipynb)

The DLA is computed by repeatedly taking Lie brackets (commutators) of operators until the set closes:

- `commutator(A, B)` — computes `AB - BA`
- `single_pass(op_set)` — one round of pairwise commutators; returns only new linearly independent operators (checked via `np.linalg.matrix_rank`)
- `compute_dla(*generators, lim=20)` — iterates `single_pass` until no new operators are found; returns the full basis and its rank

Linear independence is tested by flattening matrices into vectors, stacking as columns, and comparing matrix rank before and after adding a candidate.

### Quantum Frameworks

Two frameworks are used in parallel:
- **CUDA-Q (`cudaq`)** — for GPU-accelerated quantum circuit simulation
- **Qiskit** — for circuit loading, visualization, and operator extraction; circuits are loaded from `circuits/` via `qiskit.qasm3.load()`

### Circuit Files (circuits/)

Circuits are written in **OpenQASM 3** and loaded into Qiskit. Currently:
- `bell.qasm` — 2-qubit Bell state preparation (H + CNOT)
- `qft.qasm` — stub for quantum Fourier transform

### Generator Extraction

`extract_gen(gate_func, Θ)` numerically differentiates a parameterized gate `U(Θ)` to recover its generator `H = i · dU/dΘ` via finite differences. This bridges circuit-level gates and the Lie algebra computation.
