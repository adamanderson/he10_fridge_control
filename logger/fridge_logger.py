# fridge_logger.py
#
# A logging script for the He10 fridge that records temperatures. The data is
# saved in a text file (or perhaps hdf5 file in the future) and can be accessed
# later by the plotting script or the fridge control script when it performs
# an automatic fridge cycle.
#
# Adam Anderson
# adama@fnal.gov
# 12 September 2015

import serial
import time
import numpy as np

# update frequency
dt_update = 10  # sec

# output file info
f_text_1 = open('r00.txt', 'w')
f_text_2 = open('r01.txt', 'w')

# read a serial port
lakeshore_218_1 = serial.Serial('/dev/ttyr00', 9600, serial.SEVENBITS, serial.PARITY_ODD, serial.STOPBITS_ONE )
lakeshore_218_2 = serial.Serial('/dev/ttyr01', 9600, serial.SEVENBITS, serial.PARITY_ODD, serial.STOPBITS_ONE )

print lakeshore_218_1.name
print lakeshore_218_2.name

try:
    while True:
        # query the Lakeshore devices
        lakeshore_218_1.write('KRDG?\r\n')
        lakeshore_218_2.write('KRDG?\r\n')

        # give the Lakeshores time to issue a response
        time.sleep(.2)

        # read the response
        out_lakeshore_218_1 = lakeshore_218_1.read(lakeshore_218_1.inWaiting())
        out_lakeshore_218_2 = lakeshore_218_2.read(lakeshore_218_2.inWaiting())
        
        # write the data to text files (for backwards compatibility)
        time_struct = time.localtime()
        time_string = str(time_struct.tm_year) + ' ' + \
                      str(time_struct.tm_mon) + ' ' + \
                      str(time_struct.tm_mday) + ' ' + \
                      str(time_struct.tm_hour) + ' ' + \
                      str(time_struct.tm_min) + ' ' + \
                      str(time_struct.tm_sec) + ' '
        f_text_1.write(time_string + out_lakeshore_218_1)
        f_text_2.write(time_string + out_lakeshore_218_2)

        # wait before reading again
        time.sleep(dt_update)

except KeyboardInterrupt:
    print "\nStopping data acquisition"

# close the serial connections
lakeshore_218_1.close()
lakeshore_218_2.close()

