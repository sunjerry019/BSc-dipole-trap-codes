#!/usr/bin/env python3

import numpy as np
from dipoletrapli import DipoleTrapLi, rotate_points, cartesian_product 

import matplotlib.cm as cm
import matplotlib.pyplot as plt

beam_params = [
    {
        "w_0": [25  , 25 ], # um
        "z_0": [0   , 0  ], # mm
        "Msq": [1.1 , 1.1],
    },
    {
        "w_0": [25  , 25 ], # um
        "z_0": [0   , 0  ], # mm
        "Msq": [1.1 , 1.1],
    }
]

wavelength = 1070  #nm
# We generate in the x-z plane

x = np.linspace(start = -40, stop = 40, num = 5000, endpoint = True) # um
z = np.linspace(start = -20, stop = 20, num = 2000, endpoint = True) # mm
y = np.array([0])

points = cartesian_product(x, y, z)

rotation_axis = np.array([0,1,0]) # y-axis
angle_between_beams = 10
power = 100 # W

points_beam1 = rotate_points(points = points, axis = rotation_axis, degrees =  angle_between_beams/2)
points_beam2 = rotate_points(points = points, axis = rotation_axis, degrees = -angle_between_beams/2)

intensities_1 = DipoleTrapLi.intensity(
    x = points_beam1[:,0], y = points_beam1[:,1], z = points_beam1[:,2], 
    power = power, wavelength = wavelength,
    **beam_params[0]
)
intensities_2 = DipoleTrapLi.intensity(
    x = points_beam2[:,0], y = points_beam2[:,1], z = points_beam2[:,2], 
    power = power, wavelength = wavelength,
    **beam_params[1]
)

potential_1 = DipoleTrapLi.potential(intensity = intensities_1 * 1e12, wavelength = wavelength)*1e27 # Turn into reasonable units
potential_2 = DipoleTrapLi.potential(intensity = intensities_2 * 1e12, wavelength = wavelength)*1e27
potentials = potential_1 + potential_2


# https://matplotlib.org/stable/gallery/images_contours_and_fields/contour_demo.html
if isinstance(potentials, np.ndarray):
    potentials_for_contour_plotting = potentials.reshape((len(x), len(z))).T

    print(potentials_for_contour_plotting.shape)

    fig, ax = plt.subplots()
    cs      = ax.contour(x, z, potentials_for_contour_plotting, levels = 15)
    # ax.clabel(cs, inline=True, fontsize=10)
    ax.set_title('Simplest default with labels')