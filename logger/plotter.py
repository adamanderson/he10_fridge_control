# plotter.py
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


def write_table(outfilename, tables_list, plot_list):
    '''
    Writes a file containing an html table with the latest data.

    Parameters:
    -----------
    outfilename : string
        Name of html file in which to write table.
    tables_list : dict
        Dictionary of PyTables tables from which to take data
    plot_list : list
        List of lists of string indicating variables from which to take data.

    Returns:
    --------
    (None)
    '''
    outfile = file(outfilename, 'w')
    outfile.write('<table border=1 width=500>\n')
    outfile.write('<tr><td><b>Sensor</b></td><td><b>Value</b></td></tr>\n')
    for jplot in range(len(plot_list)):
        # write one line in table for each thermometer
        varnames = [var for sublist in plot_list[jplot] for var in sublist]
        for var in varnames:
            maxtime = [row['time'] for row in tables_list[var].iterrows(start=tables_list[var].nrows-1, stop=tables_list[var].nrows)]
            currentvalue = [x[var] for x in tables_list[var].iterrows() if x['time']==maxtime[0]][0]
            outfile.write('<tr>\n<td>\n%s\n</td>\n<td>\n%.3f\n</td>\n</tr>\n' % (var, currentvalue)) # TODO: need to make distinction between Ohm and K here
    outfile.write('</table>')
    outfile.close()


def update_plot(outfilename, tables_list, plot_list):
    '''
    update_plot(tables_list, plot_list)

    Updates a png figure containing the fridge readout plots.

    Parameters:
    -----------
    outfilename:  filename (including path) to write the image to
    tables_list:  dictionary of PyTables tables, containing (possibly a superset of)
                  the data to plot
    plot_list:    list of lists of (1 or 2) lists of strings indicating the
                  variables to plot; names must match tables_list; use 1 or 2 lists
                  of strings for 1 or two separate y-axes with different scales
                  on the left and right sides of the subplot

    Returns:
    --------
    (None)
    '''
    time_to_show = 3600 #[s]
    num_subplots = len(plot_list)

    mpl.rc('xtick', labelsize=8)
    mpl.rc('ytick', labelsize=8)

    f = plt.figure(1,figsize=(7,12))

    for jplot in range(len(plot_list)):
        # make one subplot per entry in plot_list
        ax = plt.subplot(num_subplots*100 + 10 + jplot+1)

        lines = []
        for var in plot_list[jplot][0]:
            maxtime = [row['time'] for row in tables_list[var].iterrows(start=tables_list[var].nrows-1, stop=tables_list[var].nrows)]
            time_1 = np.array([x['time'] for x in tables_list[var].iterrows() if x['time']>(maxtime[0]-time_to_show)])
            plottime_1 = [datetime.datetime.fromtimestamp(ts) for ts in time_1]
            coldata = np.array([x[var] for x in tables_list[var].iterrows() if x['time']>(maxtime[0]-time_to_show)])
            l = plt.plot(plottime_1, coldata, label=var)
            lines = lines + l
            plt.ylabel('temp. [K]',fontsize=10)
        # add another axis if indicated by plot_list argument
        if len(plot_list[jplot]) == 2:
            plt.ylabel('temp. (solid) [K]',fontsize=10)
            ax_twin = ax.twinx()
            for var in plot_list[jplot][1]:
                maxtime = [row['time'] for row in tables_list[var].iterrows(start=tables_list[var].nrows-1, stop=tables_list[var].nrows)]
                time_1 = np.array([x['time'] for x in tables_list[var].iterrows() if x['time']>(maxtime[0]-time_to_show)])
                plottime_1 = [datetime.datetime.fromtimestamp(ts) for ts in time_1]
                coldata = np.array([x[var] for x in tables_list[var].iterrows() if x['time']>(maxtime[0]-time_to_show)])
                l = plt.plot(plottime_1, coldata, label=var, linestyle='--')
                lines = lines + l

            labs = [li.get_label() for li in lines]
            ax.legend(lines, labs, loc='upper left', prop={'size':7}, bbox_to_anchor=[1.1,1.0], borderpad=.2)
            plt.ylabel('temp. (dashed) [K]',fontsize=10)
        else:
            plt.legend(loc='upper left', prop={'size':7}, bbox_to_anchor=[1.0,1.0], borderpad=.2)

        plt.autoscale()
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        if jplot+1 != len(plot_list):
            ax.get_xaxis().set_ticks([])

    plt.xlabel('time')
    plt.subplots_adjust(left=0.10, bottom=0.1, right=0.75, top=0.92, wspace=0.21, hspace=0.1)
    plt.savefig(outfilename)
    plt.clf()
