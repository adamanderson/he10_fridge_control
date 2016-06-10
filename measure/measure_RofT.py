# measure_RofT.py
#
# A script for automating R(T) measurements.
# 
# Adam Anderson
# adama@fnal.gov
# 27 April 2016

import he10_fridge_control.control.lakeshore as LS
import he10_fridge_control.control.agilent as PS
import pydfmux
import time
import datetime
import numpy as np
import cPickle as pickle
import subprocess

# user params
PID_high_temp = 0.500
PID_low_temp = 0.250
wafer_high_temp = 0.450
wafer_low_temp = 0.300
K_per_sec = 2e-4
update_time = 10
overbias_amplitude = 0.0005
# parser_path = '/daq/pydfmux/firmware/mcgill/x86_64/parser'
ledgerman_path = '/daq/spt3g_software/dfmux/bin/ledgerman.py'
RT_data_path = '/daq/spt3g_software/dfmux/bin/test.nc' #'/home/spt3g/detector_testing/run12/RT_data/20160603_1008'
channel_of_interest = 'wafer holder'
PID_channel = 'UC Head'

ChaseLS = LS.Lakeshore350('192.168.0.12',  ['UC Head', 'IC Head', 'UC stage', 'LC shield'])
WaferLS = LS.Lakeshore350('192.168.2.5',  ['wafer holder', '3G IC head', '3G UC head', '3G 4He head'])
ChaseLS.config_output(1,1,ChaseLS.channel_names.index(PID_channel)+1)

PS1 = PS.Agilent3631A('/dev/ttyr02', '3He UC switch', '3He IC switch', '3He UC pump')
PS2 = PS.Agilent3631A('/dev/ttyr03', '4He IC switch', '3He IC pump', '4He IC pump')


# pydfmux stuff
hwm_file = '/home/spt3g/detector_testing/run12/hardware_maps/hwm_slots_457/fermilab_hwm_complete_1-10.yaml'
y = pydfmux.load_session(open(hwm_file, 'r'))
bolos = y['hardware_map'].query(pydfmux.Bolometer)
ds = y['hardware_map'].query(pydfmux.Dfmux)

# unlatch the switches
print('Turning off switches...')
PS1.set_voltage('3He UC switch', 0)   
PS1.set_voltage('3He IC switch', 0)     
time.sleep(300) # <<< MAKE THIS LONGER!


# warm up the fridge
print('Heating up fridge...')
warmup_temps = np.linspace(0.250, PID_high_temp, 20)
for set_temp in warmup_temps:
    print('Setting PID to %3.fmK'%(set_temp*1e3))
    ChaseLS.set_PID_temp(1, set_temp)
    ChaseLS.set_heater_range(1, 3)
    time.sleep(20)


# wait for wafer to warm up
while WaferLS.get_temps()[channel_of_interest] < wafer_high_temp:
    time.sleep(30)

# overbias bolometers
ds.clear_all()
ds.clear_dan()
overbias_results = bolos.overbias_and_null(carrier_amplitude = overbias_amplitude)


# start ledgerman
#proc_parser = subprocess.Popen([parser_path, '-d', RT_data_path])
proc_ledgerman = subprocess.Popen(['python', ledgerman_path, hwm_file, RT_data_path])
print datetime.datetime.now()


# latch the switches to help with cooldown
print('Turning on switches...')
PS1.set_voltage('3He UC switch', 5.0)   
PS1.set_voltage('3He IC switch', 5.0)
time.sleep(60)
print('Turning off switches...')
PS1.set_voltage('3He UC switch', 0.0)   
PS1.set_voltage('3He IC switch', 0.0) 
time.sleep(60)


# do the ramp-down
print('Starting ramp down...')
current_temp = PID_high_temp
while current_temp > PID_low_temp and WaferLS.get_temps()[channel_of_interest] > wafer_low_temp:
    time.sleep(update_time)
    current_temp = current_temp - (update_time * K_per_sec)
    ChaseLS.set_PID_temp(1, current_temp)
    print('Setting PID to %3.fmK'%(current_temp*1e3))
while WaferLS.get_temps()[channel_of_interest] > wafer_low_temp:
    time.sleep(30)


# do a ramp-up
print('Starting ramp up...')
while current_temp < PID_high_temp and WaferLS.get_temps()[channel_of_interest] < wafer_high_temp:
    time.sleep(update_time)
    current_temp = current_temp + (update_time * K_per_sec)
    ChaseLS.set_PID_temp(1, current_temp)
    print('Setting PID to %3.fmK'%(current_temp*1e3))

while WaferLS.get_temps()[channel_of_interest] < wafer_high_temp:
    time.sleep(30)

proc_ledgerman.terminate()
print datetime.datetime.now()
