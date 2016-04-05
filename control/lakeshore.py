# lakeshore.py
#
# Python module for managing I/O with lakeshore boxes, including running the
# PID.
#
# Adam Anderson
# adama@fnal.gov

import numpy as np
import socket

millikelvin_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
millikelvin_socket.connect(('192.168.0.12', 7777))
millikelvin_socket.settimeout(1.0)


tcp_interfaces = {'UC Head':    millikelvin_socket,
                  'IC Head':    millikelvin_socket,
                  'UC stage':   millikelvin_socket,
                  'LC shield':  millikelvin_socket]}

class Lakeshore350:
    '''
    Class representing a Lakeshore 350 box, with basic functionality such as
    querying the temperatures and using a PID control loop.

    Attributes:
    -----------
    ip_address : IP address of the box
    channel_names : names of each of the 4 channels of the box
    io_socket : the socket object used to communicate with the box
    '''
    def __init__(self, ip_address, channel_names):
        self.ip_address = ip_address
        self.channel_names = channel_names
        self.io_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        '''
        Connects to the TCP/IP interface for this Lakeshore 350.

        Parameters:
        -----------
        None

        Returns:
        --------
        None
        '''
        self.io_socket.connect((self.ip_address, 7777))
        self.io_socket.settimeout(1.0)

    def set_pid_temp(self, channel, temp):
        '''
        Sets the PID temperature for a specific channel.

        Parameters:
        -----------
        channel : string
            Channel for which to set PID temperature.
        temp : float
            Temperature at which to PID control.

        Returns:
        --------
        None
        '''
        channel_index = channel_names.index(channel)+1
        self.io_socket.sendto('SETP %d,%f\r\n' % (channel_index, temp), (self.ip_address, 7777))

    def set_pid_chan(self, channel):
        '''
        Sets the channel to use for the PID control loop.

        Parameters:
        -----------
        channel : string
            Channel to set for the PID control loop.

        Returns:
        --------
        None
        '''
        channel_index = channel_names.index(channel)+1
        self.io_socket.sendto('OUTMODE 1,1,%d,0\r\n' % channel_index, (self.ip_address, 7777))

    def set_pid_heater(self, heater_level):
        '''
        Sets the heater level to use in the PID control loop. Options are 0-5
        (inclusive), with 0 being off. Note that this is the way to turn the
        heater on and off.

        Parameters:
        -----------
        heater_level : float
            Integer between 0 and 5 inclusive.

        Returns:
        --------
        None
        '''
        if heater_level < 0 or heater_level > 5:
            print 'ERROR: Heater level outside of range. Values 0-5 allowed only.'
            return
        channel_index = channel_names.index(channel)+1
        self.io_socket.sendto('RANGE %d,%d\r\n' % (channel_index, heater_level), (self.ip_address, 7777))
