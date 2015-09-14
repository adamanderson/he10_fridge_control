import time as sleeptime
import serial
import datetime
import re
from datetime import datetime, date, time

def gettemp():
    fo = open("../r00-480.data","r")
    lines = fo.readlines()[-1]
    TEMP = []


    iword = 0

    for word in re.split('[ ,]',lines):

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
            TEMP.append(x)
        if iword == 7:    # HEX
            TEMP.append(float(word))
        if iword == 8:    # Mainplate
            TEMP.append(float(word))
        if iword == 9:    # 4He IC Pump
            TEMP.append(float(word))
        if iword == 10:    # 3He IC Pump
            TEMP.append(float(word))
        if iword == 11:    # 3He UC Pump
            TEMP.append(float(word))
        if iword == 12:    # 4He IC Switch
            TEMP.append(float(word))
        if iword == 13:    # 3He IC Switch
            TEMP.append(float(word))
        if iword == 14:    # 3He UC Switch
            TEMP.append(float(word))
    return TEMP

