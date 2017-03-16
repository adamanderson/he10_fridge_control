
# measure_opteff.py
#
# Script for measuring optical efficiency.
#
# Adam Anderson
# adama@fnal.gov
# 28 April 2016

import pydfmux
import he10_fridge_control.control.lakeshore as LS
import he10_fridge_control.control.gettemp as gt
import time
import datetime
import numpy as np
import cPickle as pickle

# cryostat-specific settings
heater_vals = np.array([0., 1., 2., 3., 4., 5., 6.])
logfile = '/daq/fnal_temp_logs/run17_log_read.h5'
blackbody_channame = 'blackbody'

ChaseLS = LS.Lakeshore350('192.168.0.12',  ['UC Head', 'IC Head', 'channel C', 'channel D'])
WaferLS = LS.Lakeshore350('192.168.2.5',  ['UC stage', 'channel B', 'channel C', 'channel D'])
WaferLS.config_output(1,3,0)

# setup pydfmux stuff
hwm_file = '/home/adama/hardware_maps/fnal/run17-0136/hwm.yaml'
y = pydfmux.load_session(open(hwm_file, 'r'))
hwm = y['hardware_map']
bolos = y['hardware_map'].query(pydfmux.Bolometer)

# dict of housekeeping data
output_filename = '%s_opteff_housekeeping.pkl' % '{:%Y%m%d_%H%M%S}'.format(datetime.datetime.now())
housekeeping = {'starttime': [],
                'starttemp': [],
                'stoptemp': [],
                'heaterval': [],
                'stagetemp': []}

for jpower in range(len(heater_vals)):
    print('Setting heater to %f.' % heater_vals[jpower])

    # turn on heater
    WaferLS.set_heater_range(1, 3)
    WaferLS.set_heater_output(1, heater_vals[jpower])

    # wait 1h for blackbody to stabilize
    time.sleep(3600)

    # once blackbody has stabilized, take noise
    housekeeping['heaterval'].append(heater_vals[jpower])
    housekeeping['stagetemp'].append(gt.gettemp(logfile, 'UC stage'))
    housekeeping['starttemp'].append(gt.gettemp(logfile, blackbody_channame))
    housekeeping['starttime'].append(datetime.datetime.now())

    # check bolometer states and only drop overbiased bolos
    for bolo in hwm.query(pydfmux.Bolometer):
        if bolo.readout_channel:
            bolo.state = bolo.retrieve_bolo_state().state
        hwm.commit()
    bolos_to_drop = hwm.query(pydfmux.Bolometer).filter(pydfmux.Bolometer.state=='overbiased')
    drop_bolos_results = bolos_to_drop.drop_bolos(A_STEP_SIZE=0.00006, target_amplitude=0.9, fixed_stepsize=False, TOLERANCE=0.02)
    
    # measure noise
    alive = bolos.find_alive_bolos()
    noise_results = alive.dump_info()
    
    # record final temperature
    housekeeping['datadir'].append(noise_results[noise_results.keys()[0]]['output_directory'])
    housekeeping['stoptemp'].append(gt.gettemp(logfile, blackbody_channame))

    # check bolometer states and only drop tuned bolos
    for bolo in hwm.query(pydfmux.Bolometer):
        if bolo.readout_channel:
            bolo.state = bolo.retrieve_bolo_state().state
        hwm.commit()
    bolos_to_overbias = hwm.query(pydfmux.Bolometer).filter(pydfmux.Bolometer.state=='tuned')
    overbias_results = bolos_to_overbias.overbias_and_null(carrier_amplitude=False,
                                                           scale_by_frequency=True,
                                                           maxnoise=200,
                                                           bias_power=True,
                                                           shorted_threshold=1.5,
                                                           max_resistance=6,
                                                           use_dan_gain=0.01)
            
    # save housekeeping data after each measurement to avoid losses
    f = file(output_filename, 'w')
    pickle.dump(housekeeping, f)
    f.close()

# turn off the heater as the last step
WaferLS.set_heater_range(1, 0)
