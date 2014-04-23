#application to interface with the LM60BIZ analog temperature sensor
# continouously samples and writes to the given csv
from gpio_utils import *
from ShimmerBT import *
from Constants import *
from NTPTime import *
import socket
import time
import csv


def MotionSense(motionWriter):
    lastMotion = 0
    
    gpio_input(MOTION_PIN)
    
    actualTime = getDateTime()
    motionWriter.writerow(("motion", actualTime))
    startTime = datetime.datetime.now()
    
    i=0
    while i < 100:
        i = i + 1
        
        
        
        currMotion = gpio_get_value(MOTION_PIN)
        # write times of changes in value to the csv file
        if currMotion != lastMotion:
            # calculate time since start
            currTime = datetime.datetime.now()
            currTimeDelta = (currTime - startTime).seconds + (currTime - startTime).microseconds / 1000000.0
            motionWriter.writerow(("{0:.2f}".format(currTimeDelta), "{0}".format(currMotion)))
        
        lastMotion = currMotion
        time.sleep(LOOP_DELAY)
     
fmotion = open("motion", 'w')
motionWriter = csv.writer(fmotion)
MotionSense(motionWriter)
fmotion.close()