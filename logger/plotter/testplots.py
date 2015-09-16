#!/usr/bin/python 

import re 
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time
from pylab import * 
import datetime

ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

import matplotlib.dates as mdates

from datetime import datetime, date, time

f02 = open("../eth2-480.data","r")
lines02 = f02.readlines()
data02 = [[],[],[],[],[]]

for line in lines02:

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
#        data01.append([])
        data02[0].append(x)

      if iword == 7:    # UC Head
#        data01.append([])
        data02[1].append(float(word))
      if iword == 8:    # IC Head
#        data01.append([])
        data02[2].append(float(word))

      if iword == 9:   #  UC Stage
#        data01.append([])
        data02[3].append(float(word))
      if iword == 10:   #  IC Stage
#        data01.append([])
        data02[4].append(float(word))


f01 = open("../r01-480.data","r")
lines01 = f01.readlines()
data01 = [[],[],[],[],[],[]]

for line in lines01:

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
#        data01.append([])
        data01[0].append(x)

      if iword == 7:    # PTC 4 K stage
#        data01.append([])
        data01[1].append(float(word))
      if iword == 8:    # PTC 60 K stage
#        data01.append([])
        data01[2].append(float(word))

#  Get data for blackbody diodes    

      if iword == 11:   #  diode on side of Cu plate
#        data01.append([])
        data01[3].append(float(word))
      if iword == 12:   #  diode in center of Cu plate
#        data01.append([])
        data01[4].append(float(word))
      if iword == 13:   #  diode on black body
#        data01.append([])
        data01[5].append(float(word))


f00 = open("../r00-480.data","r")
lines00 = f00.readlines()
data00 =[[],[],[],[],[],[],[],[],[]]

for line in lines00:

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
#        data00.append([])
        data00[0].append(x)
      if iword == 7:    # HEX
#        data00.append([])
        data00[1].append(float(word))
      if iword == 8:    # Mainplate
#        data00.append([])
        data00[2].append(float(word))

#  Get data for blackbody diodes    
      if iword == 9:    #  4He IC Pump
#        data00.append([])
        data00[3].append(float(word))
      if iword == 10:   #  3He IC Pump
#        data00.append([])
        data00[4].append(float(word))
      if iword == 11:   #  3He UC Pump
#        data00.append([])
        data00[5].append(float(word))

      if iword == 12:   #  4He IC SW
#        data00.append([])
        data00[6].append(float(word))
      if iword == 13:   #  3He IC SW
#        data00.append([])
        data00[7].append(float(word))
      if iword == 14:   #  3He UC SW
#        data00.append([])
        data00[8].append(float(word))


#  Set labelsizes
matplotlib.rc('xtick', labelsize=8)
matplotlib.rc('ytick', labelsize=8)

plt.figure(1,figsize=(7,10))
#  Plot PTC stage 2 
ax1 = plt.subplot(611)
plt.title("Pumps and Switches", fontsize=10)
plt.plot(data00[0],data00[3],label='4He IC Pump')
plt.plot(data00[0],data00[4],label='3He IC Pump')
plt.plot(data00[0],data00[5],label='3He UC Pump')
plt.plot(data00[0],data00[6],label='4He IC Switch')
plt.plot(data00[0],data00[7],label='3He IC Switch')
plt.plot(data00[0],data00[8],label='3He UC Switch')
plt.ylabel('Temperature (K)',fontsize=10)
plt.xlabel('Last 2 Hours')
plt.legend(loc="upper left", prop={'size':7}, bbox_to_anchor=[1.0,1.0], borderpad=.2)


#  Plot PTC stage 1
ax2 = plt.subplot(612,sharex=ax1)
plt.title("Heat Exchanger and Mainplate", fontsize=10)
plt.ylabel('Tempaterature (K)',fontsize=10)
plt.plot(data00[0],data00[1],label='HEX')
plt.plot(data00[0],data00[2],label='Mainplate')

plt.legend(loc="upper left", prop={'size':8}, bbox_to_anchor=[1.0,1.0], borderpad=.2)



#  Plot PTC stage 1
ax3 = plt.subplot(613,sharex=ax1)
plt.title("4K State", fontsize=10)
plt.ylabel('Temperature (K)',fontsize=10)
plt.plot(data01[0],data01[1])

#  Plot PTC stage 2 
ax4 = plt.subplot(614,sharex=ax1)
plt.plot(data01[0],data01[2])
plt.title("60K Stage", fontsize=10)
plt.ylabel('Temperature (K)',fontsize=10)
plt.xlabel('Last 2 Hours')

#  Plot the three diodes on the coldload (side, center, blackbody)
ax5 = plt.subplot(615,sharex=ax1)
plt.plot(data01[0],data01[3], label="side")
plt.plot(data01[0],data01[4], label="center")
plt.plot(data01[0],data01[5], label="blackbody")
plt.title("Cold Load", fontsize=10)
plt.ylabel('Temperature (K)', fontsize=10)
plt.xlabel('Last 2 Hours')
#  Define legend for the coldload plot
plt.legend(loc="upper left", prop={'size':8}, bbox_to_anchor=[1.0,1.0], borderpad=0.1)

ax6 = plt.subplot(616,sharex=ax1)
plt.title("Head and Stage", fontsize=10)
plt.plot(data02[0],data02[1],label='UC Head')
plt.plot(data02[0],data02[2],label='IC Head')
plt.plot(data02[0],data02[3],label='UC Stage')
plt.plot(data02[0],data02[4],label='IC Stage')
plt.ylabel('Temperature (K)',fontsize=10)
plt.xlabel('Last 2 Hours')
plt.legend(loc="upper left", prop={'size':7}, bbox_to_anchor=[1.0,1.0], borderpad=.2)


#  Adjust the size of the plot areas
subplots_adjust(left=0.10, bottom=0.10, right=0.83, top=0.92, wspace=0.21, hspace=0.27) 

#  Setup the date format that will be shown on plot
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=20))
plt.gcf().autofmt_xdate(rotation=45)
 
plt.suptitle(st,fontsize=12)



#plt.show()
plt.savefig('testplots.png')

#  Close datafile
f00.close()
f01.close()

#  End of program
