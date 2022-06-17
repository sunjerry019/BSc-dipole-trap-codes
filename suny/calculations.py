#!/usr/bin/env python3

import numpy as np
from dipoletrapli import DipoleTrapLi, rotate_points, cartesian_product 

import matplotlib.pyplot as plt
from matplotlib.ticker import LinearLocator

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

wavelength = 1070e-9  #nm
# We generate in the x-z plane

x = np.linspace(start = -200, stop = 200, num = 5000, endpoint = True) * 1e-6
z = np.linspace(start = -0.5, stop = 0.5, num = 5000, endpoint = True) * 1e-3
y = np.array([0])

points = cartesian_product(x, y, z)

rotation_axis = np.array([0,1,0]) # y-axis
angle_between_beams = 20
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

potential_1 = DipoleTrapLi.potential(intensity = intensities_1, wavelength = wavelength)*1e27 # Turn into reasonable units
potential_2 = DipoleTrapLi.potential(intensity = intensities_2, wavelength = wavelength)*1e27
potentials = potential_1 + potential_2

assert isinstance(potentials, np.ndarray)
assert isinstance(potential_1, np.ndarray)
assert isinstance(potential_2, np.ndarray)

# https://matplotlib.org/stable/gallery/images_contours_and_fields/contour_demo.html
potentials_for_contour_plotting = potentials.reshape((len(x), len(z))).T

# fig, ax = plt.subplots()
# cs      = ax.contour(x, z, potentials_for_contour_plotting, levels = 15)
# # ax.clabel(cs, inline=True, fontsize=10)
# ax.set_title('Simplest default with labels')

fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
X, Z = np.meshgrid(x, z)
# Plot the surface.
surf = ax.plot_surface(X = X, Y = Z, Z = potentials_for_contour_plotting, cmap="inferno",
                    linewidth=0, antialiased=True)

# Customize the z axis.
# ax.set_zlim(-1.01, 1.01)
ax.zaxis.set_major_locator(LinearLocator(10))
# A StrMethodFormatter is used automatically
ax.zaxis.set_major_formatter('{x:.02f}')

ax.set_xlabel('x')
ax.set_ylabel('Propagation direction z')

# Add a color bar which maps values to colors.
fig.colorbar(surf, shrink=0.5, aspect=5)

plt.show()