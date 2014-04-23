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

#host = '172.25.98.25'


ftemp = open("temp", "w")
flight = open("light", "w")
faccel = open("accel", "w")
fsound = open("sound", "w")
ferror = open("error", "w")

accelWriter = csv.writer(faccel)
lightWriter = csv.writer(flight)
tempWriter = csv.writer(ftemp)
soundWriter = csv.writer(fsound)

#stream to base station 
if IS_STREAMING:

    if USE_ACCEL:
        # create socket
        accelSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # create socket address to send data to base station
        server_address_accel = (HOST, BASE_PORT)
        print >>sys.stderr, 'connecting to %s port %s' % server_address_accel
        # connect to base station
        accelSock.connect(server_address_accel)
        # create a thread to communicate with Shimmer3 and base station
        accelThread = threading.Thread(target=shimmerSense, args=(accelWriter,accelSock, ferror,  IS_STREAMING, IS_LOGGING))
        # Thread will stop when parent is stopped
        accelThread.setDaemon(True)
        
    if USE_LIGHT:
        lightSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address_light = (HOST, BASE_PORT + 1)
        print >>sys.stderr, 'connecting to %s port %s' % server_address_light
        lightSock.connect(server_address_light)
        lightThread = threading.Thread(target=lightSense, args=(lightWriter, lightSock, IS_STREAMING, IS_LOGGING))
        lightThread.setDaemon(True)
        
    if USE_ADC:
        soundSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tempSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address_sound = (HOST, BASE_PORT + 2)
        server_address_temp = (HOST, BASE_PORT + 3)
        print >>sys.stderr, 'connecting to %s port %s' % server_address_sound
        print >>sys.stderr, 'connecting to %s port %s' % server_address_temp
        soundSock.connect(server_address_sound)
        tempSock.connect(server_address_temp)
        # all sensors that use the ADC need to be managed by a single thread
        ADCThread = threading.Thread(target=soundSense, args = (tempWriter, soundWriter, soundSock, tempSock, IS_STREAMING, IS_LOGGING))
        ADCThread.setDaemon(True)

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
    if IS_STREAMING:
        accelSock.close()
        lightSock.close()
        soundSock.close()
        tempSock.close()
    print "Done"
