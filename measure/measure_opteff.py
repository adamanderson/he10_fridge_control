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
import he10_fridge_control.control.pid as pid
import time
import datetime
import numpy as np
import cPickle as pickle

# run-specific settings
overbias_amp = 0.018
dropbolos_step = 0.000025
dropbolos_tolerance = 0.02
coldload_temp_setpoints = [10, 12, 14, 16, 18, 20, 22, 24]

# cryostat-specific settings
logfile = '/daq/fnal_temp_logs/run17_log_read.h5'
blackbody_channame = 'blackbody'
coldload_channame = 'cold load center'
stage_channame = 'UC stage'
WaferLS = LS.Lakeshore350('192.168.2.5',
                          ['UC stage', 'channel B', 'channel C', 'channel D'])
WaferLS.set_heater_range(1, 3)
p = pid.PIDController('/daq/fnal_temp_logs/run17_log_read.h5', 'cold load center',
                      WaferLS, 1, 0.8, 0.01, 0.0, coldload_temp_setpoints[0])

# setup pydfmux stuff
hwm_file = '/home/adama/hardware_maps/fnal/run17/hwm_SPTpol_only/hwm.yaml'
y = pydfmux.load_session(open(hwm_file, 'r'))
hwm = y['hardware_map']
bolos = hwm.query(pydfmux.Bolometer)

# dict of housekeeping data
output_filename = '%s_opteff_housekeeping.pkl' % '{:%Y%m%d_%H%M%S}'.format(datetime.datetime.now())
housekeeping = {'drop_bolos datadir': [],
                'noise datadir': [],
                'overbias datadir': [],
                '{} start temp'.format(blackbody_channame): [],
                '{} stop temp'.format(blackbody_channame): [],
                '{} start temp'.format(stage_channame): [],
                '{} stop temp'.format(stage_channame): [],
                '{} start temp'.format(coldload_channame): [],
                '{} stop temp'.format(coldload_channame): []}

# Preheating stage
p.start_pid(0)

for jtemp in range(len(coldload_temp_setpoints)):
    print('Setting coldload to {} K.'.format(coldload_temp_setpoints[jtemp]))
    p.set_temp_setpoint(coldload_temp_setpoints[jtemp])
    
    # wait 1h for blackbody to stabilize
    if jtemp==0:
        time.sleep(1200)
    else:
        time.sleep(2400)

    # once blackbody has stabilized, take an IV curve then overbias
    housekeeping['{} start temp'.format(stage_channame)].append(gt.gettemp(logfile, stage_channame))
    housekeeping['{} start temp'.format(blackbody_channame)].append(gt.gettemp(logfile, blackbody_channame))
    housekeeping['{} start temp'.format(coldload_channame)].append(gt.gettemp(logfile, coldload_channame))
    
    # check bolometer states and only drop overbiased bolos
    for bolo in hwm.query(pydfmux.Bolometer):
        if bolo.readout_channel:
            bolo.state = bolo.retrieve_bolo_state().state
        hwm.commit()
    bolos_to_drop = hwm.query(pydfmux.Bolometer) \
                       .filter(pydfmux.Bolometer.state=='overbiased')
    drop_bolos_results = bolos_to_drop.drop_bolos(A_STEP_SIZE=dropbolos_step,
                                                  fixed_stepsize=False,
                                                  TOLERANCE=dropbolos_tolerance)

    # record final temperature
    housekeeping['{} stop temp'.format(stage_channame)].append(gt.gettemp(logfile, stage_channame))
    housekeeping['{} stop temp'.format(blackbody_channame)].append(gt.gettemp(logfile, blackbody_channame))
    housekeeping['{} stop temp'.format(coldload_channame)].append(gt.gettemp(logfile, coldload_channame))

    # measure noise at high setpoint
    alive = bolos.find_alive_bolos()
    noise_results = alive.dump_info()
    
    # check bolometer states and re-overbias
    for bolo in hwm.query(pydfmux.Bolometer):
        if bolo.readout_channel:
            bolo.state = bolo.retrieve_bolo_state().state
        hwm.commit()
    bolos_to_overbias = hwm.query(pydfmux.Bolometer) \
                           .filter(pydfmux.Bolometer.state=='tuned')
    overbias_results = bolos_to_overbias.overbias_and_null(carrier_amplitude=overbias_amp,
                                                           scale_by_frequency=True)

    # record data directories
    housekeeping['drop_bolos datadir'].append(drop_bolos_results['output_directory'])
    housekeeping['noise datadir'].append(noise_results[noise_results.keys()[0]]['output_directory'])
    housekeeping['overbias datadir'].append(overbias_results['output_directory'])
    
    # save housekeeping data after each measurement to avoid losses
    f = file(output_filename, 'w')
    pickle.dump(housekeeping, f)
    f.close()

# turn off the heater as the last step
WaferLS.set_heater_range(1, 0)
