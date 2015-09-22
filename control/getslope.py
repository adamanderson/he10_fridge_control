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

def getslope(datafile_path, dt):
    # open pytables file
    datafile = tables.open_file(datafile_path, 'r')
    datatable = datafile.root.data.LS_218_1
    maxtime = [row['record time'] for row in datatable.iterrows(start=datatable.nrows-1, stop=datatable.nrows)]
    HEX_temps = [row['HEX'] for row in datatable.iterrows() if row['record time'] > maxtime-dt]
    mainplate_temps = [row['mainplate'] for row in datatable.iterrows() if row['record time'] > maxtime-dt]

    HEX_slope = (HEX_temps[-1] - HEX_temps[0]) / dt
    mainplate_slope = (mainplate_temps[-1] - mainplate_temps[0]) / dt

    return HEX_slope, mainplate_slope
