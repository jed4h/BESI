from gpio_utils import *
from ShimmerBT import *
from Constants import *
from NTPTime import *
import socket
import time
import csv
import subprocess

#ftemp = open("temp_test", 'w')
#fsound = open("sound_test", "w")

#tempWriter = csv.writer(ftemp)
#soundWriter = csv.writer(fsound)

def soundSense(tempWriter, soundWriter,soundSock, tempSock, streaming = True, logging = True):
    actualTime = getDateTime()
    if logging:
        tempWriter.writerow(("Temperature", actualTime))
        soundWriter.writerow(("Noise Level", actualTime))
        
        startTime = datetime.datetime.now()
    
    while True:
        currTime = datetime.datetime.now()
        currTimeDelta = (currTime - startTime).seconds + (currTime - startTime).microseconds / 1000000.0
        
        proc = subprocess.Popen(["./ADC"], stdout=subprocess.PIPE,)
        output = proc.communicate()[0]
        split_output = output.split(',')
        
        for i in range((len(split_output) / 2) - 1):
            if logging:
                soundWriter.writerow((float(split_output[2 * i]) + currTimeDelta, split_output[2 * i + 1]))
                
            if streaming:
                soundSock.sendall("{0:015.4f},{1:05.2f},\n".format(float(split_output[2 * i]) + currTimeDelta, float(split_output[2 * i + 1])))
        
        (tempC, tempF) = calc_temp(float(split_output[-1]) * 1000)
        if logging:
            tempWriter.writerow(("{0}".format(split_output[-2]), "{0:.2f}".format(tempC), "{0:.2f}".format(tempF)))
            
        if streaming:
            tempSock.sendall("{0:0.4f},{1:03.2f},{2:03.2f},\n".format(float(split_output[-2]), tempC, tempF))
    
#ftemp.close()
#fsound.close()
#print "Done"

