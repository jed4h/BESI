from gpio_utils import *
from ShimmerBT import *
from Constants import *
from NTPTime import *
import socket
import time
import csv
import subprocess
import sys

#ftemp = open("temp_test", 'w')
#fsound = open("sound_test", "w")

#tempWriter = csv.writer(ftemp)
#soundWriter = csv.writer(fsound)

# gets sensor values from the temperature sensor and the microphone, writes the data to a file and sends the data over a socket
def soundSense(tempWriter, soundWriter,soundSock, tempSock, doorWriter, doorSock, streaming = True, logging = True):

    # NTP server request occasionally fails even if the BBB is connected to the internet. Run NTP check until we get a response    
    actualTime = -1
    while(actualTime == -1):
	actualTime = getDateTime()
    if logging:
        tempWriter.writerow(("Temperature", actualTime))
        soundWriter.writerow(("Noise Level", actualTime))
	doorWriter.writerow(("Door Motion Sensor", actualTime))
        
	# get the start time according to the BeagleBone. This time is only useful for detirmining time deltas
        startTime = datetime.datetime.now()
    
    while True:
	# calculate the time since the start of the data collection
        currTime = datetime.datetime.now()
        currTimeDelta = (currTime - startTime).days * 86400 + (currTime - startTime).seconds + (currTime - startTime).microseconds / 1000000.0
        
        # run the c code to get one second of data from the ADC
        proc = subprocess.Popen(["./ADC1"], stdout=subprocess.PIPE,)
	# anything printed in ADC.c is captured in output
        output = proc.communicate()[0]
        split_output = output.split(',')
        
	# data is in <timestamp>,<value> format
	# 100 samples/second from the mic and 1 sample/sec from the temperature sensor
	i = 0 
        while (i < (len(split_output) / 2 - 1)):
	    # every 11th sample is from the door sensor
	    if (((i + 1) % 12) == 11):
		if logging:
		    doorWriter.writerow((float(split_output[2 * i - 2]) + currTimeDelta, split_output[2 * i - 1]))
		    doorWriter.writerow((float(split_output[2 * i]) + currTimeDelta, split_output[2 * i + 1]))
		
		if streaming:
		    try:
		    	doorSock.sendall("{0:015.4f},{1:06.2f},{2:06.2f},\n".format(float(split_output[2 * i - 2]) + currTimeDelta,
				     	 float(split_output[2 * i - 1]),float(split_output[2 * i + 1])))
		   # doorSock.sendall("{0:015.4f},{1:06.2f},\n".format(float(split_output[2 * i]) + currTimeDelta, float(split_output[2 * i + 1])))
		    except:
			sys.exit()
		i = i + 1

	    else:		
            	if logging:
		    soundWriter.writerow((float(split_output[2 * i]) + currTimeDelta, split_output[2 * i + 1]))
                
        	if streaming:
		    try:
                    	soundSock.sendall("{0:015.4f},{1:06.2f},\n".format(float(split_output[2 * i]) + currTimeDelta, float(split_output[2 * i + 1])))
                    	#soundSock.sendall(packetize(struct.pack("ff",float(split_output[2 * i]) + currTimeDelta, float(split_output[2 * i + 1]))))
		    except:
			sys.exit()

	    i = i + 1
        
	# send 1 semple from the temperature sensor
        (tempC, tempF) = calc_temp(float(split_output[-1]) * 1000)
        if logging:
            tempWriter.writerow(("{0}".format(float(split_output[-2]) + currTimeDelta), "{0:.2f}".format(tempC), "{0:.2f}".format(tempF)))
            
        if streaming:
	    try:
            	tempSock.sendall("{0:0.4f},{1:03.2f},{2:03.2f},\n".format(float(split_output[-2]) + currTimeDelta, tempC, tempF))
            	#tempSock.sendall(struct.pack("fff", float(split_output[-2]) + currTimeDelta, tempC, tempF))
	    except:
		sys.exit()    


#ftemp.close()
#fsound.close()
#print "Done"

