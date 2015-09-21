# lakeshore350_record.py
#
# Python module with a class to represent a measurement from the Lakeshore 350
# device.
#
# Adam Anderson
# adama@fnal.gov
# 14 September 2015

import tables
import time

def write(row, col_keys, data_str):
    data_list_str = data_str.rstrip('\r\n').split(',')
    data_list = [float(data_str) for data_str in data_list_str]   # convert to floats

    # write time info
    row['record time'] = time.time()

    # write channel info
    for jChan in range(len(data_list)):
        row[col_keys[jChan+1]] = data_list[jChan]

    # append to the table
    row.append()
