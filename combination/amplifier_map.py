#!/usr/bin/env python3

import time
from datetime import datetime
import pyvisa

import sys, os
import numpy as np

# SETTINGS
numsamples_power = 1
agilent_powers = np.around(np.linspace(start = 0  , stop = -20, endpoint = True, num = (20*2 + 1)), decimals = 2)
am_voltages    = np.around(np.linspace(start = 6  , stop = 0.5, endpoint = True, num = int(np.around(5.5 * 4 + 1, decimals = 0))), decimals = 4)
frequencies    = np.around(np.linspace(start = 55 , stop = 105, endpoint = True, num = (50*2 + 1)), decimals = 3)
attenuation    = 20 # dBm
# / SETTINGS

# SET UP FOR FILE
base_dir = os.path.dirname(os.path.realpath(__file__))
now = datetime.now()
filename = os.path.join(base_dir, 'Data-{}.dat'.format(now.strftime("%Y-%m-%d_%H%M%S")))

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

# DO MEASUREMENTS
q = 0
total_measurements = len(frequencies) * len(agilent_powers) * len(am_voltages)

assert numsamples_power > 0

all_dtpt = []

try:
    for freq in frequencies:
        agilent_session.write(f"FREQ {freq} MHz")
        agilent_session.write("OUTP:STAT ON")

        for power in agilent_powers:
            agilent_session.write(f"POW {power} dBm")
            rigol_session.write(f"OUTP{AM_MOD}:STAT ON")

            for am_volt in am_voltages:
                q += 1

                rigol_session.write(f"SOUR{AM_MOD}:VOLT:HIGH {am_volt}")
                time.sleep(0.3) # Wait before measuring

                anritsu_session.write("CALC:MARK1:MAX")

                anritsu_session.write("CALC:MARK1:X?")
                meas_freq = float(anritsu_session.read())/1e6

                if numsamples_power > 1:
                    measured_powers = []

                    for i in range(numsamples_power):
                        print(f"[{i}/{numsamples_power}] {freq} MHz\t{power} dBm\t{am_volt} V", end = "\r")
                        anritsu_session.write("CALC:MARK1:Y?")
                        measured_powers.append(float(anritsu_session.read()))
                    
                    measured_powers = np.array(measured_powers)

                    mean = np.average(measured_powers) + attenuation
                    dev  = np.std(measured_powers)
                
                    with open(filename, 'a') as f:
                        f.write(f"{freq}\t{meas_freq}\t{power}\t{am_volt}\t{mean}\t{dev}\n")
                    
                    print(f"[DONE/{numsamples_power}] {freq} MHz\t{power} dBm\t{am_volt} V:\t{mean} +/- {dev} dBm")
                else:
                    print(f"[{q}/{total_measurements}] {freq} MHz\t{power} dBm\t{am_volt} V", end = "\r")
                    anritsu_session.write("CALC:MARK1:Y?")
                    measured_power = float(anritsu_session.read()) + attenuation

                    all_dtpt.append([freq, meas_freq, power, am_volt, measured_power])

                    print(f"[{q}/{total_measurements}] {freq} MHz\t{power} dBm\t{am_volt} V:\t{measured_power} dBm")

            rigol_session.write(f"OUTP{AM_MOD}:STAT OFF")
        agilent_session.write("OUTP:STAT OFF")
finally:
    # If numsamples == 1, save data later (SPEED UP)
    if numsamples_power == 1:
        with open(filename, 'a') as f:
            for (freq, meas_freq, power, am_volt, measured_power) in all_dtpt:
                f.write(f"{freq}\t{meas_freq}\t{power}\t{am_volt}\t{measured_power}\n")

    # CLOSE DEVICES
    agilent_session.close()
    anritsu_session.close()
    rigol_session.close()
    rm.close()
    # / CLOSE DEVICES

# / DO MEASUREMENTS
