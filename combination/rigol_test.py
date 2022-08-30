#!/usr/bin/env python3

import pyvisa
import time

rm = pyvisa.ResourceManager()
rigol_session = rm.open_resource("USB0::0x1AB1::0x0641::DG4E225002331::INSTR") # Rigol DG4162

# OUTP1 = Frequency Modulation on Agilent
# OUTP2 = AM Modulation on AOM Driver / Amplifier

FM_MOD = 1
AM_MOD = 2

rigol_session.write(f"OUTP{FM_MOD}:STAT OFF")
rigol_session.write(f"OUTP{AM_MOD}:STAT ON")
rigol_session.write(f"SOUR{AM_MOD}:FREQ {1e-6}")
rigol_session.write(f"SOUR{AM_MOD}:FUNC:SHAPE SQU")
rigol_session.write(f"SOUR{AM_MOD}:FUNC:SQU:DCYC 80") # Highest is 80%
rigol_session.write(f"SOUR{AM_MOD}:VOLT:LOW 0")
rigol_session.write(f"SOUR{AM_MOD}:VOLT:HIGH 2")
# rigol_session.write("OUTP1:STAT ON")

rigol_session.close()
rm.close()

