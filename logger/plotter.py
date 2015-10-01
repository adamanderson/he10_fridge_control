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
import datetime
import numpy as np

def update_plot(table_LS_218_1, table_LS_218_2, table_LS_350_1, table_LS_350_2):
    time_to_show = 3600 # [s]

    # extract data from table
    maxtime = [row['record time'] for row in table_LS_218_1.iterrows(start=table_LS_218_1.nrows-1, stop=table_LS_218_1.nrows)]
    time_1 = np.array([x['record time'] for x in table_LS_218_1.iterrows() if x['record time']>(maxtime[0]-time_to_show)])
    plottime_1 = [datetime.datetime.fromtimestamp(ts) for ts in time_1]
    data_LS_218_1 = dict()
    for col in table_LS_218_1.colnames:
        coldata = np.array([x[col] for x in table_LS_218_1.iterrows() if x['record time']>(maxtime[0]-time_to_show)])
        data_LS_218_1[col] = coldata

    time_2 = np.array([x['record time'] for x in table_LS_218_2.iterrows() if x['record time']>(maxtime[0]-time_to_show)])
    plottime_2 = [datetime.datetime.fromtimestamp(ts) for ts in time_2]
    data_LS_218_2 = dict()
    for col in table_LS_218_2.colnames:
        coldata = np.array([x[col] for x in table_LS_218_2.iterrows() if x['record time']>(maxtime[0]-time_to_show)])
        data_LS_218_2[col] = coldata

    time_350_1 = np.array([x['record time'] for x in table_LS_350_1.iterrows() if x['record time']>(maxtime[0]-time_to_show)])
    plottime_350_1 = [datetime.datetime.fromtimestamp(ts) for ts in time_350_1]
    data_LS_350_1 = dict()
    for col in table_LS_350_1.colnames:
        coldata = np.array([x[col] for x in table_LS_350_1.iterrows() if x['record time']>(maxtime[0]-time_to_show)])
        data_LS_350_1[col] = coldata

    time_350_2 = np.array([x['record time'] for x in table_LS_350_2.iterrows() if x['record time']>(maxtime[0]-time_to_show)])
    plottime_350_2 = [datetime.datetime.fromtimestamp(ts) for ts in time_350_2]
    data_LS_350_2 = dict()
    for col in table_LS_350_2.colnames:
        coldata = np.array([x[col] for x in table_LS_350_2.iterrows() if x['record time']>(maxtime[0]-time_to_show)])
        data_LS_350_2[col] = coldata


    # do the plotting
    #  Set labelsizes
    mpl.rc('xtick', labelsize=8)
    mpl.rc('ytick', labelsize=8)


    f = plt.figure(1,figsize=(7,10))
    ax1 = plt.subplot(511)
    ax1_twin = ax1.twinx()
    lns = []
    for col in table_LS_218_1.colnames:
        if 'Pump' in col:
            plt.sca(ax1)
            lns = lns + plt.plot(plottime_1, data_LS_218_1[col], label=col)
        if 'Switch' in col:
            plt.sca(ax1_twin)
            lns = lns + plt.plot(plottime_1, data_LS_218_1[col], label=col, linestyle='--')
    plt.sca(ax1)
    plt.ylabel('Pump Temp. [K]',fontsize=10)
    plt.xlabel('Time')
    plt.sca(ax1_twin)
    plt.ylabel('Switch Temp. [K]',fontsize=10)
    labs = [l.get_label() for l in lns]
    plt.legend(lns, labs, loc="upper left", prop={'size':7}, bbox_to_anchor=[1.1,1.0], borderpad=.2)
    plt.autoscale()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))


    ax2 = plt.subplot(512)
    plt.ylabel('Temperature [K]',fontsize=10)
    plt.plot(plottime_1, data_LS_218_1['HEX'], label='HEX')
    plt.plot(plottime_1, data_LS_218_1['mainplate'], label='mainplate')
    plt.legend(loc='upper left', prop={'size':7}, bbox_to_anchor=[1.0,1.0], borderpad=.2)
    plt.autoscale()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))


    ax3 = plt.subplot(513)
    l1 = plt.plot(plottime_2, data_LS_218_2['PTC 4K stage'], label='PTC 4K stage')
    plt.autoscale()
    plt.ylabel('4K Stage Temp. [K]',fontsize=10)
    ax3_1 = ax3.twinx()
    l2 = plt.plot(plottime_2, data_LS_218_2['PTC 50K stage'], label='PTC 50K stage', color='r')
    plt.ylabel('50K Stage Temp. [K]',fontsize=10)
    # for tl in ax3_1.get_yticklabels():
    #     tl.set_color('r')
    lns = l1 + l2
    labs = [l.get_label() for l in lns]
    ax3.legend(lns, labs, loc='upper left', prop={'size':7}, bbox_to_anchor=[1.1,1.0], borderpad=.2)
    plt.autoscale()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))


    ax4 = plt.subplot(514)
    for col in table_LS_350_1.colnames:
        if col != 'record time':
            plt.plot(plottime_350_1, data_LS_350_1[col], label=col)
        plt.plot(plottimes_350_2, data_LS_350_2['backplate'], label='backplate')
    plt.ylabel('Temperature [K]',fontsize=10)
    plt.xlabel('Time')
    plt.legend(loc="upper left", prop={'size':7}, bbox_to_anchor=[1.0,1.0], borderpad=.2)
    plt.autoscale()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))


    ax5 = plt.subplot(515)
    plt.plot(plottime_350_1, data_LS_218_2['wiring harness'], label='wiring harness')
    plt.plot(plottime_350_1, data_LS_218_2['4K shield near harness'], label='4K shield near harness')
    plt.plot(plottime_350_1, data_LS_218_2['3G SQUIDs'], label='3G SQUIDs')
    plt.plot(plottime_350_1, data_LS_218_2['SZ SQUIDs'], label='SZ SQUIDs')
    plt.ylabel('Temperature [K]',fontsize=10)
    plt.xlabel('Time')
    plt.legend(loc="upper left", prop={'size':7}, bbox_to_anchor=[1.0,1.0], borderpad=.2)
    plt.autoscale()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    #  Adjust the size of the plot areas
    plt.subplots_adjust(left=0.10, bottom=0.1, right=0.75, top=0.92, wspace=0.21, hspace=0.1)

    plt.savefig('plotter/figures/temperature_plot.png')
    plt.clf()
