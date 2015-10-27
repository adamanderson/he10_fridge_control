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

def update_plot(tables_list, plot_list):
    time_to_show = 3600 #[s]
    num_subplots = len(plot_list)

    f = plt.figure(1,figsize=(7,10))

    for jplot in range(len(plot_list)):
        # make one subplot per entry in plot_list
        ax = plt.subplot(num_subplots*100 + 10 + jplot+1)
        
        l1 = []
        l2 = []
        for var in plot_list[jplot][0]:
            maxtime = [row['time'] for row in tables_list[var].iterrows(start=tables_list[var].nrows-1, stop=tables_list[var].nrows)]
            time_1 = np.array([x['time'] for x in tables_list[var].iterrows() if x['time']>(maxtime[0]-time_to_show)])
            plottime_1 = [datetime.datetime.fromtimestamp(ts) for ts in time_1]
            coldata = np.array([x[var] for x in tables_list[var].iterrows() if x['time']>(maxtime[0]-time_to_show)])
            l1 = plt.plot(plottime_1, coldata, label=var)
            plt.ylabel('Temperature [K]',fontsize=10)
        # add another axis if indicated by plot_list argument
        if len(plot_list[jplot]) == 2:
            ax_twin = ax.twinx()
            for var in plot_list[jplot][1]:
                maxtime = [row['time'] for row in tables_list[var].iterrows(start=tables_list[var].nrows-1, stop=tables_list[var].nrows)]
                time_1 = np.array([x['time'] for x in tables_list[var].iterrows() if x['time']>(maxtime[0]-time_to_show)])
                plottime_1 = [datetime.datetime.fromtimestamp(ts) for ts in time_1]
                coldata = np.array([x[var] for x in tables_list[var].iterrows() if x['time']>(maxtime[0]-time_to_show)])
                l2 = plt.plot(plottime_1, coldata, label=var, linestyle='--')
        
                lns = l1+l2
                labs = [l.get_label() for l in lns]
                ax.legend(lns, labs, loc='upper left', prop={'size':7}, bbox_to_anchor=[1.1,1.0], borderpad=.2)
        else:
            plt.legend(loc='upper left', prop={'size':7}, bbox_to_anchor=[1.0,1.0], borderpad=.2)

        plt.autoscale()
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        if jplot+1 != len(plot_list):
            ax.get_xaxis().set_ticks([])

    plt.xlabel('time')
    plt.subplots_adjust(left=0.10, bottom=0.1, right=0.75, top=0.92, wspace=0.21, hspace=0.1)
    plt.savefig('figures/temperature_plot.png')
    plt.clf()
