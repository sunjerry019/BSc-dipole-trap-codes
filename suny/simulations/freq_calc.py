#!/usr/bin/env python3

import scipy.constants as scpc
import scipy.optimize as scpo
import numpy as np

T  = 5e-3
m  = 9.9883414e-27
w0 = 25e-6

v_atom = np.sqrt((2*scpc.Boltzmann*T)/(m)) 
# v_atom = 1
f = v_atom / (2*w0)

print("v_atom =", v_atom, "m/s")
print("f = \t", f, "Hz")

def func(t):
    v_atom = np.sqrt((2*scpc.Boltzmann*t)/(m)) 
    return v_atom / (2*w0) - 0.1e6

min_temp_for_mhz = scpo.root(func, 100e-6)
print("Min temp = ", min_temp_for_mhz.x[0] * 1e3, "mK")