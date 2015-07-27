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

hostIP = str(raw_input("Enter the base station IP address: "))
BASE_PORT = int(raw_input("Enter the relay station ID (port): "))

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

# get the shimmerID and what sensors to use from the base station if we are streaming
# if not streaming, use default values
if IS_STREAMING:
    synchSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address_synch = (hostIP, BASE_PORT)
    print "connecting to %s port %s" % server_address_synch
    synchSock.connect(server_address_synch)

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

    synchSock.close()


#stream to base station 
if IS_STREAMING:

    if USE_ACCEL:
        # create socket
        accelSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # create socket address to send data to base station
        server_address_accel = (hostIP, BASE_PORT)
        print >>sys.stderr, 'connecting to %s port %s' % server_address_accel
        # connect to base station
        accelSock.connect(server_address_accel)
        # create a thread to communicate with Shimmer3 and base station
        accelThread = threading.Thread(target=shimmerSense, args=(accelWriter,accelSock, ferror, SHIMMER_ID,  IS_STREAMING, IS_LOGGING))
        # Thread will stop when parent is stopped
        accelThread.setDaemon(True)
        
    if USE_LIGHT:
        lightSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address_light = (hostIP, BASE_PORT + 1)
        print >>sys.stderr, 'connecting to %s port %s' % server_address_light
        lightSock.connect(server_address_light)
        lightThread = threading.Thread(target=lightSense, args=(lightWriter, lightSock, IS_STREAMING, IS_LOGGING))
        lightThread.setDaemon(True)
        
    if USE_ADC:
        soundSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tempSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        doorSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address_sound = (hostIP, BASE_PORT + 2)
        server_address_temp = (hostIP, BASE_PORT + 3)
        server_address_door = (hostIP, BASE_PORT + 4)
        print >>sys.stderr, 'connecting to %s port %s' % server_address_sound
        print >>sys.stderr, 'connecting to %s port %s' % server_address_temp
        print >>sys.stderr, 'connecting to %s port %s' % server_address_door
        soundSock.connect(server_address_sound)
        tempSock.connect(server_address_temp)
        doorSock.connect(server_address_door)
        # all sensors that use the ADC need to be managed by a single thread
        ADCThread = threading.Thread(target=soundSense, args = (tempWriter, soundWriter, soundSock, tempSock, doorWriter, doorSock, IS_STREAMING, IS_LOGGING))
        ADCThread.setDaemon(True)


# running the BBB without streaming is not well tested
else:
    if USE_ACCEL:
        accelThread = threading.Thread(target=shimmerSense, args=(accelWriter, None, ferror, SHIMMER_ID, IS_STREAMING, IS_LOGGING))
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
    while True:
        pass
    
except KeyboardInterrupt:
    print ""
    print "interrupted"
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
    print "Done"
