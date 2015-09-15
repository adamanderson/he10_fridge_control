# summary_plotter.py
#
# A modification of Alex Diaz's "testplots.py" to make a simple summary plot of
# all temperatures in the fridge, but reading data from the PyTables database
# file.
#
# Adam Anderson
# adama@fnal.gov
# 14 September 2015

import matplotlib as mpl
import matplotlib.pyplot as plt
import tables
import numpy as np

# open pytables file with data
data_file = tables.open_file('run1data.h5')
table_LS_218_1 = data_file.get_node('/data/LS_218_1')

# extract data from table
maxtime = [row['record_time'] for row in table_LS_218_1.iterrows(start=table_LS_218_1.nrows-1, stop=table_LS_218_1.nrows)]
chan0 = np.array([x['chan0'] for x in table_LS_218_1.iterrows() if x['record_time']>(maxtime[0]-600)])


# # do the plotting
# #  Set labelsizes
# matplotlib.rc('xtick', labelsize=8)
# matplotlib.rc('ytick', labelsize=8)
#
# plt.figure(1,figsize=(7,10))
# #  Plot PTC stage 2
# ax1 = plt.subplot(611)
# plt.title("Pumps and Switches", fontsize=10)
# plt.plot(data00[0],data00[3],label='4He IC Pump')
# plt.plot(data00[0],data00[4],label='3He IC Pump')
# plt.plot(data00[0],data00[5],label='3He UC Pump')
# plt.plot(data00[0],data00[6],label='4He IC Switch')
# plt.plot(data00[0],data00[7],label='3He IC Switch')
# plt.plot(data00[0],data00[8],label='3He UC Switch')
# plt.ylabel('Temperature (K)',fontsize=10)
# plt.xlabel('Last 2 Hours')
# plt.legend(loc="upper left", prop={'size':7}, bbox_to_anchor=[1.0,1.0], borderpad=.2)
#
#
# #  Plot PTC stage 1
# ax2 = plt.subplot(612,sharex=ax1)
# plt.title("Heat Exchanger and Mainplate", fontsize=10)
# plt.ylabel('Tempaterature (K)',fontsize=10)
# plt.plot(data00[0],data00[1],label='HEX')
# plt.plot(data00[0],data00[2],label='Mainplate')
#
# plt.legend(loc="upper left", prop={'size':8}, bbox_to_anchor=[1.0,1.0], borderpad=.2)
#
#
#
# #  Plot PTC stage 1
# ax3 = plt.subplot(613,sharex=ax1)
# plt.title("4K State", fontsize=10)
# plt.ylabel('Temperature (K)',fontsize=10)
# plt.plot(data01[0],data01[1])
#
# #  Plot PTC stage 2
# ax4 = plt.subplot(614,sharex=ax1)
# plt.plot(data01[0],data01[2])
# plt.title("60K Stage", fontsize=10)
# plt.ylabel('Temperature (K)',fontsize=10)
# plt.xlabel('Last 2 Hours')
#
# #  Plot the three diodes on the coldload (side, center, blackbody)
# ax5 = plt.subplot(615,sharex=ax1)
# plt.plot(data01[0],data01[3], label="side")
# plt.plot(data01[0],data01[4], label="center")
# plt.plot(data01[0],data01[5], label="blackbody")
# plt.title("Cold Load", fontsize=10)
# plt.ylabel('Temperature (K)', fontsize=10)
# plt.xlabel('Last 2 Hours')
# #  Define legend for the coldload plot
# plt.legend(loc="upper left", prop={'size':8}, bbox_to_anchor=[1.0,1.0], borderpad=0.1)
#
# ax6 = plt.subplot(616,sharex=ax1)
# plt.title("Head and Stage", fontsize=10)
# plt.plot(data02[0],data02[1],label='UC Head')
# plt.plot(data02[0],data02[2],label='IC Head')
# plt.plot(data02[0],data02[3],label='UC Stage')
# plt.plot(data02[0],data02[4],label='IC Stage')
# plt.ylabel('Temperature (K)',fontsize=10)
# plt.xlabel('Last 2 Hours')
# plt.legend(loc="upper left", prop={'size':7}, bbox_to_anchor=[1.0,1.0], borderpad=.2)
#
#
# #  Adjust the size of the plot areas
# subplots_adjust(left=0.10, bottom=0.10, right=0.83, top=0.92, wspace=0.21, hspace=0.27)
#
# #  Setup the date format that will be shown on plot
# plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
# plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=20))
# plt.gcf().autofmt_xdate(rotation=45)
#
# plt.suptitle(st,fontsize=12)
#
#
#
# #plt.show()
# plt.savefig('testplots.png')
