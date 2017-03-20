
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

# run-specific settings
overbias_amp = 0.018
drobbolos_step = 0.00005
dropbolos_target = 0.9
dropbolos_tolerance = 0.02
heater_vals = np.array([0., 1., 2., 3., 4., 5., 6.])

# cryostat-specific settings
logfile = '/daq/fnal_temp_logs/run17_log_read.h5'
blackbody_channame = 'blackbody'
stage_channame = 'UC stage'
ChaseLS = LS.Lakeshore350('192.168.0.12',
                          ['UC Head', 'IC Head', 'channel C', 'channel D'])
WaferLS = LS.Lakeshore350('192.168.2.5',
                          ['UC stage', 'channel B', 'channel C', 'channel D'])
WaferLS.config_output(1,3,0)

# setup pydfmux stuff
hwm_file = '/home/adama/hardware_maps/fnal/run17/hwm_SPTpol_only/hwm.yaml'
y = pydfmux.load_session(open(hwm_file, 'r'))
hwm = y['hardware_map']
bolos = hwm.query(pydfmux.Bolometer)

# dict of housekeeping data
output_filename = '%s_net_housekeeping.pkl' % '{:%Y%m%d_%H%M%S}'
                  .format(datetime.datetime.now())
housekeeping = {'drop_bolos datadir': [],
                'noise datadir': [],
                'overbias datadir': [],
                '{} start temp'.format(blackbody_channame): [],
                '{} stop temp'.format(blackbody_channame): [],
                '{} start temp'.format(stage_channame): [],
                '{} stop temp'.format(stage_channame): [],
                'heater value': []}

for jpower in range(len(heater_vals)):
    print('Setting heater to %f.' % heater_vals[jpower])

    # turn on heater
    WaferLS.set_heater_range(1, 3)
    WaferLS.set_heater_output(1, heater_vals[jpower])

    # wait 1h for blackbody to stabilize
    time.sleep(3600)

    # once blackbody has stabilized, take noise
    housekeeping['heater value'].append(heater_vals[jpower])
    housekeeping['{} start temp'.format(stage_channame)]
        .append(gt.gettemp(logfile, stage_channame))
    housekeeping['{} start temp'.format(blackbody_channame)]
        .append(gt.gettemp(logfile, blackbody_channame))

    # check bolometer states and only drop overbiased bolos
    for bolo in hwm.query(pydfmux.Bolometer):
        if bolo.readout_channel:
            bolo.state = bolo.retrieve_bolo_state().state
        hwm.commit()
    bolos_to_drop = hwm.query(pydfmux.Bolometer)
                       .filter(pydfmux.Bolometer.state=='overbiased')
    drop_bolos_results = bolos_to_drop.drop_bolos(A_STEP_SIZE=dropbolos_step,
                                                  target_amplitude=dropbolos_target,
                                                  fixed_stepsize=False,
                                                  TOLERANCE=dropbolos_tolerance)
    
    # measure noise
    alive = bolos.find_alive_bolos()
    noise_results = alive.dump_info()
    
    # record final temperature
    housekeeping['{} stop temp'.format(stage_channame)]
        .append(gt.gettemp(logfile, stage_channame))
    housekeeping['{} stop temp'.format(blackbody_channame)]
        .append(gt.gettemp(logfile, blackbody_channame))

    # check bolometer states and only drop tuned bolos
    for bolo in hwm.query(pydfmux.Bolometer):
        if bolo.readout_channel:
            bolo.state = bolo.retrieve_bolo_state().state
        hwm.commit()
    bolos_to_overbias = hwm.query(pydfmux.Bolometer)
                           .filter(pydfmux.Bolometer.state=='tuned')
    overbias_results = bolos_to_overbias.overbias_and_null(carrier_amplitude=overbias_amp,
                                                           scale_by_frequency=True)

    # record data directories
    housekeeping['drop_bolos datadir']
        .append(drop_bolos_results[drop_bolos_results.keys()[0]]['output_directory'])
    housekeeping['noise datadir']
        .append(noise_results[noise_results.keys()[0]]['output_directory'])
    housekeeping['overbias datadir']
        .append(overbias_results[overbias_results.keys()[0]]['output_directory'])
    
    # save housekeeping data after each measurement to avoid losses
    f = file(output_filename, 'w')
    pickle.dump(housekeeping, f)
    f.close()

# turn off the heater as the last step
WaferLS.set_heater_range(1, 0)
