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
heater_vals = np.array([0.0, 0.7, 1.4, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0])
logfile = '/home/spt3g/he10_fridge_tools/production/he10_fridge_control/logger/data/run14_log_read.h5'
blackbody_channame = 'blackbody'

ChaseLS = LS.Lakeshore350('192.168.0.12',  ['UC Head', 'IC Head', 'UC stage', 'LC shield'])
WaferLS = LS.Lakeshore350('192.168.2.5',  ['wafer holder', '3G IC head', '3G UC head', '3G 4He head'])
WaferLS.config_output(1,3,0)

# setup pydfmux stuff
hwm_file = '/home/adama/hardware_maps/fnal/run17/hwm.yaml'
y = pydfmux.load_session(open(hwm_file, 'r'))
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

    # once blackbody has stabilized, take an IV curve then overbias
    housekeeping['heaterval'].append(heater_vals[jpower])
    housekeeping['stagetemp'].append(gt.gettemp(logfile, 'wafer holder'))
    housekeeping['starttemp'].append(gt.gettemp(logfile, blackbody_channame))
    housekeeping['starttime'].append(datetime.datetime.now())

    # check bolometer states and only drop overbiased bolos
    for bolo in hwm.query(pydfmux.Bolometer):
        if bolo.readout_channel:
            bolo.state = bolo.retrieve_bolo_state().state
        hwm.commit()
    bolos_to_drop = hwm.query(pydfmux.Bolometer).filter(pydfmux.Bolometer.state=='overbiased')
    drop_bolos_results = bolos_to_drop.drop_bolos(A_STEP_SIZE=0.00002, target_amplitude=0.75, fixed_stepsize=False, TOLERANCE=0.05)

    # record final temperature
    housekeeping['stoptemp'].append(gt.gettemp(logfile, blackbody_channame))

    # check bolometer states and only drop tuned bolos
    for bolo in hwm.query(pydfmux.Bolometer):
        if bolo.readout_channel:
            bolo.state = bolo.retrieve_bolo_state().state
        hwm.commit()
    bolos_to_overbias = hwm.query(pydfmux.Bolometer).filter(pydfmux.Bolometer.state=='tuned')
    overbias_results = bolos_to_overbias.overbias_and_null(carrier_amplitude=0.015, scale_by_frequency=True)

    # save housekeeping data after each measurement to avoid losses
    f = file(output_filename, 'w')
    pickle.dump(housekeeping, f)
    f.close()

# turn off the heater as the last step
WaferLS.set_heater_range(1, 0)
