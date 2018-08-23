import pydfmux
import he10_fridge_control.control.lakeshore as LS
import he10_fridge_control.control.gettemp as gt
import he10_fridge_control.control.pid as pid

class Coldload:
    '''
    Coldload

    Wrapper class for PID temperature controlling the Fermilab cold load.

    Attributes:
    -----------
    WaferLS : Lakeshore350 object
        An object representing the Lakeshroe 350 box that is used to
        control the heater connected to the cold load.
    pidcontrol : PIDController object
        This object handles the actual PID control.

    Parameters:
    -----------
    temp_logfile : str
        Path to hdf5 temperature logfile for controlling the temperature.
    pid_sensor : str
        Name of sensor to use for PID control of cold load.
    lakeshore_ip : str
        IP address of Lakeshore 350 used to control the heater.
    setpoint_init : float
        Initial temperature setpoint.
    p_init : float
        Initial 'P' in the PID control loop.
    i_init : float
        Initial 'I' in the PID control loop.
    d_init : float
        Initial 'D' in the PID control loop.

    Returns:
    --------
    None
    '''
    def __init__(self, temp_logfile, pid_sensor='cold load center',
                 lakeshore_ip='192.168.2.5', setpoint_init=0.0,
                 p_init=1.2, i_init=0.015, d_init=0.0):
        self.WaferLS = LS.Lakeshore350(lakeshore_ip, ['A', 'B', 'C', 'D'])
        self.pidcontrol = pid.PIDController(temp_logfile, pid_sensor, self.WaferLS,
                                            2, p_init, i_init, d_init, setpoint_init)

    def start_temp_control(self, setpoint):
        '''
        Sets the temperature setpoint and starts the PID control.

        Parameters:
        -----------
        setpoint : float
            Temperature setpoint.

        Returns:
        --------
        None
        '''
        self.pidcontrol.set_temp_setpoint(setpoint)
        self.pidcontrol.start_pid()

    def stop_temp_control(self):
        '''
        Stops the PID controller and zeros the heater.
        
        Parameters:
        -----------
        None
        
        Returns:
        --------
        None
        '''
        self.pidcontrol.stop_pid()
