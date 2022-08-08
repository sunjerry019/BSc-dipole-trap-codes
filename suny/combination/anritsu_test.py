#!/usr/bin/env python3

import pyvisa
import time

rm = pyvisa.ResourceManager()
anritsu_session = rm.open_resource("USB0::0x0B5B::0xFFF9::2144030_1768_55::INSTR") # Anritsu MS2720T

anritsu_session.write("DISP:WIND:TRAC:Y:SCAL:RLEV 30dBm")
anritsu_session.write("CALC:MARK1:MAX")
anritsu_session.write("CALC:MARK1:Y?")

power_level = anritsu_session.read()
print(power_level)

anritsu_session.write("CALC:MARK1:X?")
f = float(anritsu_session.read())/1e6
print(f)

anritsu_session.close()
rm.close()

