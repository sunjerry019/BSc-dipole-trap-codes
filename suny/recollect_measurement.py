#!/usr/bin/env python3

import os
import time
import numpy as np
import pandas as pd
from datetime import datetime

import pyvisa

## SETTINGS
numsamples_power = 1
attenuation = 20
## / SETTINGS

base_dir = os.path.dirname(os.path.realpath(__file__))
data_file = os.path.join(base_dir, "aom_driver_characterisation", "Data-2022-08-08_100328.dat")

DATA = pd.read_csv(data_file, skiprows = 2, header = 0, sep = "\t")

freqss = DATA.iloc[:, [0,1]]
freqss = freqss.loc[np.around(freqss["Meas Freq/MHz"], decimals = 1) != freqss["# Set Freq/MHz"]]
bad_data = DATA.iloc[freqss.index]
print(bad_data)
total_measurements = len(bad_data)

# SET UP FOR FILE
base_dir = os.path.dirname(os.path.realpath(__file__))
now = datetime.now()
filename = os.path.join(base_dir, 'Data-{}-Amplifier_Map.dat'.format(now.strftime("%Y-%m-%d_%H%M%S")))

with open(filename, 'w') as f:
    f.write("# Data taken on {}\n".format(now.strftime("%Y-%m-%d_%H%M%S")))
    f.write(f"# RF Power Mappings, {attenuation} dBm Attenuation (already taken into account)\n")

    if numsamples_power > 1:
        f.write("# Set Freq/MHz\tMeas Freq/MHz\tRF Input/dBm\tAM Volt/V\tRF Output/dBm\tDev/dBm\n")
    else:
        f.write("# Set Freq/MHz\tMeas Freq/MHz\tRF Input/dBm\tAM Volt/V\tRF Output/dBm\n")
# / SET UP FOR FILE

# INIT DEVICES
rm = pyvisa.ResourceManager()
rigol_session   = rm.open_resource("USB0::0x1AB1::0x0641::DG4E225002331::INSTR", timeout = None) # Rigol DG4162
anritsu_session = rm.open_resource("USB0::0x0B5B::0xFFF9::2144030_1768_55::INSTR", timeout = None) # Anritsu MS2720T
agilent_session = rm.open_resource("USB0::0x0957::0x1F01::MY48180595::INSTR", timeout = None) # Agilent N5182A
# / INIT DEVICES

# INIT RIGOL
# == OUTP1 = Frequency Modulation on Agilent
# == OUTP2 = AM Modulation on AOM Driver / Amplifier
FM_MOD = 1
AM_MOD = 2

rigol_session.write(f"OUTP{FM_MOD}:STAT OFF")
rigol_session.write(f"OUTP{AM_MOD}:STAT OFF")
rigol_session.write(f"OUTP{AM_MOD}:STAT ON")
rigol_session.write(f"SOUR{AM_MOD}:FREQ {1e-6}")
rigol_session.write(f"SOUR{AM_MOD}:FUNC:SHAPE SQU")
rigol_session.write(f"SOUR{AM_MOD}:FUNC:SQU:DCYC 80") # Highest is 80%
rigol_session.write(f"SOUR{AM_MOD}:VOLT:LOW 0")
rigol_session.write(f"SOUR{AM_MOD}:VOLT:HIGH 0.1")
# / INIT RIGOL

# INIT ANRITSU
anritsu_session.write("DISP:WIND:TRAC:Y:SCAL:RLEV 30dBm")
# / INIT ANRITSU

# INIT AGILENT
agilent_session.write("*RST")
agilent_session.write("FREQ 80 MHz")
agilent_session.write("FM:DEV 0 Hz")
# / INIT AGILENT

all_dtpt = []
q = 0
for _, row in bad_data.iterrows():
    q += 1
    set_freq, meas_f, rf_power, am_volt, output_p = row

    agilent_session.write(f"FREQ {set_freq} MHz")
    agilent_session.write("OUTP:STAT ON")
    agilent_session.write(f"POW {rf_power} dBm")
    rigol_session.write(f"OUTP{AM_MOD}:STAT ON")
    rigol_session.write(f"SOUR{AM_MOD}:VOLT:HIGH {am_volt}")

    while True:
        time.sleep(0.5) # Wait before measuring

        anritsu_session.write("CALC:MARK1:MAX")

        anritsu_session.write("CALC:MARK1:X?")
        meas_freq = float(anritsu_session.read())/1e6

        if np.around(meas_freq, decimals = 1) == set_freq:
            break
    
    if numsamples_power > 1:
        measured_powers = []

        for i in range(numsamples_power):
            print(f"[{i}/{numsamples_power}] {set_freq} MHz\t{rf_power} dBm\t{am_volt} V", end = "\r")
            anritsu_session.write("CALC:MARK1:Y?")
            measured_powers.append(float(anritsu_session.read()))
        
        measured_powers = np.array(measured_powers)

        mean = np.average(measured_powers) + attenuation
        dev  = np.std(measured_powers)
    
        with open(filename, 'a') as f:
            f.write(f"{set_freq}\t{meas_freq}\t{rf_power}\t{am_volt}\t{mean}\t{dev}\n")
        
        print(f"[DONE/{numsamples_power}] {set_freq} MHz\t{rf_power} dBm\t{am_volt} V:\t{mean} +/- {dev} dBm")
    else:
        print(f"[{q}/{total_measurements}] {set_freq} MHz\t{rf_power} dBm\t{am_volt} V", end = "\r")
        anritsu_session.write("CALC:MARK1:Y?")
        measured_power = float(anritsu_session.read()) + attenuation

        all_dtpt.append([set_freq, meas_freq, rf_power, am_volt, measured_power])

        print(f"[{q}/{total_measurements}] {set_freq} MHz\t{rf_power} dBm\t{am_volt} V:\t{measured_power} dBm")

    if q % 10 == 0:
        rigol_session.write(f"OUTP{AM_MOD}:STAT OFF")
        agilent_session.write("OUTP:STAT OFF")
