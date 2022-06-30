#!/usr/bin/env python3

import numpy as np
import sympy.physics.optics.gaussopt as GO

# Settings
## Initial
height_0 = 5e-3           # m
angle_0  = np.deg2rad(10) # Determined by AOM

## Lenses
f_1 = 200e-3  # m
f_2 = 300e-3
f_3 = 100e-3


ray = GO.GeometricRay(height_0, angle_0)
L1  = GO.ThinLens(f = f_1)
L2  = GO.ThinLens(f = f_2)
L3  = GO.ThinLens(f = f_3)

ray2 = GO.FreeSpace(d = f_1) * ray
print(ray2)