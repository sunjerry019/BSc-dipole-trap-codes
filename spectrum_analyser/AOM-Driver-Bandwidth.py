#!/usr/bin/env python3

from anritsuData import AnritsuData
import os, glob

import __init__
from plotter import Plotter

import lmfit.models

import scipy.signal
import scipy.optimize

import numpy as np
import uncertainties

## SETTINGS
nrows = 4; ncols = 1
figwidth = 5.5; figheight = 6.5
BW_figwidth = 7; BW_figheight = 4

SKIP_4_BW_PLOT = False

# rolcol(2,2), figsize(8,4)
multiplot = False
offset    = 90 # dBm
## / SETTINGS

base_dir = os.path.dirname(os.path.realpath(__file__))

## READ IN THE DATA
sweeping_freqs = {}

for name in glob.glob(os.path.join(base_dir, "2022-08-02_data", "*.csv")):
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
        return _result.eval(x = x) + del_y - minus3db.nominal_value + minus3db.std_dev
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
        plotter = Plotter(nrows = nrows, ncols = ncols, sharex = 'col', sharey = 'row', squeeze = False, figsize=(figwidth, figheight))

        for i, key in enumerate(keys_for_plotting):
            data = sweeping_freqs[key]
            ax = plotter.axs[i // ncols, i % ncols]

            ax.scatter(data.DATA["A"]["FREQ"], data.DATA["A"]["POWER"], marker = "+", label = key)
            ax.set_title(key)
            ax.set_xlim([70,89])

        plotter.fig.supxlabel("Frequency (MHz)")
        plotter.fig.supylabel("Power after attenuation (dBm)")
    else:
        plotter = Plotter(figsize = (figwidth, figheight))
        l = len(keys_for_plotting)

        fit_x = np.linspace(start = 70, stop = 90, num = 1000, endpoint = True)
        colors = ['darkturquoise', 'burlywood', 'mediumseagreen', 'lightcoral']

        for i, key in enumerate(keys_for_plotting):
            j = l - i - 1
            data = sweeping_freqs[key]

            _LR = [BW_lefts[key], BW_rights[key]]
            bandwidth_plot_x     = np.array([x.nominal_value for x in _LR])
            bandwidth_plot_x_err = np.array([x.std_dev for x in _LR])
            bandwidth_plot_y     = results[key].eval(x = bandwidth_plot_x) + j*offset

            fit_y = results[key].eval(x = fit_x) + j*offset
            fit_y_delta = results[key].eval_uncertainty(x = fit_x)

            # PLOT THE DATA
            plotter.axs.scatter(data.DATA["A"]["FREQ"], data.DATA["A"]["POWER"] + j*offset, marker = ".", label = f"{getNumFromKey(key)} kHz Modulation", color = colors[i], s = 6)
            plotter.axs.fill_between(fit_x, fit_y - fit_y_delta, fit_y + fit_y_delta, color='#888888')
            if i == 1:
                plotter.axs.plot(fit_x, fit_y, color = "tab:red", label = "erf-Rectangle Fit")
                plotter.axs.errorbar(x = bandwidth_plot_x, y = bandwidth_plot_y, xerr = bandwidth_plot_x_err, capsize = 5, ecolor = "black", color = "black", marker = "x", label = "3 dB Bandwidth")
            else:
                plotter.axs.plot(fit_x, fit_y, color = "tab:red")
                plotter.axs.errorbar(x = bandwidth_plot_x, y = bandwidth_plot_y, xerr = bandwidth_plot_x_err, capsize = 5, ecolor = "black", color = "black", marker = "x")

        plotter.axs.set_xlabel("Frequency (MHz)")
        plotter.axs.set_ylabel("Power after attenuation (dBm)")
        plotter.fig.suptitle("\\shortstack{Output RF Bandwidth from POS-150+ AOM Driver\\\\at different modulation frequencies}")

        plotter.axs.legend(loc='lower center', bbox_to_anchor = (0.5, -0.35), ncol=2, fancybox=True)
        plotter.fig.subplots_adjust(bottom=0.25) # https://www.adamsmith.haus/python/answers/how-to-place-a-legend-below-the-axes-in-matplotlib-in-python
        plotter.xlim([70,89])

    plotter.savefig(os.path.join(base_dir, "generated", "POS150+bandwidth.pdf"), backend = "pdf")
    plotter.clf()

# PLOTTING THE BANDWIDTH vs FREQ
BW_modfreqs = np.array([getNumFromKey(k) for k in keys]) # in kHz
BW_bandwidths = np.array([bandwidths[k].nominal_value for k in keys]) # in MHz
BW_bandwidths_err = np.array([bandwidths[k].std_dev for k in keys]) # in MHz

# FIT AN EXXPONENTIAL
BW_model = lmfit.models.ExponentialModel() + lmfit.models.ConstantModel()

BW_params = BW_model.make_params()
BW_result = BW_model.fit(BW_bandwidths, BW_params, x = BW_modfreqs, weights = 1.0/BW_bandwidths_err)

BW_A   = np.around(BW_result.params["amplitude"].value, decimals = 3)
BW_tau = np.around(BW_result.params["decay"].value, decimals = 3)
BW_c   = np.around(BW_result.params["c"].value, decimals = 3)

BW_fit_x = np.linspace(start = np.min(BW_modfreqs), stop = np.max(BW_modfreqs), num = 1000)
BW_fit_y = BW_result.eval(x = BW_fit_x)
BW_it_y_delta = BW_result.eval_uncertainty(x = BW_fit_x)

plotter2 = Plotter(figsize = (BW_figwidth, BW_figheight))
# https://stackoverflow.com/a/68160709
plotter2.axs.set_title("\\shortstack{Change in 3dB-Bandwidth of RF Output of POS-150+\\\\Voltage-Controlled Oscillator AOM Driver}")
plotter2.axs.errorbar(BW_modfreqs, BW_bandwidths, BW_bandwidths_err, capsize = 3, fmt = ' ', marker = 'x', color = "tab:blue", ecolor = "tab:blue", label = "Data", markersize = 5, elinewidth = 1)
plotter2.axs.plot(BW_fit_x, BW_fit_y, color = "tab:red", label = f"${BW_A}\\exp\\left(-\\nicefrac{{f\\!}}{{{BW_tau}}}\\right) + {BW_c}$")
plotter2.axs.fill_between(BW_fit_x, BW_fit_y - BW_it_y_delta, BW_fit_y + BW_it_y_delta, color='mistyrose')
plotter2.axs.set_ylabel("RF Output Bandwidth (MHz)")
plotter2.axs.set_xlabel("Modulation Frequency $f$ (kHz)")

BW_tau_uf = uncertainties.ufloat(BW_result.params["decay"].value, BW_result.params["decay"].stderr)
BW_t_half = BW_tau_uf * np.log(2)

print(f"Mean lifetime = {BW_tau_uf.nominal_value} +/- {BW_tau_uf.std_dev}")
print(f"Halflife      = {BW_t_half.nominal_value} +/- {BW_t_half.std_dev}")

# https://www.statology.org/matplotlib-legend-order/
handles, labels = plotter2.gca().get_legend_handles_labels()
order = [1,0]

plotter2.axs.legend([handles[idx] for idx in order],[labels[idx] for idx in order])
# ax.set_yscale("log")
# ax.set_xlim([0,100])
# ax.set_ylim([5,15])
# plotter2.show()
plotter2.savefig(os.path.join(base_dir, "generated", "POS150+bandwidth_change.pdf"), backend = "pdf")