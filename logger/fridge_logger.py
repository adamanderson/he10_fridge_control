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
import shutil
import os.path

import plotter

# channel labels
labels_lakeshore_218_1 = {'record time': tables.Time32Col(pos=0),
                          'HEX': tables.Float32Col(pos=1),
                          'mainplate': tables.Float32Col(pos=2),
                          'He4 IC Pump': tables.Float32Col(pos=3),
                          'He3 IC Pump': tables.Float32Col(pos=4),
                          'He3 UC Pump': tables.Float32Col(pos=5),
                          'He4 IC Switch': tables.Float32Col(pos=6),
                          'He3 IC Switch': tables.Float32Col(pos=7),
                          'He3 UC Switch': tables.Float32Col(pos=8),
                          }
keys_lakeshore_218_1 = ['record time', 'HEX', 'mainplate', 'He4 IC Pump', 'He3 IC Pump',
                        'He3 UC Pump', 'He4 IC Switch', 'He3 IC Switch',  'He3 UC Switch']
labels_lakeshore_218_2 = {'record time': tables.Time32Col(pos=0),
                          'PTC 4K stage': tables.Float32Col(pos=1),
                          'PTC 50K stage': tables.Float32Col(pos=2),
                          'channel 2': tables.Float32Col(pos=3),
                          'channel 3': tables.Float32Col(pos=4),
                          'wiring harness': tables.Float32Col(pos=5),
                          '4K shield near harness': tables.Float32Col(pos=6),
                          '4K plate near harness': tables.Float32Col(pos=7),
                          'SQUID board': tables.Float32Col(pos=8),
                          }
keys_lakeshore_218_2 = ['record time', 'PTC 4K stage', 'PTC 50K stage', 'channel 2', 'channel 3',
                        'wiring harness', '4K shield near harness', '3G SQUIDs',  'SZ SQUIDs']
labels_lakeshore_350_1 = {'record time': tables.Time32Col(pos=0),
                          'UC Head': tables.Float32Col(pos=1),
                          'IC Head': tables.Float32Col(pos=2),
                          'LC shield': tables.Float32Col(pos=3),
                          'LC board': tables.Float32Col(pos=4),
                          }
keys_lakeshore_350_1 = ['record time', 'UC Head', 'IC Head', 'LC shield', 'LC board']
labels_lakeshore_350_2 = {'record time': tables.Time32Col(pos=0),
                          'backplate': tables.Float32Col(pos=1),
                          'channel B': tables.Float32Col(pos=2),
                          'channel C': tables.Float32Col(pos=3),
                          'channel D': tables.Float32Col(pos=4),
                        }
keys_lakeshore_350_2 = ['record time', 'backplate', 'channel B', 'channel C', 'channel D']

# update frequency
dt_update = 10  # sec

# file name
data_filename = raw_input('Enter relative path to data file (must end in .h5): ')
if os.path.isfile(data_filename) == True:
    print data_filename + ' already exists. Attempting to append data to end of file. If thermometer names differ in the existing file, this may fail.'
    pytables_mode = 'a'
else:
    print 'Attempting to create data file ' + data_filename '.'
    pytables_mode = 'w'

# create output file
f_h5 = tables.open_file(data_filename, mode=pytables_mode, title='fridge data') # append file, by default
try:
    # try pulling the tables from the file, which should work if it exists
    group_all_data = f_h5.get_node('/data')
    table_lakeshore_218_1 = f_h5.get_node('/data/LS_218_1')
    table_lakeshore_218_2 = f_h5.get_node('/data/LS_218_2')
    table_lakeshore_350_1 = f_h5.get_node('/data/LS_350_1')
    table_lakeshore_350_2 = f_h5.get_node('/data/LS_350_2')
