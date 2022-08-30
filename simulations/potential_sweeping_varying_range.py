#!/usr/bin/env python3

import sys
import numpy as np
from sympy import false
from dipoletrapli import DipoleTrapLi, rotate_points, cartesian_product 

from matplotlib.ticker import AutoMinorLocator

from mpl_toolkits.axes_grid1 import make_axes_locatable

try:
    from plotter import Plotter
except ModuleNotFoundError:
    import __init__
    from plotter import Plotter

# https://stackoverflow.com/a/4935945
import matplotlib as mpl
mpl.use('PDF')

import matplotlib.cm as cm

from mpi4py import MPI

comm = MPI.COMM_WORLD
mpisize = comm.Get_size()
mpirank = comm.Get_rank()

# if size != 8:
#     print("Please run with 8 nodes")
#     sys.exit()

## GLOBAL SETTINGS
waist = 25e-6
beam_params = [
    {
        "w_0": [waist, waist], # m
        "z_0": [0   , 0  ], # m
        "Msq": [1.1 , 1.1],
    },
    {
        "w_0": [waist, waist], # m
        "z_0": [0   , 0  ], # m
        "Msq": [1.1 , 1.1],
    }
]

wavelength = 1070e-9  #nm

# BEG SETTINGS
rotation_axis = np.array([0,1,0]) # y-axis
power = 100                       # W
numpoints_x = 700
numpoints_y = 1
numpoints_z = 700
nrows = 2; ncols = 4
figwidth = 8; figheight = 4.8

# in units of waists
# begin = 1; end = nrows * ncols - 1
sweeping_range = [0, 1, 2, 4]

t_samples = 200
def sine_mod(t):
    return np.sin(2*np.pi*t)

def ramp_mod(t):
    return 2*(t - 0.5)

modulation_functions = [ramp_mod, sine_mod]
modulation_function_names = ["Ramp Modulation", "Sinusoidal Modulation"]
# END SETTINGS

angle_between_beams = 10

num_elements = numpoints_x * numpoints_y * numpoints_z

## GLOBAL SETTINGS
x, y, z  = 0, 0, 0

if mpirank == 0:
    plotter = Plotter(nrows = nrows, ncols = ncols, sharex = 'col', sharey = 'row', squeeze = False, figsize=(figwidth, figheight))

    assert isinstance(plotter.axs, np.ndarray)

    # We generate in the x-z plane
    x = np.linspace(start = -150, stop = 150, num = numpoints_x, endpoint = True, dtype = np.float64) * 1e-6 # 5000
    z = np.linspace(start = -0.75, stop = 0.75, num = numpoints_z, endpoint = True, dtype = np.float64) * 1e-3 # 5000
    y = np.array([0], dtype = np.float64)

    points = cartesian_product(x, y, z)

    points_beam1 = rotate_points(points = points, axis = rotation_axis, degrees =  angle_between_beams/2)
    points_beam2 = rotate_points(points = points, axis = rotation_axis, degrees = -angle_between_beams/2)
else:
    points_beam1 = np.empty((num_elements, 3), dtype = np.float64)
    points_beam2 = np.empty((num_elements, 3), dtype = np.float64)

# https://mpi4py.readthedocs.io/en/stable/tutorial.html > Broadcasting np array
comm.Bcast(points_beam1, root = 0)
comm.Bcast(points_beam2, root = 0)

total_elements = len(modulation_functions) * len(sweeping_range)
assert total_elements % mpisize == 0, f"Number of nodes not compatible; Total = {total_elements}, Nodes = {mpisize}"
chunksize = int(total_elements / mpisize)

settings_chunked = []

if mpirank == 0:
    print(f"Chunksize = {chunksize}")

    settings = []

    for mod_func in modulation_functions:
        for rng in sweeping_range:
            settings.append((mod_func, rng))

    # https://www.geeksforgeeks.org/python-reshape-a-list-according-to-given-multi-list/
    settings_iterator = iter(settings)
    settings_chunked = [[next(settings_iterator) for _ in range(chunksize)] for __ in range(mpisize)]

# https://mpi4py.readthedocs.io/en/stable/tutorial.html > Scattering Python Arrays
mychunk = comm.scatter(settings_chunked, root = 0)
print(f"Rank {mpirank}: {mychunk}")

