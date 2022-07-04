#!/usr/bin/env python3

# # Lens Setup using Raytracing

import numpy as np
import raytracing as RT

# Settings
## Initial
height_0 = 0              # m
yMax = 0.5
angle_0  = 10 # Determined by AOM

## Lenses
f_1 = 75e-3  # m
f_2 = 400e-3
f_3 = 200e-3

path = RT.ImagingPath()
path.label = "Imaging System"

path.append(RT.Space(d = f_1))
path.append(RT.Lens(f = f_1))
path.append(RT.Space(d = f_1 + f_2))
path.append(RT.Lens(f = f_2))
path.append(RT.Space(d = f_2 + f_3))
path.append(RT.Lens(f = f_3))
path.append(RT.Space(d = f_3 * 2))

path.append(RT.Lens(f = f_3))
path.append(RT.Space(d = f_3 * 2))

beam_top    = RT.UniformRays(yMax = height_0 + yMax, yMin = height_0 - yMax, thetaMax = angle_0, thetaMin = angle_0, M = 10, N = 100)
# beam_bottom = RT.UniformRays(yMax = height_0 + yMax, yMin = height_0 - yMax, thetaMax = -angle_0, thetaMin = -angle_0, M = 10, N = 100)
obj = RT.ObjectRays(diameter = 0, color = "white", z = 0, halfAngle = 0, T = 0, H = 0) # A blank object

path.display(raysList = [beam_top, obj], interactive = False, onlyPrincipalAndAxialRays = True) # beam_bottom


