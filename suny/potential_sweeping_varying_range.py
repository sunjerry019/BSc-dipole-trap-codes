#!/usr/bin/env python3

import numpy as np
from sympy import false
from dipoletrapli import DipoleTrapLi, rotate_points, cartesian_product 

from matplotlib import rc
import matplotlib.pyplot as plt
import matplotlib.cm as cm


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
numpoints_z = 700
nrows = 2; ncols = 2
figwidth = 8; figheight = 4.8

# in units of waists
# begin = 1; end = nrows * ncols - 1
sweeping_range = [0, 1, 2, 4]
assert len(sweeping_range) == (nrows * ncols)

t_samples = 100
def sine_mod(t):
    return np.sin(2*np.pi*t)

def ramp_mod(t):
    return t - 0.5

modulation_function = sine_mod
modulation_function_name = "Sinusoidal Modulation"

# modulation_function = ramp_mod
# modulation_function_name = "Ramp Modulation"
# END SETTINGS

## matplotlib settings
rc('text', usetex = True)
rc('text.latex', preamble = r"\usepackage{libertine}")
rc('font', size = 11, family = "Serif")
## END MPL Settings

angle_between_beams = 10

# We generate in the x-z plane
x = np.linspace(start = -150, stop = 150, num = numpoints_x, endpoint = True) * 1e-6 # 5000
z = np.linspace(start = -0.75, stop = 0.75, num = numpoints_z, endpoint = True) * 1e-3 # 5000
y = np.array([0])

points = cartesian_product(x, y, z)

X, Z = np.meshgrid(x * 1e6, z * 1e3)

fig, axs = plt.subplots(nrows = nrows, ncols = ncols, sharex = 'col', sharey = 'row', squeeze = False, figsize=(figwidth, figheight))
assert isinstance(axs, np.ndarray)

allpotentials = []

for rng in sweeping_range:
    print(f"Calculating for sweeping range = {rng} waists...")
    points_beam1 = rotate_points(points = points, axis = rotation_axis, degrees =  angle_between_beams/2)
    points_beam2 = rotate_points(points = points, axis = rotation_axis, degrees = -angle_between_beams/2)

    intensities_1 = DipoleTrapLi.intensity_average(
        x = points_beam1[:,0], y = points_beam1[:,1], z = points_beam1[:,2], 
        power = power, wavelength = wavelength,
        numsamples = t_samples,
        modulation_function = modulation_function,
        deviation = rng * waist,
        **beam_params[0]
    )
    intensities_2 = DipoleTrapLi.intensity_average(
        x = points_beam2[:,0], y = points_beam2[:,1], z = points_beam2[:,2], 
        power = power, wavelength = wavelength,
        numsamples = t_samples,
        modulation_function = modulation_function,
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
    potentials_for_contour_plotting = potentials_mk.reshape((len(x), len(z))).T
    allpotentials.append(potentials_for_contour_plotting)
    print(f"Calculating for sweeping range = {rng} waists...Done")

allpotentials_np  = np.array(allpotentials)
minimum_potential = np.min(allpotentials_np)
maximum_potential = np.max(allpotentials_np)

for i in range(nrows):
    for j in range(ncols):
        print(f"Making colormesh for range = {sweeping_range[i * nrows + j]} waist...", end = '\r')
        p = axs[i, j].pcolormesh(X, Z, allpotentials[i * nrows + j], \
            cmap = "inferno_r", \
            vmin = minimum_potential, \
            vmax = maximum_potential, \
            rasterized = True)
        axs[i, j].set_title(f"$\\sigma = {sweeping_range[i * nrows + j]}\\omega_0$")
        print(f"Making colormesh for range = {sweeping_range[i * nrows + j]} waist...Done")

cb = fig.colorbar(cm.ScalarMappable(norm = None, cmap = "inferno_r"), ax = axs)

# SET LABELS
cb.ax.set_ylabel('Trap Depth (mK $\\cdot k_{\\!B}$)', rotation=90, labelpad = 15)
fig.suptitle(f'${power}$ W Sweeping Beam Trap Depth ({modulation_function_name}, $10^\\circ$ Separation) at varying range $\\sigma$')
fig.supxlabel('$x$ ($\\mu$m)')
fig.supylabel('Propagation direction $z$ (mm)')
# END SET LABELS

# plt.tight_layout()
plt.show()
# plt.savefig("./generated/potential_static_varying_angles.eps", format = 'eps') # bbox_inches='tight'