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

# TODO: At various points we compute slopes to see if various temperatures have
# "settled". These are computed over the last N points, but instead should be
# computed over a fixed time interval because the logging interval can change [AJA]

import time
import gettemp
import getslope
from wx import PostEvent
import powersupply


def waitforkill(waittime, killevent):
    '''
    Waits for waittime and return True if kill flag is set, False otherwise.
    '''
    nSteps = int(waittime / 0.1)
    for jStep in range(nSteps):
        time.sleep(0.1) # our simulated calculation time
        if killevent.is_set() == True:
            return True
    return False


def run(datafile_name, parent, messageevent, killevent):
    # turn off all pumps and switches
    for name in powersupply.heaternames:
        powersupply.set_voltage(name, 0.0)
        PostEvent(parent, messageevent(message=('Setting %s to 0V.' % name)))

    PostEvent(parent, messageevent(message='Waiting for switches to cool.'))
    while gettemp.gettemp(datafile_name, 'He4 IC Switch') > 8 or \
          gettemp.gettemp(datafile_name, 'He3 IC Switch') > 13 or \
          gettemp.gettemp(datafile_name, 'He3 UC Switch') > 8:
        if waitforkill(1, killevent): return

    #Heat 4HE IC pump first, then do other He3 pumps next
    PostEvent(parent, messageevent(message='Turning on 4He IC Pump to -25 V.'))
    powersupply.set_voltage('4He IC pump', -25)
    if waitforkill(2, killevent): return

    PostEvent(parent, messageevent(message='Waiting for 4He IC Pump to reach 33K.'))
    while gettemp.gettemp(datafile_name, 'He4 IC Pump') < 33:
        if waitforkill(2, killevent): return

    PostEvent(parent, messageevent(message='Lowering 4He IC Pump voltage to -4.5V.'))
    powersupply.set_voltage('4He IC pump', -4.5)

    #Heat 3He pumps
    PostEvent(parent, messageevent(message='Turning on 3He IC Pump to +25 V.'))
    powersupply.set_voltage('3He IC pump', 25)
    if waitforkill(2, killevent): return

    PostEvent(parent, messageevent(message='Turning on 3He UC Pump to +25 V.'))
    powersupply.set_voltage('3He UC pump', -25)
    if waitforkill(2, killevent): return

    PostEvent(parent, messageevent(message='Waiting for all switches to be <8K, and 3He pumps to be >47K'))
    isHe3ICHigh, isHe3UCHigh = True, True
    while gettemp.gettemp(datafile_name, 'He4 IC Switch') > 8 or \
          gettemp.gettemp(datafile_name, 'He3 IC Switch') > 8 or \
          gettemp.gettemp(datafile_name, 'He3 UC Switch') > 8 or \
          isHe3ICHigh or isHe3UCHigh:
        if waitforkill(2, killevent): return
        
        # TODO: Don't hardcode in thermometer names, lookup from logger python modules (AJA)
        if gettemp.gettemp(datafile_name, 'He3 IC Pump')> 47 and isHe3ICHigh==True:
            PostEvent(parent, messageevent(message='Lowering 3He IC Pump voltage to 4.55V.'))
            powersupply.set_voltage('3He IC pump', 4.55)
            if waitforkill(2, killevent): return
            isHe3ICHigh = False

        if gettemp.gettemp(datafile_name, 'He3 UC Pump') > 47 and isHe3UCHigh==True:
            PostEvent(parent, messageevent(message='Lowering 3He UC Pump voltage to -6.72V.'))
            powersupply.set_voltage('3He UC pump', -6.72)
            if waitforkill(2, killevent): return
            isHe3UCHigh = False

    PostEvent(parent, messageevent(message='Waiting for mainplate to settle'))

    #Checks to see if Mainplate has settled by checking the last 10 slopes in the datafile.
    #wait 10 minutes before checking
    if waitforkill(600, killevent): return

    while getslope.getslope(datafile_name, 'mainplate', 60) > 0.001:
        if waitforkill(10, killevent): return

    PostEvent(parent, messageevent(message='Mainplate has settled'))
    PostEvent(parent, messageevent(message='Turning off 4He IC pump and turning on switch'))
    powersupply.set_voltage('4He IC pump', 0)
    powersupply.set_voltage('4He IC switch', 5)

    PostEvent(parent, messageevent(message='Waiting for heat exchanger to increase suddenly'))
    if waitforkill(1200, killevent): return
    while getslope.getslope(datafile_name, 'HEX', 60) < 0.003:
        if waitforkill(10, killevent): return

    PostEvent(parent, messageevent(message='HEX has started increasing'))
    PostEvent(parent, messageevent(message='Now turning off 3He IC Pump and turning on switch'))
    powersupply.set_voltage('3He IC pump', 0)
    powersupply.set_voltage('3He IC switch', 5)

    PostEvent(parent, messageevent(message='Waiting for heat exchanger and mainplate to settle'))
    if waitforkill(600, killevent): return
    while abs(getslope.getslope(datafile_name, 'mainplate', 60)) > 0.001:
        if waitforkill(10, killevent): return

    PostEvent(parent, messageevent(message='Now turning off 3He UC Pump and turning on switch'))
    powersupply.set_voltage('3He UC pump', 0)
    powersupply.set_voltage('3He UC switch', 5)

    if waitforkill(600, killevent): return

    PostEvent(parent, messageevent(message='Cycle is complete'))
    killevent.set()


if __name__ == '__main__':
    # when running as a standalone script, redirect messageevents to the
    # terminal via a dummy parent object
    # Updated 2017/11/23 [ASR]

    import argparse
    import signal
    import threading
    import os

    # Ensure the fridge log file is readable
    P = argparse.ArgumentParser('Run autocycle on HPD cryostat')
    P.add_argument('fridge_log', help='Path to fridge log file',
                   type=argparse.FileType('r'))
    args = P.parse_args()

    # Timestamped log messages
    # This simple log printer replaces the LoggingEvent handling
    # that's done in the GUI.
    def log(message):
        print('[ {} ]  {}'.format(
            time.strftime('%c %Z', time.localtime()), message))

    # Dummy event handler that overloads the imported wx function
    # This handler does nothing since the log message is handled
    # right away by the log function.
    def PostEvent(handler, event):
        return

    # Handle cycle interrupts smoothly
    abortcycle = threading.Event()

    def onexit(signum, frame):
        abortcycle.set()
        print('')
        log('Terminating fridge cycle.')
        log('Zeroing all pump heaters and switches.')
        powersupply.set_voltage('4He IC pump', 0.0)
        powersupply.set_voltage('3He IC pump', 0.0)
        powersupply.set_voltage('3He UC pump', 0.0)
        powersupply.set_voltage('4He IC switch', 0.0)
        powersupply.set_voltage('3He IC switch', 0.0)
        powersupply.set_voltage('3He UC switch', 0.0)
        log('Fridge cycle terminated.')
        raise SystemExit

    signal.signal(signal.SIGINT, onexit)

    # Now ready to run
    log('Starting autocycle...')
    run(args.fridge_log.name, None, log, abortcycle)
