#!/usr/bin/env python3

# Calculates the potential based on a sweeping dipole trap

import numpy as np
from dipoletrapli import DipoleTrapLi, rotate_points, cartesian_product 

beam_params = [
    {
        "w_0": [25e-6  , 25e-6 ], # m
        "z_0": [0   , 0  ], # m
        "Msq": [1.1 , 1.1],
    },
    {
        "w_0": [25e-6  , 25e-6 ], # m
        "z_0": [0   , 0  ], # m
        "Msq": [1.1 , 1.1],
    }
]

