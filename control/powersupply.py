# powersupply.py
#
# Python module for managing I/O with power supplies. This module must be edited
# by the user for each site application because different models of power supply
# have different commands that are used to get/set voltages.
#
# Adam Anderson
# adama@fnal.gov
# 10 March 2016

import serial

heaternames = ['3He UC pump', '3He IC pump', '4He IC pump',
               '3He UC switch', '3He IC switch', '4He IC switch']

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

serial_interface = {'3He UC pump': ttyr02,
                    '3He IC pump': ttyr03,
                    '4He IC pump': ttyr03,
                    '3He UC switch': ttyr02,
                    '3He IC switch': ttyr02,
                    '4He IC switch': ttyr03}
# do not include termination string in the following commands (typically '\r\n')
# for Keysight/Agilent devices
read_cmd =  {'3He UC pump': 'MEAS:VOLT:DC? N25V',
             '3He IC pump': 'MEAS:VOLT:DC? P25V',
             '4He IC pump': 'MEAS:VOLT:DC? N25V',
             '3He UC switch': 'MEAS:VOLT:DC? P6V',
             '3He IC switch': 'MEAS:VOLT:DC? P25V',
             '4He IC switch': 'MEAS:VOLT:DC? P6V'}
write_cmd = {'3He UC pump': 'APPL N25V,',
             '3He IC pump': 'APPL P25V,',
             '4He IC pump': 'APPL N25V,',
             '3He UC switch': 'APPL P6V,',
             '3He IC switch': 'APPL P25V,',
             '4He IC switch': 'APPL P6V,'}
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
    command = '%s %.2f %s' % (read_cmd[heater], voltage, termination_str)
    serial_interface[heater].write(command)
    voltage = float(serial_interface[heater].readline())

    return voltage
