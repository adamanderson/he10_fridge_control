# gettemp.py
#
# A script for reading temperatures from the log files produced by the fridge
# logger. This is a rewrite of Alex Diaz's original code, which has been
# modified to read from the new hdf5 storage for the log files.
#
# Adam Anderson
# adama@fnal.gov
# 21 September 2015

import tables
import datetime

def gettemp(datafile_path, sensor_name):
    # open pytables file
    datafile = tables.open_file(datafile_path, 'r')
    datatable = datafile.get_node('/data/' + sensor_name.replace(' ', '_'))

    # get the latest temperature from the data file
    sensor_value = [row[sensor_name] for row in datatable.iterrows(start=datatable.nrows-1, stop=datatable.nrows)][0]

    datafile.close()

    return sensor_value
