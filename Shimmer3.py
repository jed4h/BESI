# Program to collect data from a Shimmer3 over Bluetooth
# Can log data to a file locally and/or stream to a host PC
# The shimmer ID is sent from the basestation
# the basestation IP is a user input 
 


#!/usr/bin/env python
from gpio_utils import *
from ShimmerBT import *
from Constants import *
from NTPTime import *
import subprocess
import socket
import time
import csv
import struct
import sys


def shimmerSense(accelWriter, accelSock, ferror, ShimmerID, ShimmerID2, ShimmerID3, streaming = True, logging = True):
    streamingError = 0  # set to 1 if we lose connecting while streaming

    ShimmerIDs = []
    ShimmerIDs.append(SHIMMER_BASE + ShimmerID)
    ShimmerIDs.append(SHIMMER_BASE + ShimmerID2)
    #ShimmerIDs.append(SHIMMER_BASE + ShimmerID3)

    accelSock.settimeout(0.0)

    # attempt to connect until successful
    while True:
        # need to create a new socket afer every disconnect/ failed connect
	for addr in ShimmerIDs:
        	conn, s, connID = shimmer_connect([addr], PORT)
        if conn == 1:
            break
        
	string = struct.pack("HHHHh",0,0,0,0,0)   
	#string = "{0:05d},{1:04d},{2:04d},{3:04d},{4:03d},\n".format(0,0,0,0,0)
    	try:
	    accelSock.sendall(string + "~~")
	    accelSock.recv(2048)
	except:
	    print "wifi connection error"
	    sys.exit()
	time.sleep(5)

    # give sensors some time to start up
    time.sleep(1)
    print "Connect Est. to {}".format(connID)
    #read calibration info
    #try:            #disconnect while reading calib info can cause exception. Ignore for now
    #calib = readCalibInfo(s)
    #except:
    #    pass
    #calib.printCalib()
    #time.sleep(1)
    
    #write metadata at beginning of files (time and sensor for now)
    actualTime = -1
    while(actualTime == -1):
    	actualTime = getDateTime()
    if logging:
        accelWriter.writerow(("Accelerometer", actualTime))
 
    ferror.write("Connection Established to {}. Time: {}\n".format(connID, actualTime))
           
    #if streaming:
    #    accelSock.sendall("Accelerometer" + actualTime + "\n")

    # get start time of the BBB clock to calculate time deltas        
    startTime = datetime.datetime.now()
    time.sleep(1)
    print "Sending Start Streaming Command"
    # try sending start streaming command 10 times
    streamingError = 1
    for attempt in range(10):
    	if (startStreaming(s) != -1):
	    streamingError = 0
	    break
    #while (startStreaming(s) == -1):
    #	pass		
    
    while True:
	# if an exception is raised receiving data or connection is lost (streamingError == 1) try to reconnect
        try:
            if streamingError == 0:
                (timestamp, x_accel, y_accel, z_accel) = sampleAccel(s)
            else:
                raise socket.error
            # if the connection is lost: close the socket, create an new one and try to reconnect
        except socket.error:
	    if streamingError == 0:
		    actualTime = -1
		    while(actualTime == -1):
			actualTime = getDateTime()
		    # log every disconnect event in a file
		    ferror.write("Connection Lost from {}. Time: {}\n".format(connID, actualTime))

            streamingError = 1
            print "error sampling accelerometers"
            if logging:
                # 0, 0, 0, 0 indicates lost connection
                writeAccel(accelWriter, [0], [0], [0] ,[0])
            if streaming:
		string = struct.pack("HHHHh",0,0,0,0,0)
		#string = packetize(struct.pack("HHHH", 0, 0, 0, 0))
                #string = "{0:05d},{1:04d},{2:04d},{3:04d},\n".format(0,0,0,0)
		try:
                    accelSock.sendall(string + "~~")
		except:
		    sys.exit()
	    # create a new socket object because the old one cannot be used 
            s.close()
            #attempt to reconnect
            conn, s, connID = shimmer_connect(ShimmerIDs, PORT)
            if (conn == 1):
		print "Connection Est. to {}".format(connID)
                time.sleep(1)
		actualTime = -1
		while(actualTime == -1):
                	actualTime = getDateTime()
		# log reconnect events to a file
    		ferror.write("Connection Re-established to {}. Time: {}\n".format(connID, actualTime))

                if logging:
                    accelWriter.writerow(("Accelerometer", actualTime))
                print "Sending Start Streaming Command"
		for attempt in range(10):
		    if (startStreaming(s) != -1):
                	streamingError = 0
			break	
		#while (startStreaming(s) == -1):
		#	pass
            else:
                print "Error Connecting to Shimmer"
        else:
            #write accel values to a csv file
            if logging:
                writeAccel(accelWriter, timestamp, x_accel, y_accel, z_accel)
		#frssi = open("rssi", "a")
		rssi_reading = subprocess.check_output(["hcitool","rssi","{}".format(connID)])
		rssi_int = int(rssi_reading.split(":")[1].rstrip())
		#frssi.close()            

            if streaming:
                for i in range(len(z_accel)/2):
		    string = struct.pack("HHHHh", timestamp[2*i], x_accel[2*i], y_accel[2*i], z_accel[2*i], rssi_int)
		    #string = packetize(struct.pack("HHHH", timestamp[i], x_accel[i], y_accel[i], z_accel[i]))
                    #string = "{0:05d},{1:04d},{2:04d},{3:04d},{4:03d},\n".format(timestamp[i], x_accel[i], y_accel[i], z_accel[i], rssi_int)
                    #if len(string) == 22 + 4:
		    if True:
			try:
                    	    accelSock.sendall(string + "~~")
			except:
			    sys.exit()
    
        time.sleep(LOOP_DELAY * UPDATE_DELAY)
        try:
		accelSock.recv(2048)
	except:
		print "exiting accelThread"
		sys.exit()
	
