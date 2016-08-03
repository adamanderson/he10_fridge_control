# agilent.py
#
# Classes that represent Agilent power supplies with Python bindings
# to RS-232 commands.
#
# Adam Anderson
# adama@fnal.gov
# 28 April 2016

import serial

class Agilent3631A:
    def __init__(self, port, name_6V, name_P25V, name_N25V):
        '''
        Constructor

        Parameters
        ----------
        port : str
           Name of serial port (in /dev)
        name_6V : str
           Name of device connected to 6V terminal power supply
        name_P25V : str
           Name of device connected to +25V terminal power supply
        name_N25V : str
            Name of device connected to -25V terminal power supply
        
        Returns
        -------
        None
        '''
        self.interface = serial.Serial(port=port,
                                       baudrate=9600,
                                       parity=serial.PARITY_ODD,
                                       stopbits=serial.STOPBITS_ONE,
                                       bytesize=serial.SEVENBITS)
        self.chanmapping = {name_6V: 'P6V',
                            name_P25V: 'P25V',
                            name_N25V: 'N25V'}
        self.term_string = '\r\n'


    def set_voltage(self, channel, voltage):
        '''
        Sets the voltage of a heater channel.
        
        Parameters
        ----------
        channel : str
            Name of heater channel to set
        voltage : float
            Voltage to set heater to
        
        Returns
        -------
        None
        '''
        if channel not in self.chanmapping:
            print('ERROR: Selected channel name not found for this interface.')
            return
        self.interface.write('APPL %s, %.2f%s' % \
                             (self.chanmapping[channel], voltage, self.term_string))


    def read_voltage(self, channel):
        '''
        Reads the voltage of a heater channel.
        
        Parameters
        ----------
        channel : str
            Name of heater channel to set
        
        Returns
        -------
        None
        '''
        if channel not in self.chanmapping:
            print('ERROR: Selected channel name not found for this interface.')
            return
        self.interface.write('MEAS:VOLT:DC? %s%s' % \
                             (self.chanmapping[channel], self.term_string))
        
