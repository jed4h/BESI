#!/usr/bin/env python
from gpio_utils import *
from ShimmerBT import *
from Constants import *
from TSL2561 import *
from LM60 import *
from Shimmer3 import *
from Mic import *
import socket
import time
import csv
import threading
import sys

# reads analog in from temperature sensor connected to AIN0
# reads Montion sensor connected to GPIO0_7 and writes value to 
# LED coneected to GPIO1_28
# Light sensor connected to I2C bus 1
#   GND             P9_1
#   VCC (3.3V)      P9_3
#   SCL             P9_19
#   SDA             P9_20
#   
#
#   TMP OUT         P9_39
#
#   mic OUT         P9_40
#   mic VCC (1.8V)  P9_32
#
#
#
#



#i=0
#streamingError = 0  # set to 1 if we lose connecting while streaming

#if len(sys.argv) == 2:
#    hostIP = str(sys.argv[1])
#else:
#    hostIP = HOST
#    print "No IP address given, using default"

# read defaults from config file

fconfig = open("config")
for line in fconfig:
	if line[0] == "#":
            pass
        else:
            splitLine = line.split("=")
            try:
                if splitLine[0] == "BaseStation_IP":
                    BaseStation_IP2 = str(splitLine[1]).rstrip()
            except:
                print "Error reading IP Address"
            
            try:
                if splitLine[0] == "relayStation_ID":
                    relayStation_ID2 = int(splitLine[1])
            except:
                print "Error reading Port" 

default_settings = ''

print ("Default Settings:")
print ("Base Station IP Address: {0}".format(BaseStation_IP2))
print ("Relay Station ID: {0}".format(relayStation_ID2))

while default_settings != ("Y") and default_settings != ("y") and default_settings != ("N") and default_settings != ("n"):
	default_settings = str(raw_input("Use Default Settings? (Y/N):"))


if (default_settings == "N" or default_settings == "n"):
	hostIP = str(raw_input("Enter the base station IP address: "))
	BASE_PORT = int(raw_input("Enter the relay station ID (port): "))
else:
	hostIP = BaseStation_IP2
	BASE_PORT = relayStation_ID2 

