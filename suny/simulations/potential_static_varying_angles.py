#!/usr/bin/env python3

import numpy as np
from sympy import false
from dipoletrapli import DipoleTrapLi, rotate_points, cartesian_product 

import __init__

from plotter import Plotter
import matplotlib.cm as cm

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

# BEG SETTINGS
rotation_axis = np.array([0,1,0]) # y-axis
power = 100                       # W
numpoints_x = 1000
numpoints_z = 1000
nrows = 2; ncols = 2
begin = 5; end   = 20
figwidth = 8; figheight = 4.8
# END SETTINGS

# TO BE VARIED
angle_between_beams = np.linspace(start = begin, stop = end, num = nrows * ncols, endpoint = True) # degrees

# We generate in the x-z plane
x = np.linspace(start = -150, stop = 150, num = numpoints_x, endpoint = True) * 1e-6 # 5000
z = np.linspace(start = -0.5, stop = 0.5, num = numpoints_z, endpoint = True) * 1e-3 # 5000
y = np.array([0])

points = cartesian_product(x, y, z)

X, Z = np.meshgrid(x * 1e6, z * 1e3)

plotter = Plotter(nrows = nrows, ncols = ncols, sharex = 'col', sharey = 'row', squeeze = False, figsize=(figwidth, figheight))
assert isinstance(plotter.axs, np.ndarray)

allpotentials = []

for angle in angle_between_beams:
    print(f"Calculating for angle = {angle} degrees...", end = "\r")
    points_beam1 = rotate_points(points = points, axis = rotation_axis, degrees =  angle/2)
    points_beam2 = rotate_points(points = points, axis = rotation_axis, degrees = -angle/2)

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
    
    assert isinstance(potentials_mk, np.ndarray)

    # https://matplotlib.org/stable/gallery/images_contours_and_fields/contour_demo.html
    potentials_for_contour_plotting = potentials_mk.reshape((len(x), len(z))).T
    allpotentials.append(potentials_for_contour_plotting)
    print(f"Calculating for angle = {angle} degrees...Done")

allpotentials_np  = np.array(allpotentials)
minimum_potential = np.min(allpotentials_np)
maximum_potential = np.max(allpotentials_np)
colourmeshes = []

for i in range(nrows):
    for j in range(ncols):
        print(f"Making colormesh for angle = {angle_between_beams[i * ncols + j]}...", end = '\r')
        p = plotter.axs[i, j].pcolormesh(X, Z, allpotentials[i * ncols + j], \
            cmap = plotter.COLORMAP_R, \
            vmin = minimum_potential, \
            vmax = maximum_potential, \
            rasterized = True)
        colourmeshes.append(p)

        plotter.axs[i, j].set_title(f"$\\theta = {angle_between_beams[i * ncols + j]}^\\circ$")
        print(f"Making colormesh for angle = {angle_between_beams[i * ncols + j]}...Done")

# cb = plotter.fig.colorbar(cm.ScalarMappable(norm = None, cmap = plotter.COLORMAP_R), ax = plotter.axs)
cb = plotter.fig.colorbar(colourmeshes[0], ax = plotter.axs)

# SET LABELS
cb.ax.set_ylabel('Trap Depth (mK $\\cdot k_{\\!B}$)', rotation=90, labelpad = 15)
plotter.fig.suptitle(f'${power}$ W Static Beam Trap Depth at varying beam separation $\\theta$')
plotter.fig.supxlabel('$x$ ($\\mu$m)')
plotter.fig.supylabel('Propagation direction $z$ (mm)')
# END SET LABELS

# plt.tight_layout()
# plotter.show()
import os
base_dir = os.path.dirname(os.path.realpath(__file__))
plotter.savefig(os.path.join(base_dir, "generated/potential_static_varying_angles.pdf"), format = 'pdf', dpi = 600) # bbox_inches='tight'