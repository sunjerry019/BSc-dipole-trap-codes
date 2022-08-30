#!/usr/bin/env python3

import __init__
import os, sys

import pandas as pd
import numpy as np

from plotter import Plotter

plot3D = False

datafile = os.path.join(__init__.base_dir, "Data-2022-08-08_100328.dat")

DATA = pd.read_csv(datafile, skiprows = 2, header = 0, sep = "\t")

# Replace invalid data
DATA.loc[np.invert(np.isclose(DATA["Meas Freq/MHz"], DATA["# Set Freq/MHz"], atol = 0.1)), "RF Output/dBm"] = None
# Drop the measured frequency and use the set frequency instead
DATA.drop(columns = ["Meas Freq/MHz"], inplace = True)

freqs    = DATA["# Set Freq/MHz"].unique()
rfintput = DATA["RF Input/dBm"].unique()
amvolt   = DATA["AM Volt/V"].unique()

print("Freqs:", freqs)
print("RF Inputs:", rfintput)
print("AM Volts:", amvolt)

index_x = 0 
index_y = 1 
index_z = 2 
index_c = 3
figsize = (4, 3)
p = [ '# Set Freq/MHz', 'RF Input/dBm', 'AM Volt/V']
lv = [ 'RF Output/dBm' ]  # colour to plot
name_color_map = Plotter.COLORMAP

descriptive_map = {
    '# Set Freq/MHz' : "Set Frequency (MHz)", 
    "RF Input/dBm"   : "RF Input Power (dBm)", 
    "AM Volt/V"      : "AM Voltage (V)",
    'RF Output/dBm'  : "RF Output Power (dBm)"
}

def permuteLast(l: list):
    return [ [y for y in l if y != x] + [x] for x in l ]

if plot3D:
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt
    import matplotlib.tri as mtri

for n, permutation in enumerate(permuteLast(p)):
    perm = list(permutation)
    varnames = perm + lv

    if not plot3D:
        # Take average of the z dimension
        # https://stackoverflow.com/a/52957855
        
        ignoreCol = DATA.drop(columns = [varnames[index_z]])
        grped     = ignoreCol.groupby([varnames[index_x], varnames[index_y]]).mean().reset_index()
        # reset_index flattens it

        x = grped[varnames[index_x]].unique()
        y = grped[varnames[index_y]].unique()
        
        X, Y = np.meshgrid(x, y)
        C    = grped[varnames[index_c]].to_numpy().reshape((len(x), len(y))).T

        plotter = Plotter(figsize = figsize)
        p1 = plotter.ax.pcolormesh(X, Y, C, cmap=plotter.COLORMAP, vmin=C.min(), vmax=C.max(), rasterized = True)
        # plotter.ax.contour(Z, X, potentials_for_contour_plotting, colours = 'white', vmin=potentials_for_contour_plotting.min(), vmax=potentials_for_contour_plotting.max(), linestyles = "dashed")
        cb = plotter.fig.colorbar(p1, ax = plotter.axs)

        # plotter.ax.set_title(f'')
        plotter.ax.set_xlabel(descriptive_map[varnames[index_x]])
        plotter.ax.set_ylabel(descriptive_map[varnames[index_y]])
        plotter.fig.tight_layout()
        plotter.fig.subplots_adjust(right=0.9)
        plotter.fig.text(0.92, 0.52, descriptive_map[varnames[index_c]], rotation = "vertical", va = "center", ha = "center")
        # plotter.show()
        plotter.savefig(os.path.join(__init__.base_dir, "generated", f"aom-map-{n}.pdf"), backend = "PDF")

    else:
        # https://stackoverflow.com/a/57638860

        # The values ​​related to each point. This can be a "Dataframe pandas" 
        # for example where each column is linked to a variable <-> 1 dimension. 
        # The idea is that each line = 1 pt in 4D.

        # We create triangles that join 3 pt at a time and where their colors will be
        # determined by the values ​​of their 4th dimension. Each triangle contains 3
        # indexes corresponding to the line number of the points to be grouped. 
        # Therefore, different methods can be used to define the value that 
        # will represent the 3 grouped points and I put some examples.
        x = DATA[varnames[index_x]] 
        y = DATA[varnames[index_y]] 
        z = DATA[varnames[index_z]] 
        c = DATA[varnames[index_c]]

        triangles = mtri.Triangulation(x, y).triangles

        choice_calcuation_colors = 1
        if choice_calcuation_colors == 1: # Mean of the "c" values of the 3 pt of the triangle
            colors = np.mean( [c[triangles[:,0]], c[triangles[:,1]], c[triangles[:,2]]], axis = 0)
        elif choice_calcuation_colors == 2: # Mediane of the "c" values of the 3 pt of the triangle
            colors = np.median( [c[triangles[:,0]], c[triangles[:,1]], c[triangles[:,2]]], axis = 0)
        elif choice_calcuation_colors == 3: # Max of the "c" values of the 3 pt of the triangle
            colors = np.max( [c[triangles[:,0]], c[triangles[:,1]], c[triangles[:,2]]], axis = 0)
        #end
        #----------
        # Displays the 4D graphic.
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        triang = mtri.Triangulation(x, y, triangles)
        surf = ax.plot_trisurf(triang, z, cmap = name_color_map, shade=False, linewidth=0.2)
        surf.set_array(colors) 
        surf.autoscale()

        #Add a color bar with a title to explain which variable is represented by the color.
        cbar = fig.colorbar(surf, shrink=0.5, aspect=5)
        cbar.ax.get_yaxis().labelpad = 15 
        cbar.ax.set_ylabel(varnames[index_c], rotation = 270)

        # Add titles to the axes and a title in the figure.
        ax.set_xlabel(varnames[index_x]) 
        ax.set_ylabel(varnames[index_y])
        ax.set_zlabel(varnames[index_z])
        plt.title('%s in function of %s, %s and %s' % (varnames[index_c], varnames[index_x], varnames[index_y], varnames[index_z]) )

        plt.show()
        plt.clf()