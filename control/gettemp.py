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

def gettemp(datafile_path):
    last_entry = []

    # open pytables file
    datafile = tables.open_file(datafile_path, 'r')
    datatable = datafile.root.data.LS_218_1
    for colname in datatable.colnames:
        if colname == "record time":
            # time data is stored as a UNIX timestamp, and we need to convert
            # this into a Python datetime object
            time = datetime.fromtimestamp([row[colname] for row in datatable.iterrows(start=datatable.nrows-1, stop=datatable.nrows)])
            last_entry.append(time)
        else:
            last_entry.append([row[colname] for row in datatable.iterrows(start=datatable.nrows-1, stop=datatable.nrows)])

    return last_entry
