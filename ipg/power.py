#!/usr/bin/env python3

import __init__

from plotter import Plotter
import pandas as pd
import os

datafile = os.path.join(__init__.base_dir, "power.dat")

data = pd.read_csv(datafile, sep = "\t")

# Generate LaTeX Table
for row in data.to_numpy():
    # print("")
    i = 0
    for item in row:
        if i != 0:
            print(" & \t", end = "")
        print(f"\\num{{{item}}}", end = "")
        i = 1
    print("\t\\\\")

P = Plotter(figsize = (6, 4))
P.ax.scatter(data["# Set point (%)"], data["Monitored Power (W)"], label = "Monitored Power", marker = 'x')
P.ax.scatter(data["# Set point (%)"], data["Measured Power (W)"], label = "Measured Power", marker = 'x')
P.ax.scatter(data["# Set point (%)"], data["Report Power (W)"], label = "Report Monitored Power", marker = 'x')
P.ax.scatter(data["# Set point (%)"], data["Report Power (W)"], label = "Report Measured Power", marker = 'x')
P.ax.legend()

P.ax.set_xlabel("Set Point on IPG Controller (\\%)")
P.ax.set_ylabel("Power (W)")
P.ax.set_title("Power vs. Set Point Measurement for the IPG Laser")
P.fig.tight_layout()

P.savefig(os.path.join(__init__.base_dir, "generated", "ipg-power.pdf"), backend = "pdf")