except tables.NoSuchNodeError:
    # otherwise, the file presumably doesn't exist and we need new tables
    group_all_data = f_h5.create_group('/', 'data', 'all data')
    table_lakeshore_218_1 = f_h5.create_table(group_all_data, 'LS_218_1', labels_lakeshore_218_1, "Data from Lakeshore 218 #1")
    table_lakeshore_218_2 = f_h5.create_table(group_all_data, 'LS_218_2', labels_lakeshore_218_2, "Data from Lakeshore 218 #2")
    table_lakeshore_350_1 = f_h5.create_table(group_all_data, 'LS_350_1', labels_lakeshore_350_1, "Data from Lakeshore 350 #1")
    table_lakeshore_350_2 = f_h5.create_table(group_all_data, 'LS_350_2', labels_lakeshore_350_2, "Data from Lakeshore 350 #2")

# set up serial ports
lakeshore_218_1 = serial.Serial('/dev/ttyr00', 9600, serial.SEVENBITS, serial.PARITY_ODD, serial.STOPBITS_ONE )
lakeshore_218_2 = serial.Serial('/dev/ttyr01', 9600, serial.SEVENBITS, serial.PARITY_ODD, serial.STOPBITS_ONE )

# set up ethernet for Lakeshore 350
# please note that ethernet settings different from these WILL NOT WORK!
# in addition, the '\r\n' in the message sent to the lakeshore is MANDATORY!
address_lakeshore_350_1 = ('192.168.0.12', 7777) # default settings for the lakeshore 350 #1
lakeshore_350_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lakeshore_350_1.connect(address_lakeshore_350_1)
lakeshore_350_1.settimeout(1.0)
address_lakeshore_350_2 = ('192.168.2.5', 7777)  # default settings for the lakeshore 350 #2 (when #1 is plugged in!)
lakeshore_350_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lakeshore_350_2.connect(address_lakeshore_350_2)
lakeshore_350_2.settimeout(1.0)


# main loop
try:
    while True:
        # query the Lakeshore devices
        lakeshore_218_1.write('KRDG?\r\n')
        lakeshore_218_2.write('KRDG?\r\n')
        lakeshore_350_1.sendto('KRDG? 0\r\n', address_lakeshore_350_1)
        lakeshore_350_2.sendto('KRDG? 0\r\n', address_lakeshore_350_2)

        # wait for the Lakeshores to issue a response
        time.sleep(0.2)

        # read the response
        out_lakeshore_218_1 = lakeshore_218_1.read(lakeshore_218_1.inWaiting())
        out_lakeshore_218_2 = lakeshore_218_2.read(lakeshore_218_2.inWaiting())
        out_lakeshore_350_1, _ = lakeshore_350_1.recvfrom(2048)
        out_lakeshore_350_2, _ = lakeshore_350_2.recvfrom(2048)

        # write the data to a pytables file
        lakeshore218.write(table_lakeshore_218_1.row, keys_lakeshore_218_1, out_lakeshore_218_1)
        table_lakeshore_218_1.flush()
        lakeshore218.write(table_lakeshore_218_2.row, keys_lakeshore_218_2, out_lakeshore_218_2)
        table_lakeshore_218_2.flush()
        lakeshore350.write(table_lakeshore_350_1.row, keys_lakeshore_350_1, out_lakeshore_350_1)
        table_lakeshore_350_1.flush()
        lakeshore350.write(table_lakeshore_350_2.row, keys_lakeshore_350_2, out_lakeshore_350_2)
        table_lakeshore_350_2.flush()

        # duplicate the pytables file so that it can be read by other processes
        # as needed
        shutil.copyfile(data_filename, data_filename + str('.lock'))
        shutil.move(data_filename + str('.lock'), data_filename.strip('.h5') + '_read.h5')

        plotter.update_plot(table_lakeshore_218_1, table_lakeshore_218_2, table_lakeshore_350_1, table_lakeshore_350_2)

        # wait before reading again
        time.sleep(dt_update)

except KeyboardInterrupt:
    print "\nStopping data acquisition"

# close the connections
lakeshore_218_1.close()
lakeshore_218_2.close()
lakeshore_350_1.close()
lakeshore_350_2.close()
