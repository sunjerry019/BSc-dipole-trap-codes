#!/usr/bin/env python3

# Calculates the potential based on a sweeping dipole trap

from importlib.metadata import files
import numpy as np
from dipoletrapli import DipoleTrapLi, rotate_points, cartesian_product 

import __init__
from plotter import Plotter

from matplotlib.ticker import LinearLocator

beam_params = [
    {
        "w_0": [25e-6  , 25e-6 ], # m
        "z_0": [0   , 0  ], # m
        "Msq": [1.1 , 1.1],
        "deviation": 75e-6 # m
    },
    {
        "w_0": [25e-6  , 25e-6 ], # m
        "z_0": [0   , 0  ], # m
        "Msq": [1.1 , 1.1],
        "deviation": 75e-6 # m
    }
]

wavelength = 1070e-9  #nm
# We generate in the x-z plane

# BEG SETTINGS
rotation_axis = np.array([0,1,0]) # y-axis
angle_between_beams = 10          # degrees
power = 100                       # W
PLOT3D = True
numsamples = 200
x_numsamples = 1000
z_numsamples = 1000

def sine_mod(t):
    return np.sin(2*np.pi*t)

def ramp_mod(t):
    return 2*(t - 0.5)

# modulation_function = sine_mod
# modulation_function_name = "Simple Sinusoidal Modulation"

# modulation_function = ramp_mod
# modulation_function_name = "Simple Ramp Modulation"

mod_funcs = [ramp_mod, sine_mod]
mod_func_names = ["Simple Sinusoidal Modulation", "Simple Ramp Modulation"]
filenames = ["sweeping_potential_3D_ramp.pdf", "sweeping_potential_3D_sine.pdf"]

# END SETTINGS
x = np.linspace(start = -200, stop = 200, num = x_numsamples, endpoint = True) * 1e-6
z = np.linspace(start = -1.7, stop = 1.7, num = z_numsamples, endpoint = True) * 1e-3
y = np.array([0])

points = cartesian_product(x, y, z)

points_beam1 = rotate_points(points = points, axis = rotation_axis, degrees =  angle_between_beams/2)
points_beam2 = rotate_points(points = points, axis = rotation_axis, degrees = -angle_between_beams/2)

for i in range(len(mod_funcs)):
    modulation_function = mod_funcs[i]
    modulation_function_name = mod_func_names[i]
    filename = filenames[i]

    intensities_1 = DipoleTrapLi.intensity_average(
        x = points_beam1[:,0], y = points_beam1[:,1], z = points_beam1[:,2], 
        power = power, wavelength = wavelength,
        numsamples = numsamples,
        modulation_function = modulation_function,
        **beam_params[0]
    )
    intensities_2 = DipoleTrapLi.intensity_average(
        x = points_beam2[:,0], y = points_beam2[:,1], z = points_beam2[:,2], 
        power = power, wavelength = wavelength,
        numsamples = numsamples,
        modulation_function = modulation_function,
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
    X, Z = np.meshgrid(x * 1e6, z * 1e3)

    # fig, ax = plt.subplots()
    # cs      = ax.contour(x, z, potentials_for_contour_plotting, levels = 15)
    # # ax.clabel(cs, inline=True, fontsize=10)
    # ax.set_title('Simplest default with labels')

    if PLOT3D:
        plotter = Plotter(subplot_kw={"projection": "3d"})
        
        # Plot the surface.
        surf = plotter.axs.plot_surface(X = X, Y = Z, Z = potentials_for_contour_plotting, cmap=plotter.COLORMAP_R,
                            linewidth=0, antialiased=True, rasterized = True)

        plotter.axs.view_init(azim = 121, elev = 50)

        # Customize the z axis.
        # ax.set_zlim(-1.01, 1.01)
        plotter.axs.zaxis.set_major_locator(LinearLocator(10))
        # A StrMethodFormatter is used automatically
        plotter.axs.zaxis.set_major_formatter('{x:.02f}')

        # DO LABELS
        plotter.fig.suptitle(f'Sweeping Beam Trap Depth (Beam Separation ${angle_between_beams}^\\circ$, Power ${power}$ W)\n{modulation_function_name}', y = 0.95)
        plotter.axs.set_xlabel('$x$ ($\\mu$m)')
        plotter.axs.set_ylabel('Propagation direction $z$ (mm)')
        plotter.axs.set_zlabel('Trap Depth (mK $\\cdot k_B$)', linespacing=5)
        plotter.axs.invert_zaxis()
        # END DO LABELS

        # Add a color bar which maps values to colors.
        plotter.fig.colorbar(surf, shrink=0.5, aspect=5, orientation="vertical", pad=0.2)

        # plt.tight_layout()
        plotter.fig.set_size_inches(7, 4.8)

        import os
        base_dir = os.path.dirname(os.path.abspath(__file__))
        plotter.savefig(os.path.join(base_dir, "generated", filename), backend = "pdf", dpi = 600)
    else:
        # Plot 2D colour map
        # http://www.peterbeerli.com/classes/images/2/26/Isc4304matplotlib6.pdf

        plotter = Plotter()
        p = plotter.axs.pcolormesh(X, Z, potentials_for_contour_plotting, cmap=plotter.COLORMAP_R, vmin=potentials_for_contour_plotting.min(), vmax=potentials_for_contour_plotting.max())
        cb = plotter.fig.colorbar(p, ax = plotter.axs)

        plotter.show()

    min_point = np.argmin(potentials)
    print("Min Potential at =", points[min_point] * 1e6, "um")
    print("Trap Depth =", DipoleTrapLi.trap_temperature(trap_depth = potentials[min_point]*1e-27)*1e3, "mK")