#!/usr/bin/env python3

import numpy as np
from dipoletrapli import DipoleTrapLi, rotate_points, cartesian_product 

from matplotlib import rc
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

# BEG SETTINGS
rotation_axis = np.array([0,1,0]) # y-axis
angle_between_beams = 20          # degrees
power = 100                       # W
# END SETTINGS

## matplotlib settings
rc('text', usetex = True)
rc('text.latex', preamble = r"\usepackage{libertine}")
rc('font', size = 11, family = "Serif")
## END MPL Settings

x = np.linspace(start = -200, stop = 200, num = 5000, endpoint = True) * 1e-6
z = np.linspace(start = -0.5, stop = 0.5, num = 5000, endpoint = True) * 1e-3
y = np.array([0])

points = cartesian_product(x, y, z)

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

potentials_mk = DipoleTrapLi.trap_temperature(trap_depth = potentials*1e-27)*1e3

# https://matplotlib.org/stable/gallery/images_contours_and_fields/contour_demo.html
potentials_for_contour_plotting = potentials_mk.reshape((len(x), len(z))).T

# fig, ax = plt.subplots()
# cs      = ax.contour(x, z, potentials_for_contour_plotting, levels = 15)
# # ax.clabel(cs, inline=True, fontsize=10)
# ax.set_title('Simplest default with labels')

fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
X, Z = np.meshgrid(x * 1e6, z * 1e3)
# Plot the surface.
surf = ax.plot_surface(X = X, Y = Z, Z = potentials_for_contour_plotting, cmap="inferno_r",
                    linewidth=0, antialiased=True, rasterized = True)

ax.view_init(elev = 31., azim = -50)

# Customize the z axis.
# ax.set_zlim(-1.01, 1.01)
ax.zaxis.set_major_locator(LinearLocator(10))
# A StrMethodFormatter is used automatically
ax.zaxis.set_major_formatter('{x:.02f}')

# DO LABELS
fig.suptitle(f'Static Beam Trap Depth (Beam Separation ${angle_between_beams}^\\circ$, Power ${power}$ W)', y = 0.9)
ax.set_xlabel('$x$ ($\\mu$m)')
ax.set_ylabel('Propagation direction $z$ (mm)')
ax.set_zlabel('Trap Depth (mK $\\cdot k_B$)', linespacing=5)
ax.invert_zaxis()
# END DO LABELS

# Add a color bar which maps values to colors.
fig.colorbar(surf, shrink=0.5, aspect=5, orientation="vertical", pad=0.2)

# plt.tight_layout()
fig.set_size_inches(8, 4.8)
plt.show()

min_point = np.argmin(potentials)
print("Min Potential at =", points[min_point] * 1e6, "um")
print("Trap Depth =", DipoleTrapLi.trap_temperature(trap_depth = potentials[min_point]*1e-27)*1e3, "mK")