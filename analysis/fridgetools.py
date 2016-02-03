# fridgetools.py
#
# Some random tools for analyzing pytables/HDF5 files produced by the Fermilab
# Chase fridge data logger.
#
# Adam Anderson
# adama@fnal.gov
# 5 December 2015

import tables
import time
import datetime
import numpy as np

def load_var(filename, varname, starttime=0, stoptime=1e10):
    '''
    Loads time samples of selected variables present in a pytables/HDF5 file for
    a specific range of time.

    Parameters
    ----------
    filename : string with the full path and filename of the pytables/HDF5 file
    varname : string giving the variable name to load
    starttime : (optional) UNIX timestamp specifying the beginning of the time
        period for which data is requested (default = beginning of time)
    stoptime : (optional) UNIX timestamp specifying the beginning of the time
        period for which data is requested (default = end of time)

    Returns
    -------
    data : numpy array containing data
    times : numpy array containing the time corresponding to each datum

    NB: empty lists are returned for 'data' and 'times' if varname is not found
    in the input file.
    '''
    infile = tables.open_file(filename, 'r')

    data = []
    times = []

    for node in infile.list_nodes('/data/'):
        if node.title == varname:
            data = np.array([ row[node.title] for row in node.iterrows()
                                    if row['time']>starttime and row['time']<=stoptime ])
            times = np.array([ row['time'] for row in node.iterrows()
                                    if row['time']>starttime and row['time']<=stoptime ])
    infile.close()
    return data, times


def list_vars(filename):
    '''
    Lists variables available in a pytables/HDF5 file.

    Parameters
    ----------
    filename : string with the full path and filename of the pytables/HDF5 file

    Returns
    -------
    names : list of names of variables (i.e. columns) present in the file
    '''
    infile = tables.open_file(filename, 'r')
    names = [node.title for node in infile.list_nodes('/data/')]
    infile.close()
    return names


def timestamp2datetime(timestamp):
    '''
    Converts a UNIX timestamp that stores the time of each data sample into a
    python datetime object that allows easier access to year, month, day, etc.
    This is just 'datetime.datetime.fromtimestamp()'

    Parameters
    ----------
    timestamp : a UNIX timestamp (float)

    Returns
    -------
    dtime : corresponding datetime
    '''
    dtime = datetime.datetime.fromtimestamp(timestamp)
    return dtime

def datetime2timestamp(dtime):
    '''
    Converts a python datetime object to a UNIX timestamp. Useful for setting
    time boundaries in 'load_var'.

    Parameters
    ----------
    dtime : a python datetime object

    Returns
    -------
    unixtime : a UNIX timestamp (float)
    '''
    unixtime = time.mktime(dtime.timetuple())
    return unixtime
