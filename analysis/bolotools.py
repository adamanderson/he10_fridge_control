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

    # analyze the R(T) data
    
