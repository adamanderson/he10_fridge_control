# autocycle.py
#
# Python module containing high-level functions for autocycling a 10He fridge.
# The core function 'run' in this module actually runs the cycle, and expects to
# interface with some wxPython objects in GUI.py. If you want to run a fridge
# cycle as a standalone script in a terminal, then run the module from the
# command line:
#   python autocycle.py logfile.h5
# where logfile.h5 is the data file produced by the fridge logger code in the
# 'logger' directory of this package.
#
# Adam Anderson
# adama@fnal.gov
# 16 March 2016: massive rewrite to make proper use of event handlers when
# communicating with the GUI, so that the GUI is now truly non-blocking instead
# of pseudo-non-blocking.

import time
import serial
import datetime
import re
from datetime import datetime, date, time
import gettemp
import getslope
import wx
import powersupply


def waitforkill(self, waittime, killevent):
    '''
    Waits for waittime and return True if kill flag is set, False otherwise.
    '''
    nSteps = int(waittime / 0.1)
    for jStep in range(nSteps):
        time.sleep(0.01) # our simulated calculation time
        if killevent.is_set() == True:
            return True
    return False


def run(datafile_name, parent, messageevent, killevent):
    # turn off all pumps and switches
    for name in powersupply.heaternames:
        set_voltage(name, 0.0)
        wx.PostEvent(parent, messageevent(message=('Setting %s to 0V.' % name)))

    while gettemp.gettemp(datafile_name, 'He4 IC Switch') < 8 and \
          gettemp.gettemp(datafile_name, 'He3 IC Switch') < 13 and \
          gettemp.gettemp(datafile_name, 'He3 UC Switch') < 8:
        if self.waitforkill(1, killevent): return

    #Heat 4HE IC pump first, then do other He3 pumps next
    wx.PostEvent(parent, messageevent(message='Turning on 4He IC Pump to -25 V.'))
    powersupply.set_voltage('4He IC pump', -25)
    if self.waitforkill(2, killevent): return

    while gettemp.gettemp(datafile_name, 'He4 IC Pump') > 33:
        if self.waitforkill(2, killevent): return

    wx.PostEvent(parent, messageevent(message='Lowering 4He IC Pump voltage to -4.5V.'))
    powersupply.set_voltage('4He IC pump', -25)

    #Heat 3He pumps
    wx.PostEvent(parent, messageevent(message='Turning on 3He IC Pump to +25 V.'))
    powersupply.set_voltage('3He IC pump', 25)
    if self.waitforkill(2, killevent): return

    wx.PostEvent(parent, messageevent(message='Turning on 3He UC Pump to +25 V.'))
    powersupply.set_voltage('3He UC pump', -25)
    if self.waitforkill(2, killevent): return

    isHe4ICHigh, isHe3ICHigh, isHe3UCHigh = True, True, True
    while gettemp.gettemp(datafile_name, 'He4 IC Switch') > 8 or \
          gettemp.gettemp(datafile_name, 'He3 IC Switch') > 8 or \
          gettemp.gettemp(datafile_name, 'He3 UC Switch') > 8 or
          isHe4ICHigh or isHe3ICHigh or isHe3UCHigh:
        if self.waitforkill(2, killevent): return

        if gettemp.gettemp(datafile_name, 'He4 IC Pump') > 33:
            wx.PostEvent(parent, messageevent(message='Lowering 4He IC Pump voltage to -4.5V.'))
            powersupply.set_voltage('4He IC pump', -4.5)
            isHe4ICHigh = False

        if gettemp.gettemp(datafile_name, 'He3 IC Pump')> 47:
            wx.PostEvent(parent, messageevent(message='Lowering 4He IC Pump voltage to -4.5V.'))
            powersupply.set_voltage('3He IC pump', -4.55)
            isHe3ICHigh = False

        if gettemp.gettemp(datafile_name, 'He3 UC Pump') > 47:
            wx.PostEvent(parent, messageevent(message='Lowering 3He UC Pump voltage to -6.72V.'))
            powersupply.set_voltage('3He UC pump', -6.72)
            isHe3UCHigh = False

    wx.PostEvent(parent, messageevent(message='Waiting for mainplate to settle'))

    #Checks to see if Mainplate has settled by checking the last 10 slopes in the datafile.
    #wait 10 minutes before checking
    if self.waitforkill(600, killevent): return

    while getslope.getslope(datafile_name, 'mainplate', 60) > 0.001:
        if self.waitforkill(10, killevent): return

    wx.PostEvent(parent, messageevent(message='Mainplate has settled'))
    wx.PostEvent(parent, messageevent(message='Turning off 4He IC pump and turning on switch'))
    powersupply.set_voltage('4He IC pump', 0)
    powersupply.set_voltage('4He IC switch', 5)

    wx.PostEvent(parent, messageevent(message='Waiting for heat exchanger to increase suddenly'))

    # This loop gets the 5 slopes corresponding to the last five lines in the data file
    # If all the 5 slopes are greater than a particular value, we take that as the HEX increasing
    #wait 10 minutes before checking
    if self.waitforkill(600, killevent): return

    while getslope.getslope(datafile_name, 'HEX', 60) < 0.003:
        if self.waitforkill(10, killevent): return

    wx.PostEvent(parent, messageevent(message='HEX has started increasing'))
    wx.PostEvent(parent, messageevent(message='Now turning off 3He IC Pump and turning on switch'))
    powersupply.set_voltage('3He IC pump', 0)
    powersupply.set_voltage('3He IC switch', 5)

    wx.PostEvent(parent, messageevent(message='Waiting for heat exchanger and mainplate to settle'))

    #This loop gets the last 10 slope corresponding to the last ten lines in the data file
    #If all ten slopes for the HEX and mainplate are less than a certain distance from 0, we take that as them being constant.
    while abs(getslope.getslope(datafile_name, 'mainplate', 60)) > 0.001:
        if self.waitforkill(10, killevent): return

    wx.PostEvent(parent, messageevent(message='Now turning off 3He UC Pump and turning on switch'))
    powersupply.set_voltage('3He UC pump', 0)
    powersupply.set_voltage('3He UC switch', 5)

    self.logBox.AppendText( 'Cycle is complete \n ')


if __name__ == __main__:
    # when running as a standalone script, redirect messageevents to the
    # terminal via a dummy parent object
