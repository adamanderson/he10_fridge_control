# -*- coding: utf-8 -*-
"""
Last version of 6/16/17

@author: Antony Simonoff 
    for SPT-3G

This file prints position, velocity, and time to a text file or spreadsheet
"""

from __future__ import print_function
import time
import serial
from datetime import datetime
#from Tkinter import *
#import xlsxwriter

class NewportSMC100CC:
    def __init__(self): #initialize and open port
        self.serial_interface = serial.Serial(port='/dev/ttyUSB0', baudrate=57600, 
                                              bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                                              stopbits=serial.STOPBITS_ONE, xonxoff=True)
        self.serial_interface.write('01OR\r\n')                                      
        
    def get_velocity(self): #get current velocity
        self.serial_interface.write('01VA?\r\n')
        time.sleep(.1)
        velocity = self.serial_interface.read(self.serial_interface.inWaiting())
        return velocity
    
    def get_position(self): #get current position
        self.serial_interface.write('01TP?\r\n')
        time.sleep(.1)
        position = self.serial_interface.read(self.serial_interface.inWaiting())
        return position
        
newport = NewportSMC100CC()

#interacting with user:
numberOfLoops = input("How many loops should there be?\n\n") #Sets number of loops
pauseBetweenLoops = input("How many seconds between loop runs? Each loop takes about 0.2s\n\n")


"""def show_entry_fields(): #Tkinter input/output, but I haven't figured out how to do this yet
   print("Loops: %s\nSeconds between loops: %s" % (e1.get(), e2.get()))
   pauseBetweenLoops = e2.get()
   numberOfLoops = e1.get()

master = Tk()
Label(master, text="How many loops?").grid(row=0)
Label(master, text="Time between loops?").grid(row=1)

e1 = Entry(master)
e2 = Entry(master)

e1.grid(row=0, column=1)
e2.grid(row=1, column=1)

Button(master, text='Close', command=master.quit).grid(row=3, column=0, sticky=W, pady=4)
Button(master, text='Confirm', command=show_entry_fields).grid(row=3, column=1, sticky=W, pady=4)

#mainloop()
wait_variable(numberOfLoops)"""

currentLoop = 0
outputFile = open('Output.txt', 'a')
def is_number(testStr): #test to see if a string is a number or error
	try:
		float(testStr)
		return True
	except ValueError:
		return False
   
def formatter(inputStr): #formats response from device
	inputStr= str(inputStr)
	inputStr= inputStr.strip()
	inputStr= inputStr.strip()[4:]
	inputStr = float(inputStr)
	return inputStr
	
#make spreadsheet as output         
#workbook = xlsxwriter.Workbook('Output.xlsx')
#worksheet = workbook.add_worksheet()

#bold = workbook.add_format({'bold': 1})

#headers
#worksheet.write('A1', 'Position (degrees)', bold)
#worksheet.write('B1', 'Velocity', bold)
#worksheet.write('C1', 'Time in UTC', bold)

#worksheet.set_column('A:C', 15)
 
while numberOfLoops > currentLoop: #loop for data output
	currentLoop = currentLoop + 1
 
	errString_position = newport.get_position() 
	response_position = newport.get_position() 
	
	"""if is_number(response_position) == True :
		positionPrint = stringer("Position:", response_position)
		outputFile.write(positionPrint)
	else:
		positionPrint = stringer("Position Error:", errString_position)
		outputFile.write(positionPrint)"""
  
	#worksheet.write(currentLoop, 0, formatter(response_position))

	positionPrint = "Position:" + " " + str(formatter(response_position)) +"\n"
	outputFile.write(positionPrint) 

	"""
	---
	I don't know the command to get velocity
	VA, KV, ZT don't work
	Need to find command then change in NewportSMC100CC.get_velocity 
	--- 
	response_velocity = newport.get_velocity() 
	errString_velocity = newport.get_velocity() 
	#if is_number(response_velocity) == True:
	#	velocityPrint = stringer("Velocity:", response_velocity)
	#	outputFile.write(velocityPrint)
	#else:
	#	velocityPrint = stringer("Velocity Error:", errString_velocity)
	#	outputFile.write(velocityPrint)"""
 	
  	outputFile.write("Velocity: N/A\n")
 
	#worksheet.write(currentLoop, 1, 'N/A') #velocity placeholder
 
	#worksheet.write(currentLoop, 2, datetime.utcnow())


	timePrint = "Time in UTC:" + " " + str(datetime.utcnow()) +"\n"
 	outputFile.write(timePrint)
	timePrint = "Time in UTC:" + " " + str(time.time()) +"\n"
 	outputFile.write(timePrint)
	currentLoopPrint = "Current Loop:" + " " + str(currentLoop) +"\n"
	outputFile.write(currentLoopPrint)
	outputFile.write("\n")
	time.sleep(pauseBetweenLoops) #sets pause length between loop runs, each run takes about 200ms

outputFile.close()
#workbook.close()