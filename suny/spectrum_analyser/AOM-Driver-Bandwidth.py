#!/usr/bin/env python3

from anritsuData import AnritsuData
import os, glob

from matplotlib import rc
import matplotlib.pyplot as plt
import matplotlib.markers

## SETTINGS
nrows = 4; ncols = 1
figwidth = 5.5; figheight = 6

# rolcol(2,2), figsize(8,4)
multiplot = False
offset    = 90 # dBm
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



## matplotlib settings
rc('text', usetex = True)
rc('text.latex', preamble = r"\usepackage{libertine}")
rc('font', size = 11, family = "Serif")
## END MPL Settings

# PLOTTING BANDWIDTH
keys_for_plotting = ['1kHz', '50kHz', '100kHz-30kHzBW', '400kHz-100kHzBW']
if multiplot:
    fig, axs = plt.subplots(nrows = nrows, ncols = ncols, sharex = 'col', sharey = 'row', squeeze = False, figsize=(figwidth, figheight))

    for i, key in enumerate(keys_for_plotting):
        data = sweeping_freqs[key]
        ax = axs[i // ncols, i % ncols]
        ax.scatter(data.DATA["A"]["FREQ"], data.DATA["A"]["POWER"], marker = "+", label = key)
        ax.set_title(key)
        ax.set_xlim([70,89])

    fig.supxlabel("Frequency (MHz)")
    fig.supylabel("Power after attenuation (dBm)")
else:
    fig, ax = plt.subplots(figsize = (figwidth, figheight))
    l = len(keys)
    for i, key in enumerate(keys_for_plotting):
        j = l - i
        data = sweeping_freqs[key]

        # PLOT THE DATA
        ax.scatter(data.DATA["A"]["FREQ"], data.DATA["A"]["POWER"] + j*offset, marker = "+", label = f"{getNumFromKey(key)} kHz Modulation")

    ax.set_xlabel("Frequency (MHz)")
    ax.set_ylabel("Power after attenuation (dBm)")
    fig.suptitle("\\shortstack{Output RF Bandwidth from POS-150+ AOM Driver\\\\at different modulation frequencies}")

    ax.legend(loc='lower center', bbox_to_anchor = (0.5, -0.3), ncol=2, fancybox=True)
    fig.subplots_adjust(bottom=0.25) # https://www.adamsmith.haus/python/answers/how-to-place-a-legend-below-the-axes-in-matplotlib-in-python
    plt.xlim([70,89])

plt.show()

