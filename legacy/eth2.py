#!/usr/bin/python

from pylab import *
import matplotlib.pyplot as plt
import time
from matplotlib import dates
import matplotlib.dates as mdates
from datetime import datetime
import fileinput
import shutil  # Needed to copy original datafile to working datafile
#import datetime

#  Get Lakeshore 350 data, copy to a working file, and remove + signs and commas from datafile
shutil.copy2('eth2-480.data','eth2-480-working-file.data')
for line in fileinput.FileInput("eth2-480-working-file.data",inplace=1):
	line = line.replace("+"," ")
	line = line.replace(","," ")
	print line,   # Trailing comma suppresses newline to prevent extra blank lines in new file
	# Note new versions of python will require pring(x, end=" ") appends a space instead of newline
		
#  Read Lakeshore 218 temperature data after + signs were removed
data = loadtxt('eth2-480-working-file.data')


#  Define array that will hold all the timestamps for all the timestamps, and call it timestamps[]
timestamps=[]

#  Read in the timestamp data - via a 'for' loop - looping though each line of data

#  Initialize index to start at 0
i=0
 
#  Start loop
for line in data:

	#  Read in each line of date, one by one
	year = data[i,0]
	month = data[i,1]
	day = data[i,2]
	hour = data[i,3]
	minute = data[i,4]
	second = data[i,5]

	#  Convert time & date into Python time & date format (time_data) and append to the timestamp array (timestamps[]) 
	time_data = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
	timestamps.append(time_data)	

	#  Check that the timestamps array is what you want		
#	print "timestamps = ", timestamps

	#  Increment index
	i=i+1

#  Get temperature data for all eight diodes
grt1 = data[:,6]
grt2 = data[:,7]
cernox1 = data[:,8]
cernox2 = data[:,9]

#  Clear any old plots
plt.clf()

#  Tick and Label
matplotlib.rc('xtick', labelsize=8)
matplotlib.rc('ytick', labelsize=8)

#  Setup plot for all 4 sensors
#plt.subplot(2,1,1)
plt.plot_date(timestamps, grt1, tz=None, xdate=True, ydate=False, fmt='b', label='UC head')
plt.plot_date(timestamps, grt2, tz=None, xdate=True, ydate=False, fmt='g', label='IC head')
plt.plot_date(timestamps, cernox1, tz=None, xdate=True, ydate=False, fmt='r', label='UC stage') 
plt.plot_date(timestamps, cernox2, tz=None, xdate=True, ydate=False, fmt='c', label='IC stage')

#  gca is a pyplot feature meaning get current axis; used this to format the timestamp labels on the plot
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
#  gcf is a plplot feature meaning get current figure; used this to make the labels more-easily read: set to 45 degrees
plt.gcf().autofmt_xdate(rotation=45)

#  Set plot and axes titles
plt.title("UC and IC head and stage temperatures", fontsize=10)
plt.ylabel("Temperature (K)", fontsize=8)

#  Tick and Label
matplotlib.rc('xtick', labelsize=8)
matplotlib.rc('ytick', labelsize=8)

#  Plot legend for first subplot (for Pumps and Switches)
plt.legend(loc="upper left", prop={'size':8}, bbox_to_anchor=[1.0,1.0], borderpad=2)

#  Setup second plot for Heat Exchanger and Mainplate
#plt.subplot(2,1,2)
#plt.plot_date(timestamps, diode1, tz=None, xdate=True, ydate=False, fmt='b', label='HEX')
#plt.plot_date(timestamps, diode2, tz=None, xdate=True, ydate=False, fmt='g', label='Mainplate')

#  gca is a pyplot feature meaning get current axis; used this to format the timestamp labels on the plot
#plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
#  gcf is a plplot feature meaning get current figure; used this to make the labels more-easily read: set to 45 degrees
#plt.gcf().autofmt_xdate(rotation=45)

#  Set plot and axes titles for second subplot 
#plt.title("Heat Exchanger and Mainplate", fontsize=10)
#plt.ylabel("Temperature (K)", fontsize=8)

#  Plot	legend for second subplot (for HEX and Mainplate)            
plt.legend(loc="upper left", prop={'size':8}, bbox_to_anchor=[1.0,1.0], borderpad=2)

#  Add current timestamp to top of plot
ts=time.time()
st = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
plt.suptitle(st, fontsize=12)

#  Adjust entire subplot formatting to make legend and axis labels fit 
subplots_adjust(left=0.12, bottom=0.17, right=0.78, top=0.90, wspace=0.2, hspace=0.2)

#  Display plot
#plt.show()

#  Save plot
plt.savefig('eth2.png')


