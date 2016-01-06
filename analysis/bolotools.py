# bolotools.py
#
# A python module with functions that perform some basic measurements on
# bolometers in the Chase fridge at Fermilab. These are measurements like R(T)
# which require software from a variety of different packages as well as data
# from the fridge itself, and thus do not fit in the pydfmux or spt3g_software
# repos.
#
# Adam Anderson
# adama@fnal.gov
# 23 December 2015

import numpy as np
import matplotlib.pyplot as plt
import pydfmux
from spt3g import core, dfmux
from multiprocessing import Process
import os
import signal
import fridgetools
import iotools

def take_data(ip, hwm, out_filename, g3_filename, netcdf_filename=''):
    '''
    Simply takes data from an IceBoard. We have a separate function to do this
    because it is often useful to spawn the DAQ in a separate process so that
    the user can stop it on-demand by issuing SIGINT.
    
    Parameters
    ----------
    ip : string containing IP address of IceBoard from which to take data
    hwm : pydfmux hardware map ('hardware_map' field of output from
        'load_session'
    g3_filename : name of intermediate file in which to store data from IceBoard
    out_filename : name of pickle file in which to save final R(T) data
    netcdf_filename : (optional) name of netcdf file in which to write data;
        useful for displaying data in KST while doing R(T) measurement

    Returns
    -------
    [none]
    '''
    pipe = core.G3Pipeline()
    builder = dfmux.DfMuxBuilder(len(hwm.query(pydfmux.core.dfmux.IceBoard).all()))
    collector = dfmux.DfMuxCollector(ip, builder)
    pipe.Add(dfmux.PyDfMuxHardwareMapInjector, pydfmux_hwm=hwm)
    collector.Start()
    pipe.Add(builder)
    if netcdf_filename != '':
        pipe.Add(dfmux.NetCDFDump, filename=netcdf_filename)
    pipe.Add(core.G3Writer, filename=g3_filename)
    pipe.Run()


def measure_RofT(ip, hwm_filename, out_filename, g3_filename, netcdf_filename=''):
    '''
    Performs R(T) measurement. This proceeds assuming that you are already at
    base temperature with the bolometers overbiased, so this function simply
    calls the pydfmux drop_bolos method and starts the daq.
    
    Parameters
    ----------
    ip : string containing IP address of IceBoard from which to take data
    hwm_filename : name of hardware map file
    g3_filename : name of intermediate file in which to store data from IceBoard
    out_filename : name of pickle file in which to save final R(T) data
    netcdf_filename : (optional) name of netcdf file in which to write data;
        useful for displaying data in KST while doing R(T) measurement

    Returns
    -------
    [none]
    '''
    hwm = pydfmux.load_session(open(hwm_filename, 'r'))['hardware_map']

    # spawn DAQ as a separate process so that we can drop the bolos
    daq_pid = Process(target=take_data, args=(ip, hwm, out_filename, g3_filename, netcdf_filename))
    daq_process.start()
    bolos = hwm.query(pydfmux.core.dfmux.Bolometers)
    bolos.drop_bolos()

    # stop the daq when drop_bolos has finished
    os.kill(daq_pid, signal.SIGINT)

    # save the time here or somewhere above so that we can sync to the times
    # saved by the iceboard in case the 'TEST' timestamp is being used and is
    # saving the wrong time


def get_T(in_filename, T_varname, starttime, stoptime):
    '''
    Simple wrapper function to get temperature data, which just calls 'loadvar'
    in 'fridgetools'. Included only for transparency.

    Parameters
    ----------
    in_filename : path of pytables file containing temperature data
    T_varname : name of temperature variable to extract from pytables file
    starttime : starting time of data to extract (UNIX timestamp)
    dtime : interval of time for which to extract data (seconds)

    Returns
    -------
    T_data : vector of temperature data
    '''
    T_data, _ = fridgetools.load_var(in_filename, T_varname, starttime, stoptime)
    return T_data


def get_keys_parser(in_filename):
    '''
    Extracts the keys from a parser "GetData" file.

    Parameters
    ----------
    in_filename : full path to data file

    Returns
    -------
    key_list : Python list of keys to each data entry in file
    '''
    try:
        import pygetdata
    except:
        print('ERROR: Cannot load module \'pygetdata\', which is needed for reading binary files produced by parser.')

    dirfile = pygetdata.dirfile(name=in_filename)
    key_list = dirfile.entry_list()
    dirfile.close()
    return key_list


def get_R_parser(in_filename, nsamples, bolo_list=None):
    '''
    Extracts R data from the "GetData" format produced by the parser.

    Parameters
    ----------
    in_filename : name of input file; must be of either 3g or NetCDF type
    nsamples : "downsample" the R data on a uniform grid by interpolation 
    bolo_list (default=None, all bolos): list string identifying which bolos to
        save

    Returns
    -------
    R_data : python dictionary, indexed by detector name, containing another
        python dictionary with R and T data
    '''
    try:
        import pygetdata
    except:
        print('ERROR: Cannot load module \'pygetdata\', which is needed for reading binary files produced by parser.')
        
    # setup R data I/O
    R_data = dict()
    dirfile = pygetdata.dirfile(name=in_filename)
    if bolo_list == None:
        bolo_list = dirfile.entry_list()

    # downsample and save the data
    for key in bolo_list:
        bolo_data = dirfile.getdata(key)
        dirfile.raw_close()

        # check for missing data, skip, and issue a warning
        if len(bolo_data) > nsamples:
            print('Processing channel %s' % key)
            interp_points = np.floor(np.linspace(0, len(bolo_data)-1, nsamples))
            interp_grid = np.linspace(0, len(bolo_data)-1, len(bolo_data))
            R_data[key] = np.interp(interp_points, interp_grid, bolo_data)
        else:
            print('WARNING: Parser data for entry \'%s\' has fewer points than requested number of (downsampled) points. Skipping this channel.' % key)
    dirfile.close()
    return R_data


def plot_RofT(T_data, R_data, fig_filename, oneplot_flag=True):
    '''
    Makes plot(s) of data for R(T) by bolometer.

    Parameter
    ---------
    T_data : numpy array of temperature data
    R_data : python dictionary of numpy arrays, indexed by bolometer key, of 
        resistance data (or something proportional to it, in ADC units)
    fig_filename : string (for single plot) or dictionary of strings indexed by
        bolometer (for one plot per bolometer) with filename of plots to save
    oneplot_flag (default=True) : boolean flag to plot all data in a single
        figure

    Returns
    -------
    None
    '''
    f = plt.figure()
    for key in R_data.keys():
        plt.plot(T_data, R_data[key], label=key)

        if oneplot_flag == False:
            plt.title('R(T) for %s' % key)
            plt.xlabel('R(T) [ADC]')
            plt.ylabel('T [K]')
            f.savefig(fig_filename[key])
            f.clear()

    if oneplot_flag == True:
        #plt.legend()
        plt.ylabel('R(T) [ADC]')
        plt.xlabel('T [K]')
        f.savefig(fig_filename)
