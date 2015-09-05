#!/usr/bin/python 

import re 
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time
from pylab import * 
import datetime

ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

import matplotlib.dates as mdates

from datetime import datetime, date, time


fo = open("r01-480.data","r")
lines = fo.readlines()
data = []

for line in lines:

   iword = 0

   for word in re.split('[ ,]',line):

      iword = iword + 1 

      if iword == 1:   # year
         year = int(word)

      if iword == 2:   # month
         month = int(word)

      if iword == 3:   # day
         day = int(word)

      if iword == 4:   # hour
        hour =  int(word)

      if iword == 5:   # minutes
        minute =  int(word)

      if iword == 6:  # seconds
        sec  = int(word)

        d = date(year,month,day)
        t = time(hour,minute,sec)
        x = datetime.combine(d,t)
        data.append([])
        data[0].append(x)

      if iword == 7:	# PTC 4 K stage
        data.append([])
	data[1].append(float(word))
      if iword == 8:	# PTC 60 K stage
        data.append([])
        data[2].append(float(word))

#  Get data for blackbody diodes	

      if iword == 11:	#  diode on side of Cu plate
        data.append([])
        data[3].append(float(word))
      if iword == 12:	#  diode in center of Cu plate
        data.append([])
        data[4].append(float(word))
      if iword == 13:	#  diode on black body
        data.append([])
        data[5].append(float(word))

#  Set labelsizes
matplotlib.rc('xtick', labelsize=8)
matplotlib.rc('ytick', labelsize=8)

#  Plot PTC stage 1
plt.subplot(311)
plt.title(st)
plt.ylabel('4K Stage (K)',fontsize=10)
plt.plot(data[0],data[1])

#  Plot PTC stage 2 
plt.subplot(312)
plt.plot(data[0],data[2])
plt.ylabel('60K Stage (K)',fontsize=10)
plt.xlabel('Last 2 Hours')

#  Plot the three diodes on the coldload (side, center, blackbody)
plt.subplot(313)
plt.plot(data[0],data[3], label="side")
plt.plot(data[0],data[4], label="center")
plt.plot(data[0],data[5], label="blackbody")
plt.ylabel('Cold load (K)', fontsize=10)
plt.xlabel('Last 2 Hours')

#  Define legend for the coldload plot
plt.legend(loc="upper left", prop={'size':8}, bbox_to_anchor=[1.0,1.0], borderpad=0.1)

#  Adjust the size of the plot areas
subplots_adjust(left=0.12, bottom=0.21, right=0.85, top=0.91, wspace=0.21, hspace=0.27) 

#  Setup the date format that will be shown on plot
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=10))
plt.gcf().autofmt_xdate(rotation=45)
 
#show()
plt.savefig('r01.png')

#  Close datafile
fo.close()

#  End of program
