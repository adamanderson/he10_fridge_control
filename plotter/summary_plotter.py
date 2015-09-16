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
import matplotlib.dates as mdates
import tables
import numpy as np
import time
import datetime

ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

# open pytables file with data
data_file = tables.open_file('run1data.h5')
table_LS_218_1 = data_file.get_node('/data/LS_218_1')
table_LS_218_2 = data_file.get_node('/data/LS_218_2')
table_LS_350 = data_file.get_node('/data/LS_350')

# extract data from table
maxtime = [row['record time'] for row in table_LS_218_1.iterrows(start=table_LS_218_1.nrows-1, stop=table_LS_218_1.nrows)]
time_1 = np.array([x['record time'] for x in table_LS_218_1.iterrows() if x['record time']>(maxtime[0]-600)])
data_LS_218_1 = dict()
for col in table_LS_218_1.colnames:
    coldata = np.array([x[col] for x in table_LS_218_1.iterrows() if x['record time']>(maxtime[0]-600)])
    data_LS_218_1[col] = coldata

time_2 = np.array([x['record time'] for x in table_LS_218_2.iterrows() if x['record time']>(maxtime[0]-600)])
data_LS_218_2 = dict()
for col in table_LS_218_2.colnames:
    coldata = np.array([x[col] for x in table_LS_218_2.iterrows() if x['record time']>(maxtime[0]-600)])
    data_LS_218_2[col] = coldata

time_350 = np.array([x['record time'] for x in table_LS_350.iterrows() if x['record time']>(maxtime[0]-600)])
data_LS_350 = dict()
for col in table_LS_350.colnames:
    coldata = np.array([x[col] for x in table_LS_350.iterrows() if x['record time']>(maxtime[0]-600)])
    data_LS_350[col] = coldata

# should add some kind of "smart" partitioning of data between plots here,
# to avoid hardcoding...


# do the plotting
#  Set labelsizes
mpl.rc('xtick', labelsize=8)
mpl.rc('ytick', labelsize=8)

plt.figure(1,figsize=(7,10))
#  Plot PTC stage 2
ax1 = plt.subplot(611)
plt.title("Pumps and Switches", fontsize=10)
for col in table_LS_218_1.colnames:
    if 'Pump' in col or 'Switch' in col:
        plt.plot(time_1, data_LS_218_1[col], label=col)
plt.ylabel('Temperature [K]',fontsize=10)
plt.xlabel('Time')
plt.legend(loc="upper left", prop={'size':7}, bbox_to_anchor=[1.0,1.0], borderpad=.2)

#  Plot PTC stage 1
ax2 = plt.subplot(612,sharex=ax1)
plt.title("Heat Exchanger and Mainplate", fontsize=10)
plt.ylabel('Temperature [K]',fontsize=10)
plt.plot(time_1, data_LS_218_1['HEX'], label='HEX')
plt.plot(time_1, data_LS_218_1['mainplate'], label='mainplate')
plt.legend(loc="upper left", prop={'size':8}, bbox_to_anchor=[1.0,1.0], borderpad=.2)

ax6 = plt.subplot(616,sharex=ax1)
plt.title("Head and Stage", fontsize=10)
for col in table_LS_350.colnames:
    plt.plot(time_350, data_LS_350[col], label=col)
plt.ylabel('Temperature [K]',fontsize=10)
plt.xlabel('Time')
plt.legend(loc="upper left", prop={'size':7}, bbox_to_anchor=[1.0,1.0], borderpad=.2)


#  Adjust the size of the plot areas
plt.subplots_adjust(left=0.10, bottom=0.10, right=0.83, top=0.92, wspace=0.21, hspace=0.27)

#  Setup the date format that will be shown on plot
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=20))
plt.gcf().autofmt_xdate(rotation=45)

plt.suptitle(st,fontsize=12)



#plt.show()
plt.savefig('testplots.png')
