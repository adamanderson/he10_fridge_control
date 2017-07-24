# -*- coding: utf-8 -*-
"""
Last version of 7/24/17

@author: Antony Simonoff 
    for SPT-3G

This file prints position, velocity, and time to a text file or spreadsheet
"""

from __future__ import print_function
import time
import serial
import sys
#from datetime import datetime
#from Tkinter import *
#import xlsxwriter

reload(sys) #sets default encoding due to ascii encoding issues
sys.setdefaultencoding('utf8') 

class NewportSMC100CC:
    def __init__(self): #initialize and open port
        self.serial_interface = serial.Serial(port='/dev/ttyUSB1', baudrate=57600, 
                                              bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                                              stopbits=serial.STOPBITS_ONE, xonxoff=True)
        self.serial_interface.write('01OR\r\n')
        time.sleep(.3) #longer wait because initialization
        self.serial_interface.write('01VA10\r\n') #set slow velocity
        
    def set_velocity(self, velocityInput): #manually sets velocity
        velocityWrite = "01VA" + str(velocityInput) + "\r\n"
        self.serial_interface.write(velocityWrite)
    
    def set_position(self, goToDegrees):
        positionWrite = "01PA" + str(goToDegrees) + "\r\n"
        self.serial_interface.write(positionWrite)
        
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
        
        
newport = NewportSMC100CC()

#interacting with user:

#set velocity at beginning of file run:
global velocityInput
velocityInput = raw_input("What should the velocity be, in degrees per second? Leave blank for 10deg/s\n\n")
if is_number(velocityInput) == True:
    newport.set_velocity(velocityInput)
if velocityInput == "":
    veloctyInput = 10


#set pause at beginning of file run
pauseBetweenLoops = input("How often should data output? Each loop takes about 0.2s\n\n")


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

#make spreadsheet as output         
#workbook = xlsxwriter.Workbook('Output.xlsx')
#worksheet = workbook.add_worksheet()

#bold = workbook.add_format({'bold': 1})

#headers
#worksheet.write('A1', 'Position (degrees)', bold)
#worksheet.write('B1', 'Velocity', bold)
#worksheet.write('C1', 'Time in UTC', bold)

#worksheet.set_column('A:C', 15)

presetDegrees = 45 #sets preset degrees around origin; + and - presetDegrees used
outputFile = open('Output.txt', 'a')

def inputFunc(): #function for all the inputs at the beginning of each run
    goToDegrees = raw_input("Input a degree value to go to. Leave blank to choose presets: " + str(presetDegrees) + " deg, or -" + str(presetDegrees) + " deg\n\n")

    if is_number(goToDegrees) == True:
        return goToDegrees
    else:
        presetInput = raw_input("Enter (A) for " + str(presetDegrees) + " deg, (B) for -" + str(presetDegrees) + " deg\n\n")
        if presetInput == "A" or presetInput == "a":
            goToDegrees = presetDegrees
            return goToDegrees
        elif presetInput == "B" or presetInput == "b":  
            goToDegrees = presetDegrees * -1
            return goToDegrees
        else:
            inputFunc()
    
    

def rotateFunc(): #function that deals with the actual rotation of the rotating stage
    currentPosition = formatter(newport.get_position())
    print(currentPosition)
    currentLoop = 0
    
    goToDegrees = inputFunc()
    
    numberOfLoops = int((abs(int(currentPosition)) + abs(int(goToDegrees))/int(velocityInput))/pauseBetweenLoops)
    print(numberOfLoops)
    
    newport.set_position(goToDegrees)
    
    for currentLoop in range(0, numberOfLoops): #loop for data output
        currentLoop = currentLoop + 1
 
        #errString_position = newport.get_position() 
        response_position = newport.get_position() 
        print(numberOfLoops)
	
	"""if is_number(response_position) == True :
		positionPrint = stringer("Position:", response_position)
		outputFile.write(positionPrint)
	else:
		positionPrint = stringer("Position Error:", errString_position)
		outputFile.write(positionPrint)"""
  
	#worksheet.write(currentLoop, 0, formatter(response_position))

        positionPrint = "Position:" + " " + str(formatter(response_position)) +"\n"
        outputFile.write(positionPrint) 

        velocityPrint = "Velocity:" + " " + str(velocityInput) + "\n"
        outputFile.write(velocityPrint)
 
	#worksheet.write(currentLoop, 1, 'N/A') #velocity placeholder
 
	#worksheet.write(currentLoop, 2, datetime.utcnow())


	#timePrint = "Time in UTC:" + " " + str(datetime.utcnow()) +"\n"
 	#outputFile.write(timePrint)
        timePrint = "Time in UTC:" + " " + str(time.time()) +"\n"
        outputFile.write(timePrint)
        currentLoopPrint = "Current Loop:" + " " + str(currentLoop) +"\n"
        outputFile.write(currentLoopPrint)
        outputFile.write("\n")
        time.sleep(pauseBetweenLoops) #sets pause length between loop runs, each run takes about 200ms

def continueFunc():
    continueInput = raw_input("Continue Y/N? ")
    if continueInput == "Y" or continueInput == "y":
        continueInput = "Yes"
        rotateFunc()
    elif continueInput == "N" or continueInput == "n":
        continueInput = "No"
        outputFile.close()
        sys.exit()
    else:
        continueFunc()

continueFunc()

outputFile.close()
#workbook.close()
