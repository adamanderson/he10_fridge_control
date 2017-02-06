# fridge_logger.py
#
# A logging script for the ANL fridge that records temperatures. The data is
# saved in a text file (or perhaps hdf5 file in the future) and can be accessed
# later by the plotting script or the fridge control script when it performs
# an automatic fridge cycle.
#
# Original code by:
# Adam Anderson
# adama@fnal.gov
# 12 September 2015
#
# Modified heavily by:
# Faustin Carter
# Feb. 4, 2016

import serial
import time
import numpy as np
import tables
import os.path
import shutil

import plotter


# BASIC CONFIGURATION
# Specify mapping of {"interface" -> [list of channels]} here. The "interface"
# is simply the serial interface or IP address of the Lakeshore box.
# List of channels contains tuple of (channel name, channel number)
channel_map = {'/dev/ttyr13':   [('He4 IC Switch',  '1'),
                                 ('He3 IC Switch',  '2'),
                                 ('He3 UC Pump',    '3'),
                                 ('He3 UC Switch',  '4'),
                                 ('He3 IC Pump',    '5'),
                                 ('mainplate',      '6'),
                                 ('HEX',            '7'),
                                 ('He4 IC Pump',    '8')],

               '/dev/ttyr18':   [('UC Head',        'A'),
                                 ('IC Head',        'B'),
                                 ('PTC 50K Plate',  'C2'),
                                 ('PTC 4K Plate',   'C1'),
                                 ('SQUID D1',       'D1'),
                                 ('SQUID D2',       'D2')]}

# Specify the variables to be plotted in each subplot of the display. This
# should be a list of lists of (1 or 2) lists of strings, where each outer list contains the variables
# contained in one subplot, the collections of 1 or 2 lists indicated whether
# one or two y-axis scales should be used, and the variable names in the
# final lists are the names from 'channel_map' above which should be mapped to
# each y-axis scale.
plot_list = [[['He4 IC Pump', 'He3 IC Pump', 'He3 UC Pump'],
                ['He4 IC Switch', 'He3 IC Switch', 'He3 UC Switch']],
             [['HEX', 'mainplate']],
             [['PTC 4K Plate'], ['PTC 50K Plate']],
             [['UC Head', 'IC Head']],
             [['SQUID D1', 'SQUID D2']]]

# update frequency
dt_update = 2  # sec


# convenience functions for adding and removing underscores
def underscoreify(string):
    return string.replace(' ', '_')
def deunderscoreify(string):
    return string.replace('_', ' ')

#A handy function to read one temperature point from one channel.
#This is less efficient than reading all channels at once, but much easier
#to recover from when something goes wrong.
def read_temp_LS(interface, channel, num_trys = 10, delay = 0.1):
    """First attempt at making a reader that does a little bit of data validation"""
    for num in range(num_trys):
        #flush the I/O buffers
        interface.flushInput()
        interface.flushOutput()

        #Ask for the temperature
        interface.write('KRDG? ' + channel + '\r\n')

        #Wait a hot tenth of a second
        time.sleep(delay)

        #Read all the bytes that are at the port
        raw_output = interface.read(interface.inWaiting())

        #Check that the string ends with the terminator. If not, try again
        if raw_output[-2:] == '\r\n'
            #If the data is bad or incomplete, float conversion may fail
            try:
                #Strip off the term char (usually '\r\n'))
                #and convert to float
                temp = float(raw_output.strip())
            except ValueError:
                pass
            else:
                return temp

        #Welp, that didn't work, try again!
        print 'Problem reading from: ' + interface + ':' + channel
        print 'Raw output is: ' + repr(raw_output)
        print 'Will try ' + str(num_trys - 1 - num) + ' more times before aborting.'
        time.sleep(delay)

    raise NameError("Lost communication with: " + interface)

# file name
data_filename = raw_input('Enter relative path to data file (must end in .h5). NB: If enter an existing filename, the script will attempt to append that file, by default: ')
if os.path.isfile(data_filename) == True:
    print data_filename + ' already exists. Attempting to append data to end of file. If thermometer names differ in the existing file, this may fail.'
    pytables_mode = 'a'
else:
    print 'Attempting to create data file ' + data_filename
    pytables_mode = 'w'

# create output file
f_h5 = tables.open_file(data_filename, mode=pytables_mode, title='fridge data') # append file, by default
try:
    group_all_data = f_h5.get_node('/data')
except tables.NoSuchNodeError:
    group_all_data = f_h5.create_group('/', 'data', 'all data')
tables_list = dict()
for interface in channel_map:
    for channel in channel_map[interface]:
        try:
            # try pulling table from the file, which should work if it exists
            tables_list[channel] = f_h5.get_node('/data/' + underscoreify(channel))
        except tables.NoSuchNodeError:
            # otherwise, the file presumably doesn't exist and we need new tables
            table_columns = {'time': tables.Time32Col(), channel: tables.Float32Col()}
            tables_list[channel] = f_h5.create_table(group_all_data, underscoreify(channel), table_columns, channel)

# set up the serial interfaces
serial_interfaces = dict()
for interface_address in channel_map.keys():
    serial_interfaces[interface_address] = serial.Serial(interface_address,
                                                         9600,
                                                         serial.SEVENBITS,
                                                         serial.PARITY_ODD,
                                                         serial.STOPBITS_ONE)


# main data acquisition loop
try:
    while True:

        for serial_interface in serial_interfaces:
            for channel_name, channel_num in channel_map[serial_interface]:
                #Fill up the columns of a table row with data
                tables_list[channel_name].row[channel_name] = read_temp_LS(serial_interface, channel_num)
                tables_list[channel_name].row['time'] = time.time()

                #Send data to I/O buffer
                tables_list[channel_name].row.append()

                #Write data to disk and clear buffer
                tables_list[channel_name].flush()

        # update the plots
        plotter.update_plot(tables_list, plot_list)
        plotter.write_table('../website/datatable.html', tables_list, plot_list)

        # make a copy of the data file; useful for other processes that need
        # access to the latest data since we cannot do simultaneous read/write
        # of pytables files
        shutil.copyfile(data_filename, data_filename + str('.lock'))
        shutil.move(data_filename + str('.lock'), data_filename.strip('.h5') + '_read.h5')

        # wait before reading again
        time.sleep(dt_update)

except KeyboardInterrupt:
    print "\nStopping data acquisition"

# close the connections
for interface_address in serial_interface_address:
    serial_interfaces[interface_address].close()
