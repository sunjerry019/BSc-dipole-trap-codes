#!/usr/bin/env python3

from anritsuData import AnritsuData
import os, glob

from matplotlib import rc
import matplotlib.pyplot as plt
import matplotlib.markers

## SETTINGS
nrows = 2; ncols = 2
figwidth = 8; figheight = 4 
multiplot = False
## / SETTINGS

base_dir = os.path.dirname(os.path.realpath(__file__))

## READ IN THE DATA
sweeping_freqs = {}

for name in glob.glob(os.path.join(base_dir, "data", "*.csv")):
    description = name.split(os.path.sep)[-1][15:].split(".")[0]

    # store into dictionary with descrption as key
    sweeping_freqs[description] = AnritsuData(datafile = name)

def getNumFromKey(key: str) -> int | float:
    key = key.split("-")[0][:-3]
    v = AnritsuData.coerce_number(key)
    
    return v if isinstance(v, int | float) else 999

## sort the keys
keys = list(sweeping_freqs.keys())
keys.sort(key = getNumFromKey)
print(keys)

# PLOT THE DATA HERE
## Access the dictionary in the order of the sorted keys

## matplotlib settings
rc('text', usetex = True)
rc('text.latex', preamble = r"\usepackage{libertine}")
rc('font', size = 11, family = "Serif")
## END MPL Settings


if multiplot:
    fig, axs = plt.subplots(nrows = nrows, ncols = ncols, sharex = 'col', sharey = 'row', squeeze = False, figsize=(figwidth, figheight))

    for i, key in enumerate(keys):
        data = sweeping_freqs[key]
        ax = axs[i // nrows, i % nrows]
        ax.scatter(data.DATA["A"]["FREQ"], data.DATA["A"]["POWER"], marker = "+", label = key)
        ax.set_title(key)
        ax.set_xlim([70,89])

    fig.supxlabel("Frequency (MHz)")
    fig.supylabel("Power after attenuation (dBm)")
else:
    fig, ax = plt.subplots(figsize = (figwidth, figheight))
    for key in keys:
        data = sweeping_freqs[key]
        ax.scatter(data.DATA["A"]["FREQ"], data.DATA["A"]["POWER"], marker = "+", label = key)
    ax.legend()
    ax.set_xlabel("Frequency (MHz)")
    ax.set_ylabel("Power after attenuation (dBm)")
    plt.xlim([70,89])

plt.show()

