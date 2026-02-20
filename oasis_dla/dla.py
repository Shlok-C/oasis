import numpy as np


def linear_indep(*mats: np.ndarray) -> bool:
    vecs = [m.flatten() for m in mats]
    M = np.column_stack(vecs)
    rank = np.linalg.matrix_rank(M)
    return rank == len(mats)


def commutator(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    return A @ B - B @ A


def single_pass(op_set: list[np.ndarray]) -> list[np.ndarray]:
    new_ops = []
    n = len(op_set)

    for i in range(n):
        for j in range(i + 1, n):
            H = commutator(op_set[i], op_set[j])

            if np.allclose(H, 0):
                continue

            print(f"Calculating [op[{i}], op[{j}]]")

            curr = [m.flatten() for m in (op_set + new_ops)]
            new = curr + [H.flatten()]
            rank_curr = np.linalg.matrix_rank(curr)
            rank_new = np.linalg.matrix_rank(new)

            if rank_new > rank_curr:
                new_ops.append(H)

    return new_ops


def compute_dla(*generators: np.ndarray, lim: int = 20) -> tuple[list, int]:
    basis = list(generators)

    i = 0
    while True:
        print(f"Iteration: {i}, basis size of {len(basis)}")

        new_ops = single_pass(basis)

        if len(new_ops) == 0:
            break

        basis.extend(new_ops)
        i += 1

        for new_op in new_ops:
            print(f"Added\n{new_op}")

        if i > lim:
            print(f"iterations exceeded {lim}, DLA loop terminated")
            break

    rank = np.linalg.matrix_rank([m.flatten() for m in basis])
    return basis, rank
