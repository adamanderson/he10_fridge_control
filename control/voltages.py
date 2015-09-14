import time as sleeptime
import serial
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
#ser.open()
#ser.isOpen()
def getvoltages():
	ser3.write('MEAS:VOLT:DC? N25V \r\n')
	_4icpump = ''
	sleeptime.sleep(.2)
	while ser3.inWaiting() > 0:
		_4icpump+= ser3.read(1)
	
	ser3.write('MEAS:VOLT:DC? P25V \r\n')
	_3icpump = ''
	sleeptime.sleep(.2)
	while ser3.inWaiting() > 0:
		_3icpump+= ser3.read(1)
	
	ser2.write('MEAS:VOLT:DC? N25V \r\n')
	_3ucpump = ''
	sleeptime.sleep(.2)
	while ser2.inWaiting() > 0:
		_3ucpump+= ser2.read(1)

	ser3.write('MEAS:VOLT:DC? P6V \r\n')
	_4icswitch = ''
	sleeptime.sleep(.2)
	while ser3.inWaiting() > 0:
		_4icswitch+= ser3.read(1)

	ser2.write('MEAS:VOLT:DC? P25V \r\n')
	_3icswitch = ''
	sleeptime.sleep(.2)
	while ser2.inWaiting() > 0:
		_3icswitch+= ser2.read(1)
	
		
	ser2.write('MEAS:VOLT:DC? P6V \r\n')
	_3ucswitch = ''
	sleeptime.sleep(.2)
	while ser2.inWaiting() > 0:
		_3ucswitch+= ser2.read(1)

	return round(float(_4icpump),2),  round(float(_3icpump),2),  round(float(_3ucpump),2),  round(float(_4icswitch),2),  round(float(_3icswitch),2),  round(float(_3ucswitch),2)    

       

