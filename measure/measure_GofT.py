# measure_GofT.py
#
# Script for using PID control feature of Lakeshore 350 in order to automatically take G(T)
# measurements (Psat as a function of T). This script isn't totally cryostat-independent, 
# but it should be nearly so if you are using a heater close to your UC head to PID control
# the stage temperature, wait for a separate thermometry near the wafer to stabilize between
# measurements.
#
# Adam Anderson
# adama@fnal.gov
# 27 April 2016

import pydfmux
import he10_fridge_control.control.lakeshore as LS
import time
import datetime
import numpy as np
import cPickle as pickle

# cryostat-specific settings
setpoints = np.array([0.25, 0.275, 0.300, 0.325, 0.350, 0.375, 0.400, 0.425, 0.450, 0.475, 0.500])
PID_channel = 'UC Head'
channel_of_interest = 'wafer holder'

ChaseLS = LS.Lakeshore350('192.168.0.12',  ['UC Head', 'IC Head', 'UC stage', 'LC shield'])
WaferLS = LS.Lakeshore350('192.168.2.5',  ['wafer holder', '3G IC head', '3G UC head', '3G 4He head'])
ChaseLS.config_output(1,1,WaferLS.channel_names.index(channel_of_interest))

# setup pydfmux stuff
hwm_file = '/home/spt3g/detector_testing/run11/hardware_maps/hwm_wafer69_SPTpol/fermilab_hwm_complete.yaml'
y = pydfmux.load_session(open(hwm_file, 'r'))
ds = y['hardware_map'].query(pydfmux.Dfmux)
d = ds[0]
squidctrl = y['hardware_map'].query(pydfmux.SQUIDController)
squids = y['hardware_map'].query(pydfmux.SQUID)
rm = y['hardware_map'].query(pydfmux.ReadoutModule)
bolos = y['hardware_map'].query(pydfmux.Bolometer)

waferstarttemps = np.zeros(len(setpoints))
measurestarttimes = np.zeros(len(setpoints))
waferstoptemps = np.zeros(len(setpoints))
measurestoptimes = np.zeros(len(setpoints))

for jtemp in range(len(setpoints)):
    print setpoints[jtemp]
    print('Setting UC head to %f mK.' % (setpoints[jtemp]*1e3))

    ChaseLS.set_PID_temp(1, setpoints[jtemp])
    ChaseLS.set_heater_range(1, 2)
    time.sleep(5*60)

    # wait until the wafer holder temperature is stable up to 1mK;
    # give up after waiting 15 minutes
    recenttemps = [-4, -3, -2, -1]
    nAttempts = 0
    while np.abs(recenttemps[-1] - recenttemps[-4]) > 0.001 and \
          nAttempts < 45:
        time.sleep(20)
        print WaferLS.get_temps()
        recenttemps.append(WaferLS.get_temps()[channel_of_interest])
        nAttempts = nAttempts + 1
        print('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
        print('Wafer holder drifted %f mK.' % 1e3*np.abs(recenttemps[-1] - recenttemps[-4]))
    if nAttempts == 45:
        ChaseLS.set_heater_range(1, 0)
        sys.exit('UC Head failed to stabilize! Zeroed heater and quitting now.')

    waferstarttemps[jtemp] = WaferLS.get_temps()[channel_of_interest]
    measurestarttimes[jtemp] = time.time()
    print waferstarttemps

    drop_bolos_results = bolos.drop_bolos(A_STEP_SIZE=0.0003, fixed_stepsize=True, TOLERANCE=0.15)
    overbias_results = bolos.overbias_and_null(carrier_amplitude = 0.015)

    waferstoptemps[jtemp] = WaferLS.get_temps()[channel_of_interest]
    measurestoptimes[jtemp] = time.time()
    print waferstoptemps

    # save the data to a pickle file, rewriting after each acquisition
    f = file('G_temp_data.pkl', 'w')
    pickle.dump([waferstarttemps, measurestarttimes, waferstoptemps, measurestoptimes], f)
    f.close()

ChaseLS.set_heater_range(1, 0)

print waferstarttemps
print measurestarttimes
print waferstoptemps
print measurestoptimes
