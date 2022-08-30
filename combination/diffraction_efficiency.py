#!/usr/bin/env python3

import pyvisa
from ThorlabsPM100 import ThorlabsPM100
import time
from datetime import datetime

import sys, os

import numpy as np

# SETTINGS
numsamples = 3000
AM_MOD_VOLT = 6
powers = np.around(np.linspace(start = 0, stop = -15, endpoint = True, num = (15*4 + 1)), decimals = 2)
print("Powers: ", powers)
frequencies = np.around(np.linspace(start = 55, stop = 105, endpoint = True, num = (50*4 + 1)), decimals = 4)
print("Frequencies", frequencies)
# SETTINGS

base_dir = os.path.dirname(os.path.realpath(__file__))

now = datetime.now()
filename = os.path.join(base_dir, 'Data-{}.dat'.format(now.strftime("%Y-%m-%d_%H%M%S")))

with open(filename, 'w') as f:
    f.write("# Data taken on {}\n".format(now.strftime("%Y-%m-%d_%H%M%S")))
    f.write(f"# Amplifier AM Modulation Voltage: {AM_MOD_VOLT} V\n")
    f.write("# RF Freq/MHz\tRF Input/dBm\tPower/uW\tDev/uW\n")

rm = pyvisa.ResourceManager()
agilent_session     = rm.open_resource("USB0::0x0957::0x1F01::MY48180595::INSTR", timeout = None)
rigol_session       = rm.open_resource("USB0::0x1AB1::0x0641::DG4E225002331::INSTR", timeout = None)
power_meter_session = rm.open_resource("USB0::0x1313::0x8075::P5003613::INSTR"  , timeout = None)


# SET UP POWERMETER
power_meter = ThorlabsPM100(inst = power_meter_session)
power_meter.configure.scalar.power()
power_meter.sense.correction.wavelength = 1064
power_meter.sense.current.dc.range.auto = 1
power_meter.sense.power.dc.unit = "W"
# / SET UP POWERMETER

# SET UP AGILENT
agilent_session.write("*RST")
agilent_session.write("FREQ 80 MHz")
# agilent_session.write("FM:INT:FREQ 0 Hz")
# Setting the frequency modulation deviation to 0 Hz.
agilent_session.write("FM:DEV 0 Hz")
# / SET UP AGILENT

# SET UP RIGOL
# OUTP1 = Frequency Modulation on Agilent
# OUTP2 = AM Modulation on AOM Driver / Amplifier
FM_MOD = 1
AM_MOD = 2

rigol_session.write(f"OUTP{FM_MOD}:STAT OFF")
rigol_session.write(f"OUTP{AM_MOD}:STAT OFF")

rigol_session.write(f"OUTP{AM_MOD}:STAT ON")
rigol_session.write(f"SOUR{AM_MOD}:FREQ {1e-6}")
rigol_session.write(f"SOUR{AM_MOD}:FUNC:SHAPE SQU")
rigol_session.write(f"SOUR{AM_MOD}:FUNC:SQU:DCYC 80") # Highest is 80%
rigol_session.write(f"SOUR{AM_MOD}:VOLT:LOW 0")
rigol_session.write(f"SOUR{AM_MOD}:VOLT:HIGH {AM_MOD_VOLT}")
# / SET UP RIGOL

# DO MEASUREMENT
for freq in frequencies:
    agilent_session.write(f"FREQ {freq} MHz")

    for RFpower in powers:
        agilent_session.write(f"POW {RFpower} dBm")
        agilent_session.write("OUTP:STAT ON")
        time.sleep(1)

        # print("Taking Optical Power Data...")
        power_meas = []
        for i in range(numsamples):
            power_meas.append(power_meter.read)
            print(f"[{i + 1}/{numsamples}]\t{freq} MHz\t{RFpower} dBm", end = "\r")
            time.sleep(80e-3) # 80 ms
        print("")
        power_meas_np = np.array(power_meas) * 1e6
        # print("Taking Optical Power Data...Done")

        agilent_session.write("OUTP:STAT OFF")

        mean = np.mean(power_meas_np)
        dev  = np.std(power_meas_np)

        dtpt = [ freq, RFpower, mean, dev ]
        dtpt = [ str(x) for x in dtpt ]

        with open(filename, 'a') as f:
            f.write("\t".join(dtpt))
            f.write("\n")

        print(f"[DONE/{numsamples}]\t{freq} MHz\t{RFpower} dBm:\t{mean} +/- {dev} uW", end = "\n")

power_meter_session.close()
rigol_session.close()
agilent_session.close()
rm.close()
