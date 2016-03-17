# powersupply.py
#
# Python module for managing I/O with power supplies. This module must be edited
# by the user for each site application because different models of power supply
# have different commands that are used to get/set voltages.
#
# In the first few lines of the script, the following things should occur:
# 1.) Serial interfaces should be defined for all power supplies (e.g. a
# serial.Serial object).
# 2.) Serial interfaces must be mapped to each pump and heater in the dictionary
# 'serial_interface'.
# 3.) The commands to send to read each voltage must be specified in the 
# dictionary 'read_cmd'.
# 4.) The commands to sedn to write each voltage must be specified in the
# dictionary 'write_cmd'.
# 5.) The termination characters to add to the end of each read/write command
# (typically '\r\n') should be specified in the variable termination_str.
#
# Adam Anderson
# adama@fnal.gov
# 10 March 2016

import serial

heaternames = ['3He UC pump', '3He IC pump', '4He IC pump',
               '3He UC switch', '3He IC switch', '4He IC switch']

# serial interfaces to power supplies
ttyr02 = serial.Serial(port='/dev/ttyr02',
                       baudrate=9600,
                       parity=serial.PARITY_ODD,
                       stopbits=serial.STOPBITS_ONE,
                       bytesize=serial.SEVENBITS)
ttyr03 = serial.Serial(port='/dev/ttyr03',
                       baudrate=9600,
                       parity=serial.PARITY_ODD,
                       stopbits=serial.STOPBITS_ONE,
                       bytesize=serial.SEVENBITS)

# mapping of serial interfaces to heaters
serial_interface = {'3He UC pump': ttyr02,
                    '3He IC pump': ttyr03,
                    '4He IC pump': ttyr03,
                    '3He UC switch': ttyr02,
                    '3He IC switch': ttyr02,
                    '4He IC switch': ttyr03}

# commands to read from power supplies
read_cmd =  {'3He UC pump': 'MEAS:VOLT:DC? N25V',
             '3He IC pump': 'MEAS:VOLT:DC? P25V',
             '4He IC pump': 'MEAS:VOLT:DC? N25V',
             '3He UC switch': 'MEAS:VOLT:DC? P6V',
             '3He IC switch': 'MEAS:VOLT:DC? P25V',
             '4He IC switch': 'MEAS:VOLT:DC? P6V'}

# commands to write to power supplies
write_cmd = {'3He UC pump': 'APPL N25V,',
             '3He IC pump': 'APPL P25V,',
             '4He IC pump': 'APPL N25V,',
             '3He UC switch': 'APPL P6V,',
             '3He IC switch': 'APPL P25V,',
             '4He IC switch': 'APPL P6V,'}

# termination character to add onto commands to send
termination_str = '\r\n'


def set_voltage(heater, voltage):
    # TODO: Add some error-checking/handling for the voltage values
    '''
    Sets the voltage for a specific heater.

    Parameters
    ----------
    heater : str
        String to identify the pump or heater to change
    voltage : float
        Value of voltage to set

    Returns
    -------
    None
    '''
    command = '%s %.2f %s' % (write_cmd[heater], voltage, termination_str)
    serial_interface[heater].write(command)


def read_voltage(heater):
    # TODO: Add some error-checking/handling
    '''
    Read the voltage for a specific heater.

    Parameters
    ----------
    heater : str
        String to identify the pump or heater to change

    Returns
    -------
    None
    '''
    command = '%s %s' % (read_cmd[heater], termination_str)
    serial_interface[heater].write(command)
    voltage = float(serial_interface[heater].readline())

    return voltage
