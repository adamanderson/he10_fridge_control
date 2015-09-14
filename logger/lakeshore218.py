# lakeshore218_record.py
#
# Python module with a class to represent a measurement from the Lakeshore 218
# device.
#
# Adam Anderson
# adama@fnal.gov
# 14 September 2015

import tables
import time

class record(tables.IsDescription):
    record_time = tables.Time32Col()
    chan0 = tables.Float32Col()
    chan1 = tables.Float32Col()
    chan2 = tables.Float32Col()
    chan3 = tables.Float32Col()
    chan4 = tables.Float32Col()
    chan5 = tables.Float32Col()
    chan6 = tables.Float32Col()
    chan7 = tables.Float32Col()

def write(record, data_str):
    data_list_str = data_str.rstrip('\r\n').split(',')
    data_list = [float(data_str) for data_str in data_list_str]   # convert to floats

    # write time info
    record['record_time'] = time.time()

    # write channel info
    for jChan in range(len(data_list)):
        record['chan' + str(jChan)] = data_list[jChan]

    # append to the table
    record.append()
