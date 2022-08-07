#!/usr/bin/env python3

import pyvisa
from ThorlabsPM100 import ThorlabsPM100
import time
from datetime import datetime

import sys, os

import numpy as np

# SETTINGS
numsamples = 3000
# SETTINGS

base_dir = os.path.dirname(os.path.realpath(__file__))

now = datetime.now()
filename = os.path.join(base_dir, 'Data-{}.dat'.format(now.strftime("%Y-%m-%d_%H%M%S")))

with open(filename, 'w') as f:
    f.write("# Data taken on {}\n".format(now.strftime("%Y-%m-%d_%H%M%S")))
    f.write("# RF Input/dBm\tPower/uW\tDev/uW\n")

rm = pyvisa.ResourceManager()
agilent_session     = rm.open_resource("USB0::0x0957::0x1F01::MY48180595::INSTR", timeout = None)
power_meter_session = rm.open_resource("USB0::0x1313::0x8075::P5003613::INSTR"  , timeout = None)

power_meter = ThorlabsPM100(inst = power_meter_session)
power_meter.configure.scalar.power()
power_meter.sense.correction.wavelength = 1064
power_meter.sense.current.dc.range.auto = 1
power_meter.sense.power.dc.unit = "W"

agilent_session.write("*RST")
agilent_session.write("FREQ 80 MHz")
# agilent_session.write("FM:INT:FREQ 0 Hz")
# Setting the frequency modulation deviation to 0 Hz.
agilent_session.write("FM:DEV 0 Hz")

powers = np.around(np.linspace(start = 0, stop = -15, endpoint = True, num = 61), decimals = 2)
print(powers)

for RFpower in powers:
    print(f"Taking data for {RFpower} dBm")

    agilent_session.write(f"POW {RFpower} dBm")
    agilent_session.write("OUTP:STAT ON")
    time.sleep(1)

    print("Taking Optical Power Data...")
    power_meas = []
    for i in range(numsamples):
        power_meas.append(power_meter.read)
        print(f"... Point {i + 1}/{numsamples}", end = "\r")
        time.sleep(80e-3) # 80 ms
    print("")
    power_meas_np = np.array(power_meas) * 1e6
    print("Taking Optical Power Data...Done")

    agilent_session.write("OUTP:STAT OFF")

    dtpt = [ RFpower, np.mean(power_meas_np), np.std(power_meas_np) ]
    dtpt = [ str(x) for x in dtpt ]

    with open(filename, 'a') as f:
        f.write("\t".join(dtpt))
        f.write("\n")

    print(dtpt)
    print("")

power_meter_session.close()
agilent_session.close()
rm.close()
