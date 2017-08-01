# -*- coding: utf-8 -*-
"""
Last version of 7/21/2017

Author: Arielle Pfeil  
    for SPT-3G

This file preforms the following tasks: 
    Asks for an input frequency (HIGH or LOW frequency)
    Changes frequency of optical chopper 
    Gives status of frequency 
    Writes frequency and time to text file 

Protocol: 9600 N 8 1 (Baud Rate of 9600 Baud, no parity bit, 8 data 
bits, and one stop bit)

Command structure: F:1000.000CR
	F is prefix 
	1000.000 is frequency (11 digits needed)
		High frequency: 40-5000 Hz 
		Low frequency: 4-500 Hz
	CR is carriage return 

Correct response string: "OK"
Incorrect command string: "Invalid Command"

Request status string: "F:STATUSRQCR"
	Will return following: 
		INT(EXT) SYNC
 		HI (LO ) SPEED RANGE
		1000.000 HZ

Incorrect frequency string :
    FOR THE RANGE IN USE, FREQ. IS TOO HIGH (LOW)
"""


from __future__ import print_function
import time
import serial
from datetime import datetime
from sys import exit 

class OpticalChopperC995:
    def __init__(self): #initialize and open port
        self.serial_interface = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, #linux port
                            bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                            stopbits=serial.STOPBITS_ONE, xonxoff=True)
        
    def get_frequency(self): #get current frequency 
        self.serial_interface.write('F:STATUSRQ\r\n')
        time.sleep(.1)
        recieve = self.serial_interface.read(self.serial_interface.inWaiting())
        return recieve 
    
    def send_frequency(self,input_frequency): #input frequency to chopper 
        input_frequency = "F:" + str(input_frequency) + "\r\n"
        #input_frequency = "F:" + str(input_frequency)
        #print(input_frequency)
        self.serial_interface.write(input_frequency)
        time.sleep(.1)
        sent = self.serial_interface.read(self.serial_interface.inWaiting())
        return sent

chopper = OpticalChopperC995() #rename chopper

#user information and frequency input 
print("LOW frequencies are 4-500 Hz \nHIGH frequencies are 501-5000 Hz")


outputFile = open('Chopper_Frequency_Output.txt', 'a')

global invalid_input 
invalid_input = True 
def request_loop():
    ask_input = raw_input("Would you like to (A) set frequency or (B) get status? \nInput A or B: ")
    
    #for inputting frequency 
    if ask_input == "A":
        print("Input frequency with 7 digits (i.e 0015.720).\n\n")
        input_frequency = raw_input("What frequency would you like to set? \nInput: ")
        #input_frequency = float(input_frequency)
        #print("l" + str(input_frequency) + "r")

        #if input_frequency == 0:
            #invalid_input = True
            #return invalid_input
        #if input_frequency > 4 and input_frequency <= 5000:
            #print("LOW frequency: + str(sent)") 
        sent = chopper.send_frequency(input_frequency)
        if sent != "OK\r\n":
            print("\n\nERROR. You probably need to flip the frequency switch")
        #elif input_frequency > 500 and input_frequency <=5000:
            #sent = chopper.send_frequency(input_frequency)
            #if sent != "OK\r\n":
               # print("ERROR. You probably need to flip the frequency switch")
       
        #elif input_frequency >= 40 and input_frequency <= 5000:
            #print("HIGH frequency: + str(sent)")
            #sent = chopper.send_frequency(input_frequency)
            
                   
        """else:
            print("FREQUENCY NOT IN RANGE")
            invalid_input = True
            return invalid_input"""
        
        print(sent)
        frequencyPrint = "Frequency is: " + str(input_frequency) + "Hz\n"
        outputFile.write(frequencyPrint)
        timePrint = "Time in UTC:" + " " + str(datetime.utcnow()) +"\n"
        outputFile.write(timePrint)
        invalid_input = False
        return invalid_input
          
    #for recieving frequency 
    elif ask_input == "B":
        recieve = chopper.get_frequency()
        print(recieve) 
        frequencyPrint = "Frequency is: " + str(recieve) + "Hz\n"
        outputFile.write(frequencyPrint)
        timePrint = "Time in UTC:" + " " + str(datetime.utcnow()) +"\n"
        outputFile.write(timePrint)
        #recieved frequency should read:
            #INT(EXT) SYNC, HI (LO) SPEED RANGE, 1000.000 HZ
        invalid_input = True
        return invalid_input
    
    else:
        print("Error: Please input (A) set frequency or (B) get status.")  
        invalid_input = True
        return invalid_input

#global run_again_failed
#run_again_failed = False
def run_again():
    run_again_failed = False
    while run_again_failed == False:
        run_again_request = raw_input("Would you like to stop? (N) No or (ENTER) Yes  \nInput N or ENTER: ")
        if run_again_request == "N":
            wait = raw_input("PRESS ENTER TO CONTINUE.")
            run_again_failed = False
            return run_again_failed
        else: #run_again_request == "N": 
            outputFile.close()            
            exit()
        #else:
            #print("YOU FAILED. TRY AGAIN.")
            #run_again_failed = False
            #return run_again_failed
        

def loop_function():
    while invalid_input == True:
        request_loop()
        #wait = raw_input("PRESS ENTER TO CONTINUE.")
        run_again()

        
loop_function()

"""def is_number(testStr): #test to see if a string is a number or error
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
	return inputStr"""

#timePrint = "Time in UTC:" + " " + str(datetime.utcnow()) +"\n"
#outputFile.write(timePrint)
#timePrint = "Time in UTC:" + " " + str(time.time()) +"\n"
#outputFile.write(timePrint)
#outputFile.write("\n")

outputFile.close()


"""run_again_request = raw_input("Would you like to run again? (Y) yes or (N) no  \nInput: ")
if run_again_request == "Y":
    loop_function()
elif run_again_request == "N": 
    sys.exit()
"""