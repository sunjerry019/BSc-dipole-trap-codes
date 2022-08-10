#!/usr/bin/env python3

import sys
from anritsuData import AnritsuData
import os, glob

from matplotlib import rc
import matplotlib.pyplot as plt
import lmfit.models

import scipy.signal
import scipy.optimize

import numpy as np
import uncertainties

## SETTINGS
nrows = 4; ncols = 1
figwidth = 5.5; figheight = 6.5
bw_figwidth = 6; bw_figheight = 5

SKIP_4_BW_PLOT = True

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
BW_lefts   = {}
BW_rights  = {}
bandwidths = {}

for i, key in enumerate(keys):
    khz = getNumFromKey(key)
    print(khz, "Khz =============")

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


    _amplitude = uncertainties.ufloat(_result.params[f"{prefix}amplitude"].value, _result.params[f"{prefix}amplitude"].stderr)
    _constant  = uncertainties.ufloat(_result.params[f"{prefix}c"].value, _result.params[f"{prefix}c"].stderr)

    minus3db = _amplitude - 3 + _constant
    print("-3dB point:", minus3db, "dBm")

    def eval_func(x: np.ndarray | float) -> np.ndarray | float:
        return _result.eval(x = x) - minus3db.nominal_value

    def eval_func_top(x: np.ndarray | float) -> np.ndarray | float:
        del_y = _result.eval_uncertainty(x = x)
        return _result.eval(x = x) + del_y - minus3db.nominal_value +  + minus3db.std_dev
    def eval_func_bottom(x: np.ndarray | float) -> np.ndarray | float:
        del_y = _result.eval_uncertainty(x = x)
        return _result.eval(x = x) - del_y - minus3db.nominal_value - minus3db.std_dev

    # SOME ROOTFINDING ALGOS here
    _left_res  = scipy.optimize.root(fun = eval_func, x0 = center1)
    _left_res_top  = scipy.optimize.root(fun = eval_func_top, x0 = _left_res.x)
    _left_res_bottom  = scipy.optimize.root(fun = eval_func_bottom, x0 = _left_res.x)

    _right_res = scipy.optimize.root(fun = eval_func, x0 = center2)
    _right_res_top = scipy.optimize.root(fun = eval_func_top, x0 = _right_res.x)
    _right_res_bottom = scipy.optimize.root(fun = eval_func_bottom, x0 = _right_res.x)

    _left_res_dev = np.average(np.abs(np.array([_left_res_top.x, _left_res_bottom.x]) - _left_res.x))
    _right_res_dev = np.average(np.abs(np.array([_right_res_top.x, _right_res_bottom.x]) - _right_res.x))

    _left = uncertainties.ufloat(_left_res.x, _left_res_dev)
    _right = uncertainties.ufloat(_right_res.x, _right_res_dev)

    bandwidth = np.abs(_right - _left)
    
    BW_lefts[key] = _left
    BW_rights[key] = _right
    bandwidths[key] = bandwidth

    print("bandwidth", bandwidth, "MHz\n")

    # bandwidth_plot_x = np.array([_left.nominal_value, _right.nominal_value])
    # bandwidth_plot_x_err = np.array([_left.std_dev, _right.std_dev])
    # bandwidth_plot_y = _result.eval(x = bandwidth_plot_x)

    # _freqs_fit = np.linspace(np.min(freqs), np.max(freqs), 1000)
    # plt.scatter(freqs, power, label='data', marker = '+')
    # plt.errorbar(x = bandwidth_plot_x, y = bandwidth_plot_y, xerr = bandwidth_plot_x_err, label = "Bandwidth", uplims=True, lolims=True, ecolor = "red", color = "green", capsize = 10)
    # plt.plot(_freqs_fit, _result.eval(x = _freqs_fit), 'r-', label='interpolated fit')
    # plt.legend()
    # plt.show()
    # # plt.savefig(f'./tv1/peak_{np.around(p, decimals = 5)}.eps', format='eps')
    # plt.clf()

# PLOTTING BANDWIDTH
if not SKIP_4_BW_PLOT:
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
        l = len(keys_for_plotting)

        fit_x = np.linspace(start = 70, stop = 90, num = 1000, endpoint = True)
        colors = ['darkturquoise', 'burlywood', 'mediumseagreen', 'lightcoral']

        for i, key in enumerate(keys_for_plotting):
            j = l - i
            data = sweeping_freqs[key]

            _LR = [BW_lefts[key], BW_rights[key]]
            bandwidth_plot_x     = np.array([x.nominal_value for x in _LR])
            bandwidth_plot_x_err = np.array([x.std_dev for x in _LR])
            bandwidth_plot_y     = results[key].eval(x = bandwidth_plot_x) + j*offset

            fit_y = results[key].eval(x = fit_x) + j*offset
            fit_y_delta = results[key].eval_uncertainty(x = fit_x)

            # PLOT THE DATA
            ax.scatter(data.DATA["A"]["FREQ"], data.DATA["A"]["POWER"] + j*offset, marker = ".", label = f"{getNumFromKey(key)} kHz Modulation", color = colors[i], s = 6)
            ax.fill_between(fit_x, fit_y - fit_y_delta, fit_y + fit_y_delta, color='#888888')
            if i == 1:
                ax.plot(fit_x, fit_y, color = "tab:red", label = "erf-Rectangle Fit")
                ax.errorbar(x = bandwidth_plot_x, y = bandwidth_plot_y, xerr = bandwidth_plot_x_err, capsize = 5, ecolor = "black", color = "black", marker = "x", label = "3 dB Bandwidth")
            else:
                ax.plot(fit_x, fit_y, color = "tab:red")
                ax.errorbar(x = bandwidth_plot_x, y = bandwidth_plot_y, xerr = bandwidth_plot_x_err, capsize = 5, ecolor = "black", color = "black", marker = "x")

        ax.set_xlabel("Frequency (MHz)")
        ax.set_ylabel("Power after attenuation (dBm)")
        fig.suptitle("\\shortstack{Output RF Bandwidth from POS-150+ AOM Driver\\\\at different modulation frequencies}")

        ax.legend(loc='lower center', bbox_to_anchor = (0.5, -0.35), ncol=2, fancybox=True)
        fig.subplots_adjust(bottom=0.25) # https://www.adamsmith.haus/python/answers/how-to-place-a-legend-below-the-axes-in-matplotlib-in-python
        plt.xlim([70,89])

    plt.show()
    plt.clf()

# PLOTTING THE BANDWIDTH vs FREQ
BW_freqs = np.array([getNumFromKey(k) for k in keys]) # in kHz
BW_bandwidths = np.array([bandwidths[k].nominal_value for k in keys]) # in MHz
BW_bandwidths_err = np.array([bandwidths[k].std_dev for k in keys]) # in MHz


