#code to interface with the TSL2561 ambient light sensor over i2c
# continuously samples lux semsor and writes result to given can write
from gpio_utils import *
from Constants import *
from NTPTime import *
import time
import csv

def lightSense(lightWriter):
    light_i2c = i2c_light_init(LIGHT_ADDR)
    actualTime = getDateTime()
    lightWriter.writerow(("Lux", actualTime))
    startTime = datetime.datetime.now()
    
    while True:
        # calculate time since start
        currTime = datetime.datetime.now()
        currTimeDelta = (currTime - startTime).seconds + (currTime - startTime).microseconds / 1000000.0
        # read light sensor
        # error reading i2c bus. Try to reinitialize sensor
        lightLevel = lux_calc(light_i2c.readU16(LIGHT_REG_LOW), light_i2c.readU16(LIGHT_REG_HIGH))
        if lightLevel == -1:
            light_i2c = i2c_light_init(LIGHT_ADDR)
                
        lightWriter.writerow(("{0:.2f}".format(currTimeDelta), "{0:.2f}".format(lightLevel)))
        time.sleep(LOOP_DELAY * UPDATE_DELAY)
        
        
