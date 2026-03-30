import numpy as np

def linear_indep(*mats: np.ndarray) -> bool:
    vecs = [m.flatten() for m in mats]
    M = np.column_stack(vecs)
    rank = np.linalg.matrix_rank(M)
    return rank == len(mats)

# sl_2 basis

e = np.array([
    [0, 1],
    [0, 0]
])

h = np.array([
    [1, 0],
    [0, -1]
])

f = np.array([
    [0, 0],
    [1, 0]
])

I = np.eye(2)

sl2 = [e, h, f]

sl2_2 = [np.kron(I, X) for X in sl2] + [np.kron(X, I) for X in sl2]

sl2_3 = (
    [np.kron(np.kron(X, I), I) for X in sl2] +
    [np.kron(np.kron(I, X), I) for X in sl2] +
    [np.kron(np.kron(I, I), X) for X in sl2]
)

root2 = np.sqrt(2)
root3 = np.sqrt(3)

GHZ = np.array([
    [root2],    # 000
    [0],
    [0],
    [0],
    [0],
    [0],
    [0],
    [root2],    # 111
])

W = np.array([
    [0],        # 000
    [root3],    # 001
    [root3],    # 010
    [0],        # 011
    [root3],    # 100
    [0],
    [0],
    [0],        # 111
])

def calc_orbit(algebra, vector):
    results = []
    # results.append(vector) # v + g.x

    for M in algebra:
        # print(M)
        action = M @ vector

        if np.allclose(action, 0):
            continue

        if results and not linear_indep(*results, action):
            continue

        results.append(action)

    if not results:
        return [], 0

    matrix = np.column_stack(results)
    rank = np.linalg.matrix_rank(matrix)

    return results, rank