while True:
	# get the shimmerID and what sensors to use from the base station if we are streaming
	# if not streaming, use default values
	if IS_STREAMING:
		synchSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address_synch = (hostIP, BASE_PORT)
		synchSock.settimeout(10)
		print "connecting to %s port %s" % server_address_synch
		try:
			synchSock.connect(server_address_synch)
		except:
			print "connection to base station timed out"
			time.sleep(5)
			continue
			
		synchSock.settimeout(None)
		
		# receive info
		# get 3 byte length first
		msgLen = ''
		while (len(msgLen) != 3):
			try:
				msgLen = msgLen + synchSock.recv(3)
			except:
				pass

		msgLen = int(msgLen)
		data = ''    
		# call recv until we get all the data
		while (len(data) != msgLen):
			try:
				data = data + synchSock.recv(msgLen)
			except:
				pass
			
		splitData = data.split(",")
		#data format is <USE_ACCEL>,<USE_ADC>,<USE_LIGHT>,<ShimmerID>
		USE_ACCEL = (splitData[0] == "True")
		USE_ADC = (splitData[1] == "True")
		USE_LIGHT = (splitData[2] == "True")
		SHIMMER_ID = splitData[3]
		SHIMMER_ID2 = splitData[4]
		SHIMMER_ID3 = splitData[5]


		synchSock.close()

	ftemp = open("temp", "w")
	flight = open("light", "w")
	faccel = open("accel", "w")
	fsound = open("sound", "w")
	ferror = open("error", "w")
	fdoor = open("door", "w")

	accelWriter = csv.writer(faccel)
	lightWriter = csv.writer(flight)
	tempWriter = csv.writer(ftemp)
	soundWriter = csv.writer(fsound)
	doorWriter = csv.writer(fdoor)
		

	#stream to base station 
	if IS_STREAMING:

		if USE_ACCEL:
		    # try to connect until successful
		    while True:
			# create socket
			accelSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			# create socket address to send data to base station
			server_address_accel = (hostIP, BASE_PORT)
			print >>sys.stderr, 'connecting to %s port %s' % server_address_accel
			try:
			    # connect to base station
			    accelSock.connect(server_address_accel)
			except:
			    continue
			else:
			    # create a thread to communicate with Shimmer3 and base station
			    accelThread = threading.Thread(target=shimmerSense, args=(accelWriter,accelSock, ferror, SHIMMER_ID, SHIMMER_ID2, SHIMMER_ID3,  IS_STREAMING, IS_LOGGING))
			    # Thread will stop when parent is stopped
			    accelThread.setDaemon(True)
			    break			

		if USE_LIGHT:
		    while True:
			lightSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			server_address_light = (hostIP, BASE_PORT + 1)
			print >>sys.stderr, 'connecting to %s port %s' % server_address_light
			try:
			    lightSock.connect(server_address_light)
			except:
			    continue
			else:
			    lightThread = threading.Thread(target=lightSense, args=(lightWriter, lightSock, IS_STREAMING, IS_LOGGING))
			    lightThread.setDaemon(True)
			    break
			
		if USE_ADC:
		    while True:
			soundSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			tempSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			doorSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			server_address_sound = (hostIP, BASE_PORT + 2)
			server_address_temp = (hostIP, BASE_PORT + 3)
			server_address_door = (hostIP, BASE_PORT + 4)
			print >>sys.stderr, 'connecting to %s port %s' % server_address_sound
			print >>sys.stderr, 'connecting to %s port %s' % server_address_temp
			print >>sys.stderr, 'connecting to %s port %s' % server_address_door
			try:
			    soundSock.connect(server_address_sound)
			    tempSock.connect(server_address_temp)
			    doorSock.connect(server_address_door)
			except:
			    continue
			else:
			    # all sensors that use the ADC need to be managed by a single thread
			    ADCThread = threading.Thread(target=soundSense, args = (tempWriter, soundWriter, soundSock, tempSock, doorWriter, doorSock, IS_STREAMING, IS_LOGGING))
			    ADCThread.setDaemon(True)
			    break


	# running the BBB without streaming is not well tested
	else:
		if USE_ACCEL:
			accelThread = threading.Thread(target=shimmerSense, args=(accelWriter, None, ferror, SHIMMER_ID, SHIMMER_ID, SHIMMER_ID,  IS_STREAMING, IS_LOGGING))
		accelThread.setDaemon(True)
		if USE_LIGHT:
			lightThread = threading.Thread(target=lightSense, args=(lightWriter, None, IS_STREAMING, IS_LOGGING))
		lightThread.setDaemon(True)
		if USE_ADC:
			ADCThread = threading.Thread(target=soundSense, args = (tempWriter, soundWriter, None, None, doorWriter, None, IS_STREAMING, IS_LOGGING))



	# trap keyboard interrupt
	try:
		if USE_ACCEL:
			accelThread.start()
		if USE_LIGHT:
			lightThread.start()
		if USE_ADC:
			ADCThread.start()
		#while True:
		#    pass

		if USE_ACCEL:
			accelThread.join()
		if USE_LIGHT:
			lightThread.join()
		if USE_ADC:
			ADCThread.join()
	
    
	except:
		print ""
		print "Exit"
		

	
	finally:
		ferror.close()    
		ftemp.close()
		flight.close()
		faccel.close()
		fsound.close()
		fdoor.close()
		if IS_STREAMING:
			if USE_ACCEL:
					accelSock.close()
			if USE_LIGHT:
					lightSock.close()
			if USE_ADC:
					soundSock.close()
					tempSock.close()
					doorSock.close()
			print "Done"
