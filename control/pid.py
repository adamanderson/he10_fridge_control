import numpy as np
import time
import he10_fridge_control.control.gettemp as gt
import Queue
import multiprocessing

class PIDController:
    def __init__(self, logger_file, thermometer_name, heater, heater_num, P, I, D, temp_setpoint):
        self.logger_file = logger_file
        self.thermometer_name = thermometer_name
        self.heater = heater
        self.heater_num = heater_num
        self.Kp = P
        self.Ki = I
        self.Kd = D
        self.temp_setpoint = temp_setpoint
        self.update_time = 5 # sec

        # multiprocessing stuff to run PID in background
        self.queue = multiprocessing.Queue(maxsize=1)

    def start_pid(self, heater_initial=0):
        self.proc = multiprocessing.Process(target=self.run, args=(self.queue, heater_initial))
        self.proc.start()

    def stop_pid(self):
        self.proc.terminate()

    def set_temp_setpoint(self, temp_setpoint):
        self.queue.put(temp_setpoint)
        
    def run(self, queue, heater_initial):
        i_prev = heater_initial
        err_prev = 0
        while True:
            # Use queue to change the setpoint
            try:
                self.temp_setpoint = queue.get(block=False)
            except Queue.Empty:
                pass
            temp = gt.gettemp(self.logger_file, self.thermometer_name)
            err = self.temp_setpoint - temp

            # Integral
            i = i_prev + self.Ki * (self.update_time * err)
            # Derivative
            d = self.Kd * (err - err_prev)/self.update_time
            # Proportional
            p = self.Kp * err
            
            # set heater
            heater_value = np.max([i + d + p, 0])
            self.heater.set_heater_output(self.heater_num, heater_value)
            
            # Adjust previous values
            err_prev = err
            i_prev = i

            time.sleep(self.update_time)
