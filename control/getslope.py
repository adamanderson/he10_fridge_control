# getslope.py
#
# A script for reading temperature slopes from the log files produced by the
# fridgelogger. This is a rewrite of Alex Diaz's original code, which has been
# modified to read from the new hdf5 storage for the log files.
#
# Adam Anderson
# adama@fnal.gov
# 21 September 2015

import tables
import datetime

def getslope(datafile_path, sensor_name, dt):
    # open pytables file
    datafile = tables.open_file(datafile_path, 'r')
    datatable = datafile.get_node('/data/' + sensor_name.replace(' ', '_'))

    # get the latest temperature from the data file
    maxtime = [row['time'] for row in datatable.iterrows(start=datatable.nrows-1, stop=datatable.nrows)]
    sensor_value = [row[sensor_name] for row in datatable.iterrows() if row['time'] > (maxtime[0]-dt)]

    slope = (sensor_value[-1] - sensor_value[0]) / dt

    datafile.close()

    return slope
