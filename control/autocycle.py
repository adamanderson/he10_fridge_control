import time as sleeptime
import serial
import datetime
import re
from datetime import datetime, date, time
import gettemp
import getslope
import wx
# configure the serial connections (the parameters differs on the device you are connecting to)
ser2 = serial.Serial(
    port='/dev/ttyr02',
    baudrate=9600,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.SEVENBITS
)
ser3 = serial.Serial(
    port='/dev/ttyr03',
    baudrate=9600,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.SEVENBITS
)

#temp[0]=time, temp[1]=HEX, temp2]=Mainplate, temp[3]=4He IC Pump, temp[4]=3He IC Pump
#temp[5]=3He UC Pump, temp[6]=4He IC Switch, temp[7]= 3He IC Switch, temp[8]= 3He UC Switch



def autocycle(self, datafile_name):
  
    #Turning off the Pumps 
    self.logBox.AppendText( 'Turning the 4He IC Pump to 0 V \n')
    wx.Yield()
    ser3.write('APPL N25V, -0 \r\n') #turn on 4HE IC Pump
    sleeptime.sleep(2)
    self.logBox.AppendText( 'Turning on 3He IC Pump to 0V \n')
    wx.Yield()
    ser3.write('APPL P25V, 0 \r\n') #turn on 3He IC Pump
    sleeptime.sleep(2)
    self.logBox.AppendText( 'Turning on 3He UC Pump to -0V \n')
    wx.Yield()
    ser2.write('APPL N25V, -0 \r\n')#turn on 3He UC Pump
    sleeptime.sleep(2)

    #Turning off the Switches
    self.logBox.AppendText( 'Waiting for switches to cool below 8 K \n')

    sleeptime.sleep(2)
    self.logBox.AppendText( 'Turning off 4He IC Switch \n')
    wx.Yield()
    ser3.write('APPL P6V, 0 \r\n') #turns off 4He IC Switch
    sleeptime.sleep(2)
    self.logBox.AppendText( 'Turning off 3He IC Switch \n')
    wx.Yield()
    ser2.write('APPL P25V, 0 \r\n') #turns off 3HE IC Switch
    sleeptime.sleep(2)
    self.logBox.AppendText( 'Turning off 3He UC Switch \n')
    wx.Yield()
    ser2.write('APPL P6V, 0 \r\n') #turns off 3HE UC Switch
    sleeptime.sleep(2)

    while 1:
        sleeptime.sleep(2)
        if self.abortcycle:
            self.logBox.AppendText('ABORTING AUTOMATIC FRIDGE CYCLE \n')
            self.abortcycle =0
            self.canstartcycle =1
            return
        if gettemp.gettemp(datafile_name, 'He4 IC Switch') < 8 and \
            gettemp.gettemp(datafile_name, 'He3 IC Switch') < 13 and \
            gettemp.gettemp(datafile_name, 'He3 UC Switch') < 8:
            break

    #Heat 4HE IC pump first, then do other He3 pumps next
    self.logBox.AppendText( 'Turning on 4He IC Pump to -25 V \n')
    wx.Yield()
    ser3.write('APPL N25V, -25 \r\n') #turn on 4HE IC Pump
    sleeptime.sleep(2)
    
    while 1:
        sleeptime.sleep(2)
        wx.Yield()
        if self.abortcycle:
            self.logBox.AppendText('ABORTING AUTOMATIC FRIDGE CYCLE \n')
            self.abortcycle =0
            self.canstartcycle =1
            return
        if gettemp.gettemp(datafile_name, 'He4 IC Pump') > 33:
            sleeptime.sleep(2)
            self.logBox.AppendText( 'Lowering 4He IC Pump voltage to -4.5V \n')
            wx.Yield()
            ser3.write('APPL N25V, -4.5 \r\n')
            break 

    #Heat 3He pumps 
    self.logBox.AppendText( 'Turning on 3He IC Pump to 25V \n')
    wx.Yield()
    ser3.write('APPL P25V, 25 \r\n') #turn on 3He IC Pump
    sleeptime.sleep(2)
    self.logBox.AppendText( 'Turning on 3He UC Pump to -25V \n')
    wx.Yield()
    ser2.write('APPL N25V, -25 \r\n')#turn on 3He UC Pump
    sleeptime.sleep(2)
    if self.abortcycle:
        self.logBox.AppendText('ABORTING AUTOMATIC FRIDGE CYCLE \n')
        self.abortcycle =0
        self.canstartcycle =1
        return

    n=1
    m=1
    l=1
    #First three if statements check to see if pump temperatures have reached the desired point
    #Last if statement is True when all pump and switch temperatures have reached desired point
    while 1:
        if self.abortcycle:
            self.logBox.AppendText('ABORTING AUTOMATIC FRIDGE CYCLE \n')
            self.abortcycle =0
            self.canstartcycle =1
            return
        for i in range(20):
            sleeptime.sleep(1)
            wx.Yield()
        if n:
            if gettemp.gettemp(datafile_name, 'He4 IC Pump') > 33:
                sleeptime.sleep(2)
                self.logBox.AppendText( 'Lowering 4He IC Pump voltage to -4.5V \n')
                wx.Yield()
                ser3.write('APPL N25V, -4.5 \r\n')
                n=0
        if m:
            if gettemp.gettemp(datafile_name, 'He3 IC Pump')> 47:
                sleeptime.sleep(2)
                self.logBox.AppendText( 'Lowering 3He IC Pump voltage to 4.55V \n')
                wx.Yield()
                ser3.write('APPL P25V, 4.55 \r\n')
                m=0
        if l:
            if gettemp.gettemp(datafile_name, 'He3 UC Pump') > 47:
                sleeptime.sleep(2)
                self.logBox.AppendText( 'Lowering 3He UC Pump voltage to -6.72V \n')
                wx.Yield()
                ser2.write('APPL N25V, -6.72 \r\n')
                l=0
        if n==0 and m==0 and l==0 and \
            gettemp.gettemp(datafile_name, 'He4 IC Switch') < 8 and \
            gettemp.gettemp(datafile_name, 'He3 IC Switch') < 8 and \
            gettemp.gettemp(datafile_name, 'He3 UC Switch') < 8:
            break

    self.logBox.AppendText( 'Waiting for mainplate to settle \n')
    wx.Yield()

    #Checks to see if Mainplate has settled by checking the last 10 slopes in the datafile.
    #wait 10 minutes before checking
    sleeptime.sleep(600)

    while 1:
        if self.abortcycle:
           self.logBox.AppendText('ABORTING AUTOMATIC FRIDGE CYCLE \n')
           self.abortcycle =0
           self.canstartcycle =1
           return

        for i in range(60):
            sleeptime.sleep(1)
            wx.Yield()
        slope = getslope.getslope(datafile_name, 'mainplate', 60)
        if abs(slope) < 0.001:
            break

    self.logBox.AppendText( 'Mainplate has settled \n')
    wx.Yield()

    self.logBox.AppendText( 'turning off 4He IC pump and turning on switch \n')
    wx.Yield()
    ser3.write('APPL N25V, 0 \r\n')
    sleeptime.sleep(2)
    ser3.write('APPL P6V, 5 \r\n')
    self.logBox.AppendText( 'Waiting for heat exchanger to increase suddenly \n')
    wx.Yield()

    # This loop gets the 5 slopes corresponding to the last five lines in the data file
    # If all the 5 slopes are greater than a particular value, we take that as the HEX increasing
    #wait 10 minutes before checking
    sleeptime.sleep(600)

    while 1:
        if self.abortcycle:
            self.logBox.AppendText('ABORTING AUTOMATIC FRIDGE CYCLE \n')
            self.abortcycle =0
            self.canstartcycle =1
            return
        for i in range(60):
            sleeptime.sleep(1)
            wx.Yield()
        slope = getslope.getslope(datafile_name, 'HEX', 60)
        if slope > 0.003:
            break

    self.logBox.AppendText( 'HEX has started increasing \n')
    wx.Yield()
    self.logBox.AppendText( 'Now turning off 3He IC Pump and turning on switch \n')
    wx.Yield()
    sleeptime.sleep(2)
    ser3.write('APPL P25V, 0 \r\n')
    sleeptime.sleep(2)
    ser2.write('APPL P25V, 5 \r\n')
    self.logBox.AppendText( 'Waiting for heat exchanger and mainplate to settle \n')
    wx.Yield()

    #This loop gets the last 10 slope corresponding to the last ten lines in the data file
    #If all ten slopes for the HEX and mainplate are less than a certain distance from 0, we take that as them being constant.
    while 1:
        if self.abortcycle:
            self.logBox.AppendText('ABORTING AUTOMATIC FRIDGE CYCLE \n')
            self.abortcycle =0
            self.canstartcycle =1
            return
        for i in range(60):
            sleeptime.sleep(1)
            wx.Yield()
        mainplate_slope = getslope.getslope(datafile_name, 'mainplate', 60)
        if abs(mainplate_slope) < 0.001:
            break

    self.logBox.AppendText( 'Now turning off 3He UC Pump and turning on switch \n')
    wx.Yield()
    sleeptime.sleep(2)
    ser2.write('APPL N25V, 0 \r\n')
    sleeptime.sleep(2)
    ser2.write('APPL P6V, 5 \r\n')
    sleeptime.sleep(2)

    self.logBox.AppendText( 'Cycle is complete \n ')
    wx.Yield()
    return '\n'
