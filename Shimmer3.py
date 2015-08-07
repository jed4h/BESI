# Program to collect data from a Shimmer3 over Bluetooth
# Can log data to a file locally and/or stream to a host PC
# The shimmer ID is sent from the basestation
# the basestation IP is a user input 
 


#!/usr/bin/env python
from gpio_utils import *
from ShimmerBT import *
from Constants import *
from NTPTime import *
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
    ShimmerIDs.append(SHIMMER_BASE + ShimmerID3)
    # attempt to connect until successful
    while True:
        # need to create a new socket afer every disconnect/ failed connect
        conn, s = shimmer_connect(ShimmerIDs, PORT)
        if conn == 1:
            break
    
    # give sensors some time to start up
    time.sleep(1)
    print "Connect Est."
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
 
    ferror.write("Connection Established. Time: {}\n".format(actualTime))
           
    #if streaming:
    #    accelSock.sendall("Accelerometer" + actualTime + "\n")

    # get start time of the BBB clock to calculate time deltas        
    startTime = datetime.datetime.now()
    time.sleep(1)
    print "Sending Start Streaming Command"
    # send the start streaming command until successful
    while (startStreaming(s) == -1):
	pass
    
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
		    ferror.write("Connection Lost. Time: {}\n".format(actualTime))

            streamingError = 1
            print "error sampling accelerometers"
            if logging:
                # 0, 0, 0, 0 indicates lost connection
                writeAccel(accelWriter, [0], [0], [0] ,[0])
            if streaming:
		#string = packetize(struct.pack("HHHH", 0, 0, 0, 0))
                string = "{0:05d},{1:04d},{2:04d},{3:04d},\n".format(0,0,0,0)
		try:
                    accelSock.sendall(string)
		except:
		    sys.exit()
	    # create a new socket object because the old one cannot be used 
            s.close()
            #attempt to reconnect
            conn, s = shimmer_connect(ShimmerIDs, PORT)
            if (conn == 1):
		print "Connection Est."
                time.sleep(1)
		actualTime = -1
		while(actualTime == -1):
                	actualTime = getDateTime()
		# log reconnect events to a file
    		ferror.write("Connection Re-established. Time: {}\n".format(actualTime))

                if logging:
                    accelWriter.writerow(("Accelerometer", actualTime))
                print "Sending Start Streaming Command"
		while (startStreaming(s) == -1):
			pass
                streamingError = 0
            else:
                print "Error Connecting to Shimmer"
        else:
            #write accel values to a csv file
            if logging:
                writeAccel(accelWriter, timestamp, x_accel, y_accel, z_accel)
            
            if streaming:
                for i in range(len(z_accel)):
		    #string = packetize(struct.pack("HHHH", timestamp[i], x_accel[i], y_accel[i], z_accel[i]))
                    string = "{0:05d},{1:04d},{2:04d},{3:04d},\n".format(timestamp[i], x_accel[i], y_accel[i], z_accel[i])
                    if len(string) == 22:
			try:
                    	    accelSock.sendall(string)
			except:
			    sys.exit()
    
        time.sleep(LOOP_DELAY * UPDATE_DELAY)
        
