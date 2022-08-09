#!/usr/bin/env python3

import sys
from anritsuData import AnritsuData
import os, glob

from matplotlib import rc
import matplotlib.pyplot as plt
import lmfit.models

import scipy.signal

import numpy as np

## SETTINGS
nrows = 4; ncols = 1
figwidth = 5.5; figheight = 6

# rolcol(2,2), figsize(8,4)
multiplot = False
offset    = 90 # dBm
## / SETTINGS

## matplotlib settings
rc('text', usetex = True)
rc('text.latex', preamble = r"\usepackage{libertine}")
rc('font', size = 11, family = "Serif")
## END MPL Settings

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

models  = {}
results = {}

for i, key in enumerate(keys):
    khz = getNumFromKey(key)

    freqs = sweeping_freqs[key].DATA["A"]["FREQ"]
    power = sweeping_freqs[key].DATA["A"]["POWER"]

    prefix = f"khz{khz}_"
    
    baseline = lmfit.models.ConstantModel(prefix = prefix)
    rectangular_func = lmfit.models.RectangleModel(prefix = prefix, form = 'erf')

    model = baseline + rectangular_func

    models[key] = model

    minimum = np.min(power)
    maximum = np.max(power)
    middle  = np.average([minimum, maximum])

    center1 = None
    center1_idx = 0
    center2 = None
    center2_idx = 0

    assert len(power) == len(freqs)
    for idx in range(len(power)):
        if center1 is None and power[idx] >= middle:
            # Gets the first element that is >= middle
            center1 = freqs[idx]
            center1_idx = idx
            break
        
    for idx in reversed(range(len(power))):
        if center2 is None and power[idx] >= middle:
            # Gets the first element in the other direction that is >= middle
            center2 = freqs[idx]
            center2_idx = idx
            break

    # SMOOTHING THE DATA
    fit_freqs = freqs
    fit_power = power
    while True:
        peaks, properties = scipy.signal.find_peaks(x = -fit_power[center1_idx:center2_idx], threshold = (maximum - minimum)/50)
        peaks = peaks + center1_idx
        
        fit_freqs = np.delete(fit_freqs, peaks)
        fit_power = np.delete(fit_power, peaks)

        correction = np.count_nonzero(peaks <= center1_idx)
        center1_idx -= correction
        correction = np.count_nonzero(peaks <= center2_idx)
        center2_idx -= correction

        if len(peaks) == 0:
            break

    _params_dict = {
        f"{prefix}c"        : minimum,
        f"{prefix}amplitude": maximum - minimum,
        f"{prefix}center1"  : center1,
        f"{prefix}center2"  : center2,
    }

    _params = model.make_params(**_params_dict)

    _result = model.fit(fit_power, _params, x = fit_freqs)
    results[key] = _result

    # print(_result.fit_report())

    # _freqs_fit = np.linspace(np.min(freqs), np.max(freqs), 1000)
    # plt.scatter(freqs, power, label='data', marker = '+')
    # plt.plot(_freqs_fit, _result.eval(x = _freqs_fit), 'r-', label='interpolated fit')
    # plt.legend()
    # plt.show()
    # # plt.savefig(f'./tv1/peak_{np.around(p, decimals = 5)}.eps', format='eps')
    # plt.clf()

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

