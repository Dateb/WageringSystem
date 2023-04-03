import timeit

import numpy as np
from numpy import array
from scipy.optimize import minimize

from Model.Betting.Bets.Bet import Bet


def kelly_jacobian(stakes: np.ndarray, P: np.ndarray, B: np.ndarray) -> np.ndarray:
    total_stakes = sum(stakes)
    V = np.multiply(stakes, B) * (1 - Bet.WIN_COMMISION)

    R = 1 + V - total_stakes

    delta_v = -P / R

    m = B.shape[0]
    B = np.diag(-B) + np.ones(shape=(m, m))

    return -np.matmul(B, delta_v)


def kelly_objective(stakes: np.ndarray, P: np.ndarray, B: np.ndarray) -> float:
    if sum(stakes) >= 1:
        stakes = stakes / sum(stakes)

    total_stakes = sum(stakes)

    R = (1 + np.multiply(stakes, B) * (1 - Bet.WIN_COMMISION)) - total_stakes
    print(R)
    result = P * np.log(R)

    return -sum(result)


def main():
    P = np.array([0.5, 0.5])
    B = np.array([2.1, 2.2])
    print(kelly_objective(array([0, 0]), P, B))

    bounds = [(0, 1) for _ in range(len(P))]
    init_stakes = np.array([1/len(P) for _ in range(len(P))])
    #
    start = timeit.default_timer()
    result = minimize(
        fun=kelly_objective,
        jac=kelly_jacobian,
        x0=init_stakes,
        method="Nelder-Mead",
        args=(P, B),
        bounds=bounds,
        constraints=({'type': "ineq", "fun": lambda x: 0.9999 - sum(x)})
    )
    stop = timeit.default_timer()
    print('Time: ', stop - start)

    print(result)
    print(result.fun)

    # for i in range(20):
    #     start = timeit.default_timer()
    #     result = minimize(
    #         fun=kelly_objective,
    #         jac=kelly_jacobian,
    #         x0=init_stakes,
    #         method="L-BFGS-B",
    #         args=(P, B),
    #         bounds=bnds
    #     )
    #     stop = timeit.default_timer()
    #     print('Time: ', stop - start)
    #     print(-kelly_objective(result.x, P, B))
    #     init_stakes = result.x
    #     # P = np.array([P[0] + uniform(a=-0.05, b=0.05),
    #     #               P[1] + uniform(a=-0.05, b=0.05),
    #     #               P[2] + uniform(a=-0.05, b=0.05),
    #     #               P[3] + uniform(a=-0.05, b=0.05),
    #     #               P[4] + uniform(a=-0.05, b=0.05),
    #     #               P[5] + uniform(a=-0.05, b=0.05),
    #     #               ])
    #
    # print(f"x:{result.x}")


if __name__ == '__main__':
    main()
    print("finished")
