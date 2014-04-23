#application to interface with the LM60BIZ analog temperature sensor
# continouously samples and writes to the given csv
##############
##Deprecated##
##############
from gpio_utils import *
from ShimmerBT import *
from Constants import *
from NTPTime import *
import socket
import time
import csv



def tempSense(tempWriter):
    adc_setup()
    
    actualTime = getDateTime()
    tempWriter.writerow(("temperature", actualTime))
    startTime = datetime.datetime.now() # used to calculate time deltas
    
    while True:
        # calculate time since start
        currTime = datetime.datetime.now()
        currTimeDelta = (currTime - startTime).seconds + (currTime - startTime).microseconds / 1000000.0
        # read temperature sensor
        (tempC, tempF) = calc_temp(adc_get_value(TEMP_PIN))
        tempWriter.writerow(("{0:.2f}".format(currTimeDelta), "{0:.2f}".format(tempC), "{0:.2f}".format(tempF)))
        time.sleep(LOOP_DELAY * UPDATE_DELAY)
        
'''      
ftemp = open("temp", 'w')
tempWriter = csv.writer(ftemp)
tempSense(tempWriter)
'''
