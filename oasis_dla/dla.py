import numpy as np


def linear_indep(*mats: np.ndarray) -> bool:
    vecs = [m.flatten() for m in mats]
    M = np.column_stack(vecs)
    rank = np.linalg.matrix_rank(M)
    return rank == len(mats)


def commutator(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    return A @ B - B @ A

# bad algorithm
def fast_numerical_construct_dla(generators):
    dla = [] # init empty dla to start
    # print('test')

    # go through initial generators
    for gen in generators:
        pot_dla = dla + [gen]
        if linear_indep(*pot_dla):
            dla = pot_dla

    # now we're left w all the linear indep generators 
    # go thru all combinations of generators and compute brackets, find
    l = 1
    r = 0

    while l < len(dla):
        for m in range(r):
            bracket = commutator(dla[l], dla[m])
            pot_dla = dla + [bracket]
            if linear_indep(*pot_dla):
                dla = pot_dla
        r += 1
        if r == l:
            l += 1
            r = 0

    return dla

def construct_dla(generators):
    S = generators
    S_prev = generators
    S_new = []
    C = 1
    new = 1

    while new > 0:
        S_new = []
        for h0 in generators:
            for h in S_prev:
                C = commutator(h0, h)
                S_union_C = S + [C]
                if linear_indep(*S_union_C):
                    S = S_union_C
                    S_new = S_new + [C]

        new = len(S_new)
        S_prev = S_new

    return S

            


