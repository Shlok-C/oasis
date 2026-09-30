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

def construct_dla(generators):
    dla = [] # init empty dla to start
    print('test')

    # go through initial generators
    for gen in generators:
        pot_dla = dla.append(gen)
        print(pot_dla)
        if linear_indep(pot_dla):
            dla = pot_dla

    # now we're left w all the linear indep generators 
    # go thru all combinations of generators and compute brackets, find
    l = 1
    r = 0

    while l < len(dla):
        for m in range(r):
            bracket = commutator(dla[l], dla[m])
            pot_dla = dla.append(bracket)
            if linear_indep(pot_dla):
                dla = pot_dla
        r += 1
        if r == l:
            l += 1
            r = 0

    return dla


            


