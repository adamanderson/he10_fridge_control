# testRofT.py
#
# A quick script for testing some tools useful for taking and analyzing R(T)
# data.
#
# Adam Anderson
# adama@fnal.gov

import bolotools as bt
import datetime as dt
import time
import matplotlib.pyplot as plt

starttime = time.mktime(dt.datetime(2015, 12, 28, 11, 10, 55).timetuple())
stoptime = time.mktime(dt.datetime(2015, 12, 28, 13, 1, 0).timetuple())
T_data = bt.get_T('/home/spt3g/he10_fridge_tools/production/he10_fridge_control/logger/run5_fridge_log.h5', 'backplate', starttime, stoptime)

data_keys = bt.get_keys_parser('/home/spt3g/parser_data/12_28_2015/RT')
bolo_keys = [key for key in data_keys if 'bolo' in key and '_i' in key and int(key.split('_')[6][1:]) == 6]
R_data = bt.get_R_parser('/home/spt3g/parser_data/12_28_2015/RT', len(T_data), bolo_list=bolo_keys)

# the parser data contains data from a period when the temperature was rising and another period when the temperature was falling; let's split this into two chunks
R_data_cooling = dict()
R_data_heating = dict()
for key in R_data:
    R_data_cooling[key] = R_data[key][:850]
    R_data_heating[key] = R_data[key][850:]
    T_data_cooling = T_data[:850]
    T_data_heating = T_data[850:]

bt.plot_RofT(T_data_cooling, R_data_cooling, 'testplot_cooling.png')
bt.plot_RofT(T_data_heating, R_data_heating, 'testplot_heating.png')

for key in R_data_cooling:
    plt.figure()
    plt.subplot(2,1,1)
    plt.plot(R_data_cooling[key])
    plt.ylabel('R(t)')
    plt.subplot(2,1,2)
    plt.plot(T_data_cooling)
    plt.ylabel('T(t)')
