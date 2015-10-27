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
import os.path

import plotter


# BASIC CONFIGURATION
# Specify mapping of {"interface" -> [list of channels]} here. The "interface"
# is simply the serial interface or IP address of the Lakeshore box.
channel_map = {'/dev/ttyr00':   ['HEX', 'mainplate', 'He4 IC Pump', 'He3 IC Pump',
                                 'He3 UC Pump', 'He4 IC Switch', 'He3 IC Switch',  'He3 UC Switch'],
               '/dev/ttyr01':   ['PTC 4K stage', 'PTC 50K stage', 'channel 2', 'channel 3',
                                 'wiring harness', '4K shield near harness', '3G SQUIDs',  'SZ SQUIDs'],
               '192.168.0.12':  ['UC Head', 'IC Head', 'LC shield', 'LC board'],
               '192.168.2.5':   ['backplate', 'channel B', 'channel C', 'channel D']}

# Specify the variables to be plotted in each subplot of the display. This
# should be a list of lists of strings, where each list contains the variables
# contained in one subplot, and each string should be one of the variable names
# in the 'channel_map' above
plot_list = [[['He4 IC Pump', 'He3 IC Pump', 'He3 UC Pump'], ['He4 IC Switch', 'He3 IC Switch', 'He3 UC Switch']],
             [['HEX', 'mainplate']],
             [['PTC 4K stage'], ['PTC 50K stage']],
             [['UC Head', 'IC Head', 'LC shield', 'LC board']],
             [['wiring harness', '4K shield near harness', '3G SQUIDs', 'SZ SQUIDs']]]

# Specify mapping of {"interface" -> "human-readable description"}. This isn't
# used for anything specific right now, but it is worth having some more human-
# readable description about what interface name corresponds to which box, just
# in case it is ever needed somewhere, or minimally just for code readability.
interface_map = {}


# convenience functions for adding and removing underscores
def underscoreify(string):
    return string.replace(' ', '_')
def deunderscoreify(string):
    return string.replace('_', ' ')


# update frequency
dt_update = 10  # sec

# file name
data_filename = raw_input('Enter relative path to data file (must end in .h5): ')
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

# split up interface addresses by serial and TCP
serial_interface_address = [name for name in channel_map.keys() if '/dev' in name]
tcp_interface_address = [name for name in channel_map.keys() if '192.168' in name]
# check that we didn't miss interfaces in the split
if set(serial_interface_address + tcp_interface_address) != set(channel_map.keys()):
    print "WARNING: Could not parse all interface addresses as either serial or TCP. " + \
          "Some devices may not be read!"

# set up the serial interfaces
serial_interfaces = dict()
for interface_address in serial_interface_address:
    serial_interfaces[interface_address] = serial.Serial(interface_address, 9600, serial.SEVENBITS, serial.PARITY_ODD, serial.STOPBITS_ONE)

# setup the TCP interfaces
tcp_interfaces = dict()
for interface_address in tcp_interface_address:
    tcp_interfaces[interface_address] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_interfaces[interface_address].connect((interface_address, 7777))
    tcp_interfaces[interface_address].settimeout(1.0)


# main data acquisition loop
try:
    while True:
        # query the devices
        for interface_name in serial_interfaces:
            serial_interfaces[interface_name].write('KRDG?\r\n')
        for interface_address in tcp_interfaces:
            tcp_interfaces[interface_address].sendto('KRDG? 0\r\n', (interface_address, 7777))
        current_time = time.time()

        # wait for devices to issue a response
        time.sleep(0.2)

        # read the responses
        for interface_name in serial_interfaces:
            raw_output = serial_interfaces[interface_name].read(serial_interfaces[interface_name].inWaiting())
            for jValue in range(len(channel_map[interface_name])):
                channel_name = channel_map[interface_name][jValue]
                tables_list[channel_name].row['time'] = current_time
                tables_list[channel_name].row[channel_name] = float(raw_output.split(',')[jValue])
                tables_list[channel_name].row.append()
                tables_list[channel_name].flush()

        for interface_name in tcp_interfaces:
            raw_output, _ = tcp_interfaces[interface_name].recvfrom(2048)
            for jValue in range(len(channel_map[interface_name])):
                channel_name = channel_map[interface_name][jValue]
                tables_list[channel_name].row['time'] = current_time
                tables_list[channel_name].row[channel_name] = float(raw_output.split(',')[jValue])
                tables_list[channel_name].row.append()
                tables_list[channel_name].flush()

        # update the plots
        plotter.update_plot(tables_list, plot_list)

        # wait before reading again
        time.sleep(dt_update)

except KeyboardInterrupt:
    print "\nStopping data acquisition"

# close the connections
for interface_address in serial_interface_address:
    serial_interfaces[interface_address].close()
for interface_address in tcp_interface_address:
    tcp_interfaces[interface_address].close()
