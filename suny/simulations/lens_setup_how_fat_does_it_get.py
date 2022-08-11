#!/usr/bin/env python3

import numpy as np
from dipoletrapli import DipoleTrapLi

f1  = 75e-3
f2  = 400e-3
w_0 = DipoleTrapLi.get_spot_size(f = f1, radius_at_lens = 0.5e-3, Msq = 1, wavelength = 1070e-9)

finalRadius = DipoleTrapLi.gaussian_beam_width(z = f2, w_0 = w_0, z_0 = 0, Msq = 1, wavelength = 1070e-9)
print("For 400mm lens: ", finalRadius*1e3, "mm")

f1  = 75e-3
f2  = 200e-3
w_0 = DipoleTrapLi.get_spot_size(f = f1, radius_at_lens = 1e-3, Msq = 1, wavelength = 1070e-9)

finalRadius = DipoleTrapLi.gaussian_beam_width(z = f2, w_0 = w_0, z_0 = 0, Msq = 1, wavelength = 1070e-9)
print("For 200mm lens: ", finalRadius * 1e3, "mm")