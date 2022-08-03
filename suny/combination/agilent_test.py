#!/usr/bin/env python3

import time
import pyvisa

rm = pyvisa.ResourceManager()
agilent_session = rm.open_resource("USB0::0x0957::0x1F01::MY48180595::INSTR", timeout = None)

agilent_session.write('*IDN?')
idn = agilent_session.read()

print('*IDN: %s' % idn.rstrip('\n'))

agilent_session.write("*RST")
agilent_session.write("FREQ 80 MHz")
agilent_session.write("POW -15 dB")
agilent_session.write("OUTP:STAT ON")

time.sleep(1)

agilent_session.write("OUTP:STAT OFF")

agilent_session.close()
rm.close()