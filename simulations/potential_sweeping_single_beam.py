#!/usr/bin/env python3

# Calculates the potential based on a sweeping dipole trap
import sys, os
import numpy as np
from dipoletrapli import DipoleTrapLi, cartesian_product 

from mpl_toolkits.axes_grid1 import make_axes_locatable

import __init__
from plotter import Plotter

from matplotlib.ticker import LinearLocator

beam_params = {
    "w_0": [25e-6  , 25e-6 ], # m
    "z_0": [0   , 0  ], # m
    "Msq": [1 , 1],
    "deviation": 100e-6 # m
}

wavelength = 1070e-9  #nm
# We generate in the x-z plane

# BEG SETTINGS
power = 100                       # W
PLOT3D = False
numsamples = 200
x_numsamples = 700
z_numsamples = 700

def sine_mod(t):
    return np.sin(2*np.pi*t)

def ramp_mod(t):
    return 2*(t - 0.5)

mod_funcs = [ramp_mod, sine_mod]
mod_func_names = ["Ramp Modulation", "Sinusoidal Modulation"]
filenames = ["sweeping_potential_single_beam_ramp.pdf", "sweeping_potential_single_beam_sine.pdf"]

# END SETTINGS
x = np.linspace(start = -200, stop = 200, num = x_numsamples, endpoint = True) * 1e-6
z = np.linspace(start = -8, stop = 8, num = z_numsamples, endpoint = True) * 1e-3
y = np.array([0])

points = cartesian_product(x, y, z)

for i in range(len(mod_funcs)):
    modulation_function = mod_funcs[i]
    modulation_function_name = mod_func_names[i]
    filename = filenames[i]

    intensities = DipoleTrapLi.intensity_average(
        x = points[:,0], y = points[:,1], z = points[:,2], 
        power = power, wavelength = wavelength,
        numsamples = numsamples,
        modulation_function = modulation_function,
        **beam_params
    )

    potential = DipoleTrapLi.potential(intensity = intensities, wavelength = wavelength)*1e27 # Turn into reasonable units

    assert isinstance(potential, np.ndarray)

    potentials_mk = DipoleTrapLi.trap_temperature(trap_depth = potential*1e-27)*1e3

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
        plotter.axs.zaxis.set_major_formatter('${x:.02f}$')

        # DO LABELS
        plotter.fig.suptitle(f'Sweeping Beam Trap Depth (Power ${power}$ W)\n{modulation_function_name}', y = 0.95)
        plotter.axs.set_xlabel('$x$ ($\\mu$m)')
        plotter.axs.set_ylabel('Propagation direction $z$ (mm)')
        plotter.axs.set_zlabel('Trap Depth (mK $\\cdot k_B$)', linespacing=5)
        plotter.axs.invert_zaxis()
        # END DO LABELS

        # Add a color bar which maps values to colors.
        plotter.fig.colorbar(surf, shrink=0.5, aspect=5, orientation="vertical", pad=0.2)

        # plt.tight_layout()
        plotter.fig.set_size_inches(7, 4.8)

        plotter.savefig(os.path.join(__init__.base_dir, "generated", filename), backend = "pdf", dpi = 600)
    else:
        # Plot 2D colour map
        # http://www.peterbeerli.com/classes/images/2/26/Isc4304matplotlib6.pdf

        lenz, lenx = potentials_for_contour_plotting.shape
        schnitt_x = potentials_for_contour_plotting[lenz // 2, :]

        plotter = Plotter(nrows = 1, ncols = 2, gridspec_kw={'width_ratios': [1, 4]}, sharey = 'row', squeeze = False)
        p = plotter.axs[0,1].pcolormesh(Z, X, potentials_for_contour_plotting, cmap=plotter.COLORMAP_R, vmin=potentials_for_contour_plotting.min(), vmax=potentials_for_contour_plotting.max(), rasterized = True)

        # https://stackoverflow.com/a/49037495
        divider = make_axes_locatable(plotter.axs[0,1])
        cax = divider.append_axes('right', size='5%', pad=0.05)
        plotter.fig.colorbar(p, cax = cax, orientation='vertical')

        plotter.axs[0,0].plot(schnitt_x, x * 1e6)
        plotter.axs[0,0].set_title("Cross section\nat $z = 0$")
        plotter.axs[0,0].set_ylabel('Modulation Direction $x$ ($\\mu$m)')
        plotter.axs[0,0].set_xlabel('Potential Depth\n(mK $\\cdot k_B$)')

        plotter.axs[0,1].set_title("Dipole Potential Depth")
        plotter.axs[0,1].set_xlabel('Propagation Direction $z$ (mm)')

        plotter.fig.suptitle(f"Sweeping Beam Trap Depth ($P = \\SI{{100}}{{\\watt}}$, $w_0 = \\SI{{25}}{{\\micro\\meter}}$, $A = 4w_0$)\n{modulation_function_name}")

        plotter.fig.set_size_inches(7, 3)
        plotter.fig.tight_layout()

        plotter.fig.subplots_adjust(top= 0.72, right = 0.91)

        plotter.fig.text(0.98, 0.48,'Trap Depth (mK $\\cdot k_B$)', rotation = "vertical", va = "center", ha = "center")

        # plotter.show()
        plotter.savefig(os.path.join(__init__.base_dir, "generated", filename), backend = "pdf", dpi = 600)

    min_point = np.argmin(potential)
    print("Min Potential at =", points[min_point] * 1e6, "um")
    print("Trap Depth =", DipoleTrapLi.trap_temperature(trap_depth = potential[min_point]*1e-27)*1e3, "mK")