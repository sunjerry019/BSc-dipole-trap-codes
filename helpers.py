#!/usr/bin/env python3

# Some helper functions

from typing import Callable
import numpy as np
import scipy.optimize

def findIntersection(
    func1: Callable[[float | np.ndarray], float | np.ndarray], \
    func2: Callable[[float | np.ndarray], float | np.ndarray], \
    initialGuess: float) -> float:

    def eval_func(x: float | np.ndarray) -> float | np.ndarray:
        return func1(x) - func2(x)

    _result = scipy.optimize.root(fun = eval_func, x0 = initialGuess)

    return _result.x


if __name__ == "__main__":
    def f1(x):
        return 1/x

    def f2(x):
        return x**2 + 5

    x = findIntersection(f1, f2, 1.5)
    print(x)