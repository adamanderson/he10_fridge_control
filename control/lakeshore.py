# lakeshore.py
#
# Classes that represent Lakeshore boxes with Python bindings to RS-232 and TCP/IO
# commands.
#
# Adam Anderson
# adama@fnal.gov
# 25 April 2016

import socket

class Lakeshore350:
    def __init__(self, address, channames):
        '''
        Constructor

        Parameters
        ----------
        address : str
            IP address of Lakeshore box.
        channames : Python list of str
            Names of channels

        Returns
        -------
        None
        '''
        # check for valid channel names
        if len(channames) != 4:
            print('ERROR: Incorrect number of channel names supplied!')
            return

        self.IPaddress = address
        self.channel_names = channames

        self.tcp_interface = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_interface.connect((self.IPaddress, 7777))
        self.tcp_interface.settimeout(1.0)
    

    def query_temps(self):
        '''
        Request temperature measurements from box.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        self.tcp_interface.sendto('KRDG? 0\r\n', (self.IPaddress, 7777))


    def read_queue(self):
        '''
        Read whatever data is in the queue.

        Parameters
        ----------
        None

        Returns
        -------
        output : str
            Contents of the queue.
        '''
        output, _ = self.tcp_interface.recvfrom(2048)
        return output


    def get_temps(self):
        '''
        Request a temperature measurement and then get it from 
        the queue, split merrily into a dictionary indexed by 
        channel name.

        Parameters
        ----------
        None

        Returns
        -------
        temps : dict
            Measured temperatures
        '''
        self.query_temps()
        output = self.read_queue()
        
        temps = {self.channel_names[jchan]: float(output.split(',')[jchan]) \
                 for jchan in range(len(self.channel_names))}
        return temps


    def set_heater_range(self, output, range):
        '''
        Sets the heater range for the PID---morally equivalent to turning
        the heater on and off.
        
        Parameters
        ----------
        output : int
            Heater to configure (1 or 2; 3 and 4 not implemented here)
        range : int
            Heater range (0-5 inclusive, with 0 being off)
        
        Returns
        -------
        None
        '''
        if output in [1,2] and range in [0,1,2,3,4,5]:
            self.tcp_interface.sendto('RANGE %d,%d\r\n'%(output, range), (self.IPaddress, 7777))
        else:
            print('ERROR: Heater range or output outside of allowed range!')


    def set_PID_temp(self, output, temp):
        '''
        Set the PID temperature setpoint.

        Parameters
        ----------
        output : int
            Heater to configure (1 or 2; 3 and 4 not implemented here)
        temp : float
            Setpoint temperature in K

        Returns
        -------
        None
        '''
        if output in [1,2]:
            self.tcp_interface.sendto('SETP %d,%f\r\n'%(output, temp), (self.IPaddress, 7777))
        else:
            print('ERROR: Heater output outside of allowed range!')


    def set_PID_params(self, P, I, D):
        '''
        Set the PID parameters.

        Parameters
        ----------
        P : float
            proportional
        I : float
            integral
        D : float
            derivative

        Returns
        -------
        None
        '''
        self.tcp_interface.sendto('PID %f,%f,%f\r\n'%(P, I, D), (self.IPaddress, 7777))


    def config_output(self, output, mode, input):
        '''
        Configures the output.
        
        Parameters
        ----------
        output : int
            Heater to configure (1 or 2; 3 and 4 not implemented here)
        mode : int
            0 = off
            1 = closed loop PID
            2 = zone
            3 = open loop
            4 = monitor out
            5 = warmup supply
        input : int
            0 = None
            1 = A
            2 = B
            3 = C
            4 = D
        
        Returns
        -------
        None
        '''
        if output in [1,2] and mode in range(6) and input in range(5):
            self.tcp_interface.sendto('OUTMODE %d,%d,%d,0\r\n'%(output, mode, input), (self.IPaddress, 7777))
        else:
            print('ERROR: Heater output, mode, or input outside of allowed range!')
