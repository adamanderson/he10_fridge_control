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
import he10_fridge_control.control.agilent as PS
import time
import datetime
import numpy as np
import cPickle as pickle

# run-specific settings
overbias_amp = 0.025
drobbolos_step = overbias_amp / 1000.
setpoints = np.linspace(0.25, 0.550, 13)
output_filename = '%s_G_temp_data.pkl' % '{:%Y%m%d_%H%M%S}'.format(datetime.datetime.now())

# cryostat-specific settings
PID_channel = 'UC Head'
channel_of_interest = 'wafer holder'
ChaseLS = LS.Lakeshore350('192.168.0.12',  ['UC Head', 'IC Head', 'UC stage', 'LC shield'])
WaferLS = LS.Lakeshore350('192.168.2.5',  ['wafer holder', '3G IC head', '3G UC head', '3G 4He head'])
ChaseLS.config_output(1,1,ChaseLS.channel_names.index(PID_channel)+1)
PS1 = PS.Agilent3631A('/dev/ttyr02', '3He UC switch', '3He IC switch', '3He UC pump')
PS2 = PS.Agilent3631A('/dev/ttyr03', '4He IC switch', '3He IC pump', '4He IC pump')

# setup pydfmux stuff
hwm_file = '/home/spt3g/detector_testing/run14/hardware_maps/hwm_slot1/fermilab_hwm_complete.yaml'
y = pydfmux.load_session(open(hwm_file, 'r'))
bolos = y['hardware_map'].query(pydfmux.Bolometer)


waferstarttemps = np.zeros(len(setpoints))
measurestarttimes = np.zeros(len(setpoints))
waferstoptemps = np.zeros(len(setpoints))
measurestoptimes = np.zeros(len(setpoints))

# unlatch the switches
print('Turning off switches...')
PS1.set_voltage('3He UC switch', 0)   
PS1.set_voltage('3He IC switch', 0)     
time.sleep(300)

for jtemp in range(len(setpoints)):
    print setpoints[jtemp]
    print('Setting UC head to %f mK.' % (setpoints[jtemp]*1e3))

    ChaseLS.set_PID_temp(1, setpoints[jtemp])
    ChaseLS.set_heater_range(1, 2)
    time.sleep(10*60)

    # wait until the wafer holder temperature is stable up to 1mK;
    # give up after waiting 15 minutes
    recenttemps = [-4, -3, -2, -1]
    nAttempts = 0
    while np.abs(recenttemps[-1] - recenttemps[-4]) > 0.001 and \
          nAttempts < 45:
        time.sleep(20)
        recenttemps.append(WaferLS.get_temps()[channel_of_interest])
        nAttempts = nAttempts + 1
        if recenttemps[-1]>0 and recenttemps[-4]>0:
            print('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
            print('Wafer holder drifted %f mK.' % 1e3*np.abs(recenttemps[-1] - recenttemps[-4]))
    if nAttempts == 45:
        ChaseLS.set_heater_range(1, 0)
        sys.exit('UC Head failed to stabilize! Zeroed heater and quitting now.')

    waferstarttemps[jtemp] = WaferLS.get_temps()[channel_of_interest]
    measurestarttimes[jtemp] = time.time()
    print waferstarttemps

    drop_bolos_results = bolos.drop_bolos(A_STEP_SIZE=drobbolos_step, target_amplitude=0.75, fixed_stepsize=False, TOLERANCE=0.1)
    overbias_results = bolos.overbias_and_null(carrier_amplitude = overbias_amp)

    waferstoptemps[jtemp] = WaferLS.get_temps()[channel_of_interest]
    measurestoptimes[jtemp] = time.time()
    print waferstoptemps

    # save the data to a pickle file, rewriting after each acquisition
    f = file(output_filename, 'w')
    pickle.dump([waferstarttemps, measurestarttimes, waferstoptemps, measurestoptimes], f)
    f.close()

ChaseLS.set_heater_range(1, 0)

print waferstarttemps
print measurestarttimes
print waferstoptemps
print measurestoptimes
