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
#   SCL             P9_19
#   SDA             P9_20
#   
#   LED             P9_12
#
#   TMP             P9_39
#
#   microphone      P9_40
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

accelWriter = csv.writer(faccel)
lightWriter = csv.writer(flight)
tempWriter = csv.writer(ftemp)
soundWriter = csv.writer(fsound)

if IS_STREAMING:
    #stream to base station instead of write to file
    if USE_ACCEL:
        accelSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if USE_LIGHT:
        lightSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if USE_ADC:
        soundSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tempSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    if USE_ACCEL:
        server_address_accel = (HOST, BASE_PORT)
    if USE_LIGHT:
        server_address_light = (HOST, BASE_PORT + 1)
    if USE_ADC:
        server_address_sound = (HOST, BASE_PORT + 2)
        server_address_temp = (HOST, BASE_PORT + 3)
    
    if USE_ACCEL:
        print >>sys.stderr, 'connecting to %s port %s' % server_address_accel
    if USE_LIGHT:
        print >>sys.stderr, 'connecting to %s port %s' % server_address_light
    if USE_ADC:
        print >>sys.stderr, 'connecting to %s port %s' % server_address_sound
        print >>sys.stderr, 'connecting to %s port %s' % server_address_temp
    
    if USE_ACCEL:
        accelSock.connect(server_address_accel)
    if USE_LIGHT:
        lightSock.connect(server_address_light)
    if USE_ADC:
        soundSock.connect(server_address_sound)
        tempSock.connect(server_address_temp)

# create a thread to manage each sensor
if USE_ACCEL:
    accelThread = threading.Thread(target=shimmerSense, args=(accelWriter,accelSock, streaming = IS_STREAMING, logging = IS_LOGGING))
    accelThread.setDaemon(True)
if USE_LIGHT:
    lightThread = threading.Thread(target=lightSense, args=(lightWriter, lightSock, streaming = IS_STREAMING, logging = IS_LOGGING))#tempThread = threading.Thread(target=tempSense, args=(tempWriter,))
    lightThread.setDaemon(True)
if USE_ADC:
    ADCThread = threading.Thread(target=soundSense, args = (tempWriter, soundWriter, soundSock, tempSock, streaming = IS_STREAMING, logging = IS_LOGGING))
    ADCThread.setDaemon(True)





# trap keyboard interrupt
try:
    lightThread.start()
    accelThread.start()
    ADCThread.start()
    while True:
        pass
    
except KeyboardInterrupt:
    print ""
    print "interrupted"
finally:
    
    ftemp.close()
    flight.close()
    faccel.close()
    fsound.close()
    accelSock.close()
    lightSock.close()
    soundSock.close()
    tempSock.close()
    print "Done"