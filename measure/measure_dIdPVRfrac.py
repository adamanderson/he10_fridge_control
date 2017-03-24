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
coldload_low_setpoint = 17
coldload_high_setpoint = 20
Rfrac_vals = [0.95, 0.9, 0.85, 0.8]

# cryostat-specific settings
logfile = '/daq/fnal_temp_logs/run17_log_read.h5'
blackbody_channame = 'blackbody'
coldload_channame = 'cold load center'
stage_channame = 'UC stage'
WaferLS = LS.Lakeshore350('192.168.2.5',
                          ['UC stage', 'channel B', 'channel C', 'channel D'])
WaferLS.set_heater_range(1, 3)
p = pid.PIDController('/daq/fnal_temp_logs/run17_log_read.h5', 'cold load center', WaferLS, 1, 0.8, 0.01, 0.0, coldload_low_setpoint)

# setup pydfmux stuff
hwm_file = '/home/adama/hardware_maps/fnal/run17/hwm_3G_only/hwm.yaml'
y = pydfmux.load_session(open(hwm_file, 'r'))
hwm = y['hardware_map']
bolos = hwm.query(pydfmux.Bolometer)

# dict of housekeeping data
output_filename = '%s_dIdPVRfrac_housekeeping.pkl' % '{:%Y%m%d_%H%M%S}' \
                  .format(datetime.datetime.now())
housekeeping = {'drop_bolos low-P datadir': [],
                'drop_bolos high-P datadir': [],
                'noise low-P datadir': [],
                'noise high-P datadir': [],
                'overbias datadir': [],
                '{} start temp'.format(blackbody_channame): [],
                '{} stop temp'.format(blackbody_channame): [],
                '{} start temp'.format(stage_channame): [],
                '{} stop temp'.format(stage_channame): [],
                '{} start temp'.format(coldload_channame): [],
                '{} stop temp'.format(coldload_channame): [],
                'Rfrac': []}

# Preheating stage
p.start_pid(0)

# wait 1h for blackbody to stabilize
time.sleep(3600)

for jR in range(len(Rfrac_vals)):
    print('Dropping to Rfrac={}'.format(Rfrac_vals[jR]))
    
    # drop into transition
    for bolo in hwm.query(pydfmux.Bolometer):
        if bolo.readout_channel:
            bolo.state = bolo.retrieve_bolo_state().state
        hwm.commit()
    bolos_to_drop = hwm.query(pydfmux.Bolometer) \
                       .filter(pydfmux.Bolometer.state=='overbiased')
    for b in bolos_to_drop.all():
        b.rfrac = Rfrac_vals[jR]
    drop_bolos_results_lowP = bolos_to_drop.drop_bolos(A_STEP_SIZE=dropbolos_step,
                                                       fixed_stepsize=False,
                                                       TOLERANCE=dropbolos_tolerance)
    
    # measure noise at low setpoint
    alive = bolos.find_alive_bolos()
    noise_results_lowP = alive.dump_info()
    
    # switch to high setpoint
    p.set_temp_setpoint(coldload_high_setpoint)

    # wait for blackbody to stabilize
    time.sleep(2400)

    # once blackbody has stabilized, take noise
    housekeeping['Rfrac'].append(Rfrac_vals[jR])
    housekeeping['{} start temp'.format(stage_channame)].append(gt.gettemp(logfile, stage_channame))
    housekeeping['{} start temp'.format(blackbody_channame)].append(gt.gettemp(logfile, blackbody_channame))
    housekeeping['{} start temp'.format(coldload_channame)].append(gt.gettemp(logfile, coldload_channame))
    
    # measure noise at high setpoint
    alive = bolos.find_alive_bolos()
    noise_results_highP = alive.dump_info()

    # re-overbias
    for bolo in hwm.query(pydfmux.Bolometer):
        if bolo.readout_channel:
            bolo.state = bolo.retrieve_bolo_state().state
        hwm.commit()
    bolos_to_overbias = hwm.query(pydfmux.Bolometer).filter(pydfmux.Bolometer.state=='tuned')
    overbias_results = bolos_to_overbias.overbias_and_null(carrier_amplitude=overbias_amp,
                                                           scale_by_frequency=True)    

    # drop into transition to measure loading at high setpoint
    for bolo in hwm.query(pydfmux.Bolometer):
        if bolo.readout_channel:
            bolo.state = bolo.retrieve_bolo_state().state
        hwm.commit()
    bolos_to_drop = hwm.query(pydfmux.Bolometer) \
                       .filter(pydfmux.Bolometer.state=='overbiased')
    for b in bolos_to_drop.all():
        b.rfrac = Rfrac_vals[jR]
    drop_bolos_results_highP = bolos_to_drop.drop_bolos(A_STEP_SIZE=dropbolos_step,
                                                  fixed_stepsize=False,
                                                  TOLERANCE=dropbolos_tolerance)

    # re-overbias while switching to low setpoint
    for bolo in hwm.query(pydfmux.Bolometer):
        if bolo.readout_channel:
            bolo.state = bolo.retrieve_bolo_state().state
        hwm.commit()
    bolos_to_overbias = hwm.query(pydfmux.Bolometer).filter(pydfmux.Bolometer.state=='tuned')
    overbias_results = bolos_to_overbias.overbias_and_null(carrier_amplitude=overbias_amp,
                                                           scale_by_frequency=True)
    
    # reduce to low setpoint
    p.set_temp_setpoint(coldload_low_setpoint)

    # wait for blackbody to stabilize
    time.sleep(2400)

    # record final temperature
    housekeeping['{} stop temp'.format(stage_channame)].append(gt.gettemp(logfile, stage_channame))
    housekeeping['{} stop temp'.format(blackbody_channame)].append(gt.gettemp(logfile, blackbody_channame))
    housekeeping['{} stop temp'.format(coldload_channame)].append(gt.gettemp(logfile, coldload_channame))

    # record data directories
    housekeeping['drop_bolos low-P datadir'].append(drop_bolos_results_lowP['output_directory'])
    housekeeping['drop_bolos high-P datadir'].append(drop_bolos_results_highP['output_directory'])
    housekeeping['noise low-P datadir'].append(noise_results_lowP[noise_results_lowP.keys()[0]]['output_directory'])
    housekeeping['noise high-P datadir'].append(noise_results_highP[noise_results_highP.keys()[0]]['output_directory'])
    housekeeping['overbias datadir'].append(overbias_results['output_directory'])
    
    # save housekeeping data after each measurement to avoid losses
    f = file(output_filename, 'w')
    pickle.dump(housekeeping, f)
    f.close()

# turn off the heater as the last step
p.stop_pid()
