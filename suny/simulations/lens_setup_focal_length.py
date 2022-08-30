#!/usr/bin/env python3

import wave
import numpy as np


def f2_over_f1(msq, wavelength, f3, entry_width, final_width):
    return (msq*wavelength * f3) / (np.pi * entry_width * final_width)

def omega_0_prime(msq, wavelength, f1, f2, f3, entry_width):
    return ((msq*wavelength * f3) * (f1 / f2)) / (np.pi * entry_width)

params = {
    "msq"         : 1,
    "wavelength"  : 1070e-9,
    "entry_width" : 0.5e-3,
    "f3"          : 200e-3
}

x = f2_over_f1(**params, final_width = 25e-6)

print("ratio =" , x)

AvailableOptics = [50, 75, 100, 125, 150, 200]

print("F1\tF2")
for f1 in AvailableOptics:
    f2 = x * f1
    print(f1, "\t", f2)

print("We choose f1 = 75mm, f2 = 200mm, hence we obtain:")
focus = omega_0_prime(**params, f1 = 75e-3, f2 = 200e-3)
print(focus * 1e6, "um")

print("We choose f1 = 75mm, f2 = 400mm, hence we obtain:")
focus = omega_0_prime(**params, f1 = 75e-3, f2 = 400e-3)
print(focus * 1e6, "um")

print("We choose f1 = 75mm, f2 = 500mm, hence we obtain:")
focus = omega_0_prime(**params, f1 = 75e-3, f2 = 500e-3)
print(focus * 1e6, "um")