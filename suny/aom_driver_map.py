#!/usr/bin/env python3

import sys
import pandas as pd
import os

from matplotlib import rc
import matplotlib.pyplot as plt

from spectrum_analyser.anritsuData import AnritsuData

import numpy as np

## matplotlib settings
rc('text', usetex = True)
rc('text.latex', preamble = r"\usepackage{libertine}\usepackage{nicefrac}")
rc('font', size = 11, family = "Serif")
## END MPL Settings

base_dir = os.path.dirname(os.path.realpath(__file__))
data_file = os.path.join(base_dir, "aom_driver_characterisation", "Data-2022-08-08_100328.dat")

DATA = pd.read_csv(data_file, skiprows = 2, header = 0, sep = "\t")

freqss = DATA.iloc[:, [0,1]]
freqss = freqss.loc[np.around(freqss["Meas Freq/MHz"], decimals = 1) != freqss["# Set Freq/MHz"]]
bad_data = DATA.iloc[freqss.index]
print(bad_data)

sys.exit()

# Convert to Watt
# DATA['RF Output/dBm'] = DATA['RF Output/dBm'].map(AnritsuData.dBmToWatt)
# DATA['RF Input/dBm'] = DATA['RF Input/dBm'].map(AnritsuData.dBmToWatt)

variables = ["RF Input/dBm", "AM Volt/V", "# Set Freq/MHz"]
var_fix_val = [-0.5, 1.25, 80]

fig, axs = plt.subplots(1, 1)

# Fix one variable
for i, fix_var in enumerate(variables):
    fix_DATA = DATA.loc[DATA[fix_var] == var_fix_val[i]]
    fix_DATA = fix_DATA.drop(fix_var, axis=1)

    if "# Set Freq/MHz" in fix_DATA.columns:
        fix_DATA = fix_DATA.drop("# Set Freq/MHz", axis=1)
    else:
        fix_DATA = fix_DATA.drop("Meas Freq/MHz", axis=1)

    print(fix_DATA)
    x = fix_DATA.iloc[:, 0].unique()
    y = fix_DATA.iloc[:, 1].unique()
    z = fix_DATA.iloc[:, 2].to_numpy()
    
    print(x.shape)
    print(y.shape)
    print(z.shape)

    X, Y = np.meshgrid(x, y)

    Z = z.reshape((len(x), len(y))).T
    axs[0, 0].pcolormesh(X, Y, Z, \
        cmap = "inferno_r", \
        vmin = np.min(z), \
        vmax = np.max(z), ) # \ rasterized = True

    break

plt.show()