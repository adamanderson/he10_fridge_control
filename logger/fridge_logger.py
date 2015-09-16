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
import socket
import time
import numpy as np
import tables
import lakeshore218
import lakeshore350

# channel labels
labels_lakeshore_218_1 = {'record time': tables.Time32Col(),
                          'HEX': tables.Float32Col(),
                          'mainplate': tables.Float32Col(),
                          'He4 IC Pump': tables.Float32Col(),
                          'He4 IC Pump': tables.Float32Col(),
                          'He4 UC Pump': tables.Float32Col(),
                          'He4 IC Switch': tables.Float32Col(),
                          'He3 IC Switch': tables.Float32Col(),
                          'He3 Uc Switch': tables.Float32Col(),
                          }
labels_lakeshore_218_2 = {'record time': tables.Time32Col(),
                          'channel 0': tables.Float32Col(),
                          'channel 1': tables.Float32Col(),
                          'channel 2': tables.Float32Col(),
                          'channel 3': tables.Float32Col(),
                          'channel 4': tables.Float32Col(),
                          'channel 5': tables.Float32Col(),
                          'channel 6': tables.Float32Col(),
                          'channel 7': tables.Float32Col(),
                          }
labels_lakeshore_350 = {'record time': tables.Time32Col(),
                        'UC Head': tables.Float32Col(),
                        'IC Head': tables.Float32Col(),
                        'UC Stage': tables.Float32Col(),
                        'IC Stage': tables.Float32Col(),
                        }

# update frequency
dt_update = 10  # sec

# create output files
# f_text_1 = open('r00.txt', 'a')
# f_text_2 = open('r01.txt', 'a')
f_h5 = tables.open_file('data/fridge_data.h5', mode='w', title='fridge data')
group_all_data = f_h5.create_group('/', 'data', 'all data')
table_lakeshore_218_1 = f_h5.create_table(group_all_data, 'LS_218_1', labels_lakeshore_218_1, "Data from Lakeshore 218 #1")
table_lakeshore_218_2 = f_h5.create_table(group_all_data, 'LS_218_2', labels_lakeshore_218_2, "Data from Lakeshore 218 #2")
table_lakeshore_350 = f_h5.create_table(group_all_data, 'LS_350', labels_lakeshore_350, "Data from Lakeshore 350")

# set up serial ports
lakeshore_218_1 = serial.Serial('/dev/ttyr00', 9600, serial.SEVENBITS, serial.PARITY_ODD, serial.STOPBITS_ONE )
lakeshore_218_2 = serial.Serial('/dev/ttyr01', 9600, serial.SEVENBITS, serial.PARITY_ODD, serial.STOPBITS_ONE )

# set up ethernet for Lakeshore 350
# please note that ethernet settings different from these WILL NOT WORK!
# in addition, the '\r\n' in the message sent to the lakeshore is MANDATORY!
address_lakeshore_350 = ('192.168.0.12', 7777) # default settings for the lakeshore 350
socket_lakeshore_350 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_lakeshore_350.connect(address_lakeshore_350)
socket_lakeshore_350.settimeout(1.0)


# main loop
try:
    while True:
        # query the Lakeshore devices
        lakeshore_218_1.write('KRDG?\r\n')
        lakeshore_218_2.write('KRDG?\r\n')
        socket_lakeshore_350.sendto('KRDG? 0\r\n', address_lakeshore_350)

        # wait for the Lakeshores to issue a response
        time.sleep(0.2)

        # read the response
        out_lakeshore_218_1 = lakeshore_218_1.read(lakeshore_218_1.inWaiting())
        out_lakeshore_218_2 = lakeshore_218_2.read(lakeshore_218_2.inWaiting())
        out_lakeshore_350, addr = socket_lakeshore_350.recvfrom(2048)

        # # write the data to text files (for backwards compatibility)
        # time_struct = time.localtime()
        # time_string = str(time_struct.tm_year) + ' ' + \
        #               str(time_struct.tm_mon) + ' ' + \
        #               str(time_struct.tm_mday) + ' ' + \
        #               str(time_struct.tm_hour) + ' ' + \
        #               str(time_struct.tm_min) + ' ' + \
        #               str(time_struct.tm_sec) + ' '
        # f_text_1.write(time_string + out_lakeshore_218_1)
        # f_text_2.write(time_string + out_lakeshore_218_2)

        # write the data to a pytables file for more modern storage
        lakeshore218.write(table_lakeshore_218_1.row, labels_lakeshore_218_1, out_lakeshore_218_1)
        table_lakeshore_218_1.flush()
        lakeshore218.write(table_lakeshore_218_2.row, labels_lakeshore_218_2, out_lakeshore_218_2)
        table_lakeshore_218_2.flush()
        lakeshore350.write(table_lakeshore_350.row, labels_lakeshore_350, out_lakeshore_350)
        table_lakeshore_350.flush()

        # wait before reading again
        time.sleep(dt_update)

except KeyboardInterrupt:
    print "\nStopping data acquisition"

# close the connections
lakeshore_218_1.close()
lakeshore_218_2.close()
socket_lakeshore_350.close()
