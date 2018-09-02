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
import os
import os.path
import shutil
import argparse as ap
import plotter

P0 = ap.ArgumentParser(description='Plotter for Chase He10 fridge.',
                       formatter_class=ap.RawTextHelpFormatter)
P0.add_argument('logfile', action='store', default=None, type=str,
                help='Name of HDF5 file to which to write temperature data.')
args = P0.parse_args()

# BASIC CONFIGURATION
# Specify mapping of {"interface" -> [list of channels]} here. The "interface"
# is simply the serial interface or IP address of the Lakeshore box.
channel_map = {'/dev/ttyr00':   ['HEX', 'mainplate', 'He4 IC Pump', 'He3 IC Pump',
                                 'He3 UC Pump', 'He4 IC Switch', 'He3 IC Switch',  'He3 UC Switch'],
               '/dev/ttyr01':   ['PTC 4K stage', 'PTC 50K stage', 'cold load center', 'cold load side',
                                 'blackbody', '4K shield near harness', 'SQUID 6',  'SQUID 7'],
               '192.168.0.12':  ['UC Head', 'IC Head', 'UC stage', 'UC stage 2']}

# Specify the variables to be plotted in each subplot of the display. This
# should be a list of lists of (1 or 2) lists of strings, where each outer list contains the variables
# contained in one subplot, the collections of 1 or 2 lists indicated whether
# one or two y-axis scales should be used, and the variable names in the
# final lists are the names from 'channel_map' above which should be mapped to
# each y-axis scale.
plot_list = [[['He4 IC Pump', 'He3 IC Pump', 'He3 UC Pump'], ['He4 IC Switch', 'He3 IC Switch', 'He3 UC Switch']],
             [['HEX', 'mainplate']],
             [['PTC 4K stage'], ['PTC 50K stage']],
             [['UC Head', 'IC Head', 'UC stage']],
             [['4K shield near harness', 'SQUID 6', 'SQUID 7']],
             [['cold load center', 'cold load side', 'blackbody']]]

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
dt_update = 2  # sec changed to 1 sec for RT

base_path = os.path.dirname(os.path.abspath(__file__))

# file name
if os.path.isfile(args.logfile) == True:
    print args.logfile + ' already exists. Attempting to append data to end of file. If thermometer names differ in the existing file, this may fail.'
    pytables_mode = 'a'
else:
    print 'Attempting to create data file ' + args.logfile
    pytables_mode = 'w'

# create output file
f_h5 = tables.open_file(args.logfile, mode=pytables_mode, title='fridge data') # append file, by default
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

# create output directory for plots, if it does not already exist
plot_dirname = os.path.join(base_path, '../website/img/')
if not os.path.exists(plot_dirname):
    os.mkdir(plot_dirname)
            
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
        time.sleep(0.1)

        # read the responses for serial interfaces
        for interface_name in serial_interfaces:
            raw_output = serial_interfaces[interface_name].read(serial_interfaces[interface_name].inWaiting())

            # check that we actually got a response with data in it (occasionally the MOXA
            # is non-responsive), otherwise do nothing
            if len(raw_output.split(',')) > 0:
                for jValue in range(len(channel_map[interface_name])):
                    channel_name = channel_map[interface_name][jValue]
                    tables_list[channel_name].row['time'] = current_time
                    tables_list[channel_name].row[channel_name] = float(raw_output.split(',')[jValue])
                    tables_list[channel_name].row.append()
                    tables_list[channel_name].flush()

        # for the TCP interfaces, also get the raw sensor values and substitute these
        # in for the temperature if the temperature reads exactly zero
        raw_output_temp = dict()
        raw_output_resist = dict()
        for interface_address in tcp_interfaces:
            raw_output_temp[interface_address], _ = tcp_interfaces[interface_address].recvfrom(2048)
        for interface_address in tcp_interfaces:
            tcp_interfaces[interface_address].sendto('SRDG? 0\r\n', (interface_address, 7777))
        time.sleep(0.1)
        for interface_address in tcp_interfaces:
            raw_output_resist[interface_address], _ = tcp_interfaces[interface_address].recvfrom(2048)
        for interface_address in tcp_interfaces:
            for jValue in range(len(channel_map[interface_address])):
                channel_name = channel_map[interface_address][jValue]
                tables_list[channel_name].row['time'] = current_time
                if float(raw_output_temp[interface_address].split(',')[jValue]) == 0.0:
                    tables_list[channel_name].row[channel_name] = float(raw_output_resist[interface_address].split(',')[jValue])
                else:
                    tables_list[channel_name].row[channel_name] = float(raw_output_temp[interface_address].split(',')[jValue])
                tables_list[channel_name].row.append()
                tables_list[channel_name].flush()


        # update the plots
        plotter.update_plot(base_path + '/../website/img/temperature_plot.png' ,tables_list, plot_list)
        plotter.write_table(base_path + '/../website/datatable.html', tables_list, plot_list)

        # make a copy of the data file; useful for other processes that need
        # access to the latest data since we cannot do simultaneous read/write
        # of pytables files
        shutil.copyfile(args.logfile, args.logfile + str('.lock'))
        shutil.move(args.logfile + str('.lock'), args.logfile.strip('.h5') + '_read.h5')

        # wait before reading again
        time.sleep(dt_update)

except KeyboardInterrupt:
    print "\nStopping data acquisition"

# close the connections
for interface_address in serial_interface_address:
    serial_interfaces[interface_address].close()
for interface_address in tcp_interface_address:
    tcp_interfaces[interface_address].close()
