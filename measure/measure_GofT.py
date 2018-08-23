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
overbias_amp = 0.015
drobbolos_step = 0.00005
dropbolos_target = 0.9
dropbolos_tolerance = 0.02
setpoints = np.linspace(0.270, 0.410, 10)

# cryostat-specific settings
PID_channel = 'UC stage'
channel_of_interest = 'UC stage'
ChaseLS = LS.Lakeshore350('192.168.0.12',
                          ['UC Head', 'IC Head', 'UC stage', 'LC shield'])
ChaseLS.config_output(1,1,ChaseLS.channel_names.index(PID_channel)+1)
PS1 = PS.Agilent3631A('/dev/ttyr02',
                      '3He UC switch', '3He IC switch', '3He UC pump')
PS2 = PS.Agilent3631A('/dev/ttyr03',
                      '4He IC switch', '3He IC pump', '4He IC pump')

# setup pydfmux stuff
hwm_file = '/home/adama/hardware_maps/fnal/run31/hwm.yaml'
y = pydfmux.load_session(open(hwm_file, 'r'))
hwm = y['hardware_map']
bolos = hwm.query(pydfmux.Bolometer)

# dict of housekeeping data
output_filename = '%s_G_temp_data.pkl' % '{:%Y%m%d_%H%M%S}'.format(datetime.datetime.now())
housekeeping = {'drop_bolos datadir': [],
                'overbias datadir': [],
                '{} start temp'.format(channel_of_interest): [],
                '{} stop temp'.format(channel_of_interest): []}

# unlatch the switches
print('Turning off switches...')
PS1.set_voltage('3He UC switch', 0)   
PS1.set_voltage('3He IC switch', 0)     
time.sleep(600)

# take data at each temperature
for jtemp in range(len(setpoints)):
    print('Setting UC head to %f mK.' % (setpoints[jtemp]*1e3))
    ChaseLS.set_PID_temp(1, setpoints[jtemp])
    ChaseLS.set_heater_range(1, 3)
    time.sleep(10*60)

    # wait until the wafer holder temperature is stable up to 1mK;
    # give up after waiting 15 minutes
    recenttemps = [-4, -3, -2, -1]
    nAttempts = 0
    while np.abs(recenttemps[-1] - recenttemps[-4]) > 0.001 and \
          nAttempts < 45:
        time.sleep(20)
        recenttemps.append(ChaseLS.get_temps()[channel_of_interest])
        nAttempts = nAttempts + 1
        if recenttemps[-1]>0 and recenttemps[-4]>0:
            print('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
            print('Wafer holder drifted %f mK.' % 1e3*np.abs(recenttemps[-1] -
                                                             recenttemps[-4]))
    if nAttempts == 45:
        ChaseLS.set_heater_range(1, 0)
        sys.exit('UC Head failed to stabilize! Zeroed heater and quitting now.')

    # get housekeeping information before operating bolos 
    housekeeping['{} start temp'.format(channel_of_interest)].append(ChaseLS.get_temps()[channel_of_interest])

    # check bolometer states and only drop overbiased bolos
    for bolo in hwm.query(pydfmux.Bolometer):
        if bolo.readout_channel:
            bolo.state = bolo.retrieve_bolo_state().state
        hwm.commit()
    bolos_to_drop = hwm.query(pydfmux.Bolometer).filter(pydfmux.Bolometer.state=='overbiased')
    drop_bolos_results = bolos_to_drop.drop_bolos(A_STEP_SIZE=drobbolos_step,
                                                  fixed_stepsize=False,
                                                  TOLERANCE=dropbolos_tolerance)

    # get housekeeping information after operating bolos
    housekeeping['{} stop temp'.format(channel_of_interest)].append(ChaseLS.get_temps()[channel_of_interest]) 
    
    # check bolometer states and only drop tuned bolos
    for bolo in hwm.query(pydfmux.Bolometer):
        if bolo.readout_channel:
            bolo.state = bolo.retrieve_bolo_state().state
        hwm.commit()
    bolos_to_overbias = hwm.query(pydfmux.Bolometer).filter(pydfmux.Bolometer.state=='tuned')
    overbias_results = bolos_to_overbias.overbias_and_null(carrier_amplitude=overbias_amp,
                                                           scale_by_frequency=True)

    # record data directories
    housekeeping['drop_bolos datadir'].append(drop_bolos_results['output_directory'])
    housekeeping['overbias datadir'].append(overbias_results['output_directory'])
    
    # save the data to a pickle file, rewriting after each acquisition
    f = file(output_filename, 'w')
    pickle.dump(housekeeping, f)
    f.close()

ChaseLS.set_heater_range(1, 0)