mypotentials = []
for mod_func, rng in mychunk:
    print(f"Rank {mpirank}: Calculating for {mod_func}, {rng}...")

    intensities_1 = DipoleTrapLi.intensity_average(
        x = points_beam1[:,0], y = points_beam1[:,1], z = points_beam1[:,2], 
        power = power, wavelength = wavelength,
        numsamples = t_samples,
        modulation_function = mod_func,
        deviation = rng * waist,
        **beam_params[0]
    )
    intensities_2 = DipoleTrapLi.intensity_average(
        x = points_beam2[:,0], y = points_beam2[:,1], z = points_beam2[:,2], 
        power = power, wavelength = wavelength,
        numsamples = t_samples,
        modulation_function = mod_func,
        deviation = rng * waist,
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
    potentials_for_contour_plotting = potentials_mk.reshape((numpoints_x, numpoints_z)).T
    mypotentials.append(potentials_for_contour_plotting)

    print(f"Rank {mpirank}: Calculating for {mod_func}, {rng}...Done")

print(f"Rank {mpirank}: Calculation Done")

mypotentials  = np.array(mypotentials)
allpotentials = np.empty((mpisize, *np.shape(mypotentials)), dtype = np.float64)

# https://stackoverflow.com/a/36082684
# https://www.kth.se/blogs/pdc/2019/11/parallel-programming-in-python-mpi4py-part-2/
split_counts  = [np.size(mypotentials)] * mpisize
displacements = np.insert(np.cumsum(split_counts),0,0)[0:-1]
comm.Barrier()

comm.Gatherv(sendbuf = mypotentials, recvbuf = [allpotentials, split_counts, displacements, MPI.DOUBLE], root = 0)

if mpirank == 0:
    minimum_potential = np.amin(allpotentials) # auto-flattens
    maximum_potential = np.amax(allpotentials)

    # https://stackoverflow.com/a/26553855
    # Flatten the outermost dimension
    allpotentials = np.reshape(allpotentials, newshape = (-1, *allpotentials.shape[2:]))
    colourmeshes = []

    # PLOTTING
    X, Z = np.meshgrid(x * 1e6, z * 1e3)
    for i in range(nrows):
        for j in range(ncols):
            p = plotter.axs[i, j].pcolormesh(X, Z, allpotentials[i * ncols + j], \
                cmap = plotter.COLORMAP_R, \
                vmin = minimum_potential, \
                vmax = maximum_potential, \
                rasterized = True)

            colourmeshes.append(p)

            # if j > 1:
            #     # For the right 4 plots, we do a re-plot to show more levels

            #     _axins = plotter.axs[i, j].inset_axes([0.5, 0.15, 0.5, 0.75]) # [x0, y0, width, height]
            #     _c = _axins.contour(X, Z, allpotentials[i * ncols + j], cmap = plotter.COLORMAP_R, rasterized = True)
            #     _axins.tick_params(axis = 'both', which = 'both', direction = 'out')
            #     _axins.tick_params(axis = 'both', which = 'minor', colors = plotter.MINORTICK_COLOR)
            #     _axins.xaxis.set_minor_locator(AutoMinorLocator())
            #     _axins.yaxis.set_minor_locator(AutoMinorLocator())
            #     plotter.axs[i, j].indicate_inset_zoom(_axins, edgecolor="#222222")

            #     # Add colourbar
            #     divider = make_axes_locatable(_axins)
            #     cax = divider.append_axes('right', size='5%', pad=0.05)
            #     cb = plotter.fig.colorbar(_c, cax=cax, orientation='vertical')

            if i == 0:
                plotter.axs[i, j].set_title(f"$A = {sweeping_range[j]}w_0$")
            if j == 0:
                plotter.axs[i, j].set_ylabel(f"{modulation_function_names[i]}")

    # cb = plotter.fig.colorbar(cm.ScalarMappable(norm = None, cmap = plotter.COLORMAP_R), ax = plotter.axs)
    cb = plotter.fig.colorbar(colourmeshes[0], ax = plotter.axs)

    # plotter.fig.subplots_adjust(right=0.6)

    # SET LABELS
    cb.ax.set_ylabel('Trap Depth (mK $\\cdot k_{\\!B}$)', rotation=90, labelpad = 15)
    plotter.fig.suptitle(f'${power}$ W Sweeping Beam Trap Depth ($10^\\circ$ Separation) at varying amplitude $A$')
    try:
        plotter.fig.supxlabel('$x$ ($\\mu$m)')
        plotter.fig.supylabel('Propagation direction $z$ (mm)')
    except AttributeError as e:
        # https://stackoverflow.com/a/50610853
        # axs[-1, 0].set_xlabel('.', color=(0, 0, 0, 0))
        # axs[-1, 0].set_ylabel('.', color=(0, 0, 0, 0))
        plotter.fig.text(0.43, 0.04, '$x$ ($\\mu$m)', va='center', ha='center', fontsize='large')
        plotter.fig.text(0.025, 0.5, 'Propagation direction $z$ (mm)', va='center', ha='center', rotation='vertical', fontsize='large')
    # END SET LABELS

    # plt.tight_layout()
    # plt.show()
    # plt.savefig("./sweeping_potential_2D.eps", format = 'eps') # bbox_inches='tight'
    plotter.savefig("./sweeping_potential_2D.pdf", format = 'pdf', dpi = 600)