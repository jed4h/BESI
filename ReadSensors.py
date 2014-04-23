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
#   MOTION OUT      P9_42
#
#
#
#



i=0
streamingError = 0  # set to 1 if we lose connecting while streaming


ftemp = open("temp", 'w')
flight = open("light", "w")
faccel = open("accel", 'w')

accelWriter = csv.writer(faccel)
lightWriter = csv.writer(flight)
tempWriter = csv.writer(ftemp)

# create a thread to manage each sensor
lightThread = threading.Thread(target=lightSense, args=(lightWriter,))
tempThread = threading.Thread(target=tempSense, args=(tempWriter,))
accelThread = threading.Thread(target=shimmerSense, args=(accelWriter,))
soundThread = threading.Thread(target=soundSense)

lightThread.setDaemon(True)
#tempThread.setDaemon(True)
accelThread.setDaemon(True)
soundThread.setDaemon(True)

# trap keyboard interrupt
try:
    lightThread.start()
#    tempThread.start()
    accelThread.start()
    soundThread.start()
    while True:
        pass
    
except KeyboardInterrupt:
    print ""
    print "interrupted"
finally:
    
    ftemp.close()
    flight.close()
    faccel.close()
    print "Done"