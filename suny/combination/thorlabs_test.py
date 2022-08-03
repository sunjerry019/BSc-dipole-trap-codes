#!/usr/bin/env python3

# Use Driver Switcher to switch to VISA driver

from numpy import power
import pyvisa
from ThorlabsPM100 import ThorlabsPM100
import time

import numpy as np

# SETTINGS
numsamples = 3000
# SETTINGS

rm = pyvisa.ResourceManager()
inst = rm.open_resource("USB0::0x1313::0x8075::P5003613::INSTR", timeout=None)

# https://stackoverflow.com/q/67257646
power_meter = ThorlabsPM100(inst=inst)

power_meter.configure.scalar.power()
power_meter.sense.correction.wavelength = 1064
power_meter.sense.current.dc.range.auto = 1
power_meter.sense.power.dc.unit = "W"

print("Taking Data...")
power_meas = []
for i in range(numsamples):
    power_meas.append(power_meter.read)
    print(f"Taking Data {i + 1}/{numsamples}", end = "\r")
    time.sleep(80e-3) # 80 ms
print("")
power_meas_np = np.array(power_meas) * 1e6

print("Taking Data done")
print(f"Mean: {np.mean(power_meas_np)}\tStd Dev:{np.std(power_meas_np)}")
