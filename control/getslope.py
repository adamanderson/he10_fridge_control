import time as sleeptime
import serial
import datetime
import re
from datetime import datetime, date, time



def getslope(number):
    fo = open("../r00-480.data","r")
    lines = fo.readlines()
    data = []
    HEXslopes=[]
    mainslopes=[]

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
          if iword == 7:    # HEX
            data.append([])
            data[1].append(float(word))
          if iword == 8:    # Mainplate
            data.append([])
            data[2].append(float(word))
    for i in range(len(data[0])-number,len(data[0])):
        HEXdiff= data[1][i]-data[1][i-1]
        maindiff= data[2][i]-data[2][i-1]
        timediff=(data[0][i]-data[0][i-1]).seconds
        HEXslopes.append(HEXdiff/timediff)
        mainslopes.append(maindiff/timediff)

    return HEXslopes, mainslopes

