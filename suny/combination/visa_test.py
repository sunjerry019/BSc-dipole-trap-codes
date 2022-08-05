#!/usr/bin/env python3

import pyvisa

rm = pyvisa.ResourceManager()
# rigol_session = rm.open_resource("USB0::0x1AB1::0x0642::DG1ZA233104002::INSTR") # Rigol DG1022
ress = rm.list_resources()
for res in ress:
    try:
        session = rm.open_resource(res)
        session.write('*IDN?')
        idn = session.read()

        print('{}: {}'.format(res, idn.rstrip('\n')))
        session.close()

    except pyvisa.errors.VisaIOError as e:
        print("{}: Not Available".format(res))



# rigol_session.close()
rm.close()