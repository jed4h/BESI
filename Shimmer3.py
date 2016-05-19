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


def shimmerSense(accelWriter, accelSock, ferror, ShimmerID, ShimmerID2, ShimmerID3, streaming = True, logging = True, startDateTime = "0"):
    streamingError = 0  # set to 1 if we lose connecting while streaming

    # counts seconds to check for ack from basestation
    noRecvCount = 0

    ShimmerIDs = []
    ShimmerIDs.append(SHIMMER_BASE + ShimmerID)
    ShimmerIDs.append(SHIMMER_BASE + ShimmerID2)
    #ShimmerIDs.append(SHIMMER_BASE + ShimmerID3)

    accelSock.settimeout(0.0)

    ferror.write(startDateTime + "\n")

    # attempt to connect until successful
    while True:
	conn, s, connID = shimmer_connect(ShimmerIDs, PORT)
        # need to create a new socket afer every disconnect/ failed connect
	#for addr in ShimmerIDs:
        #	conn, s, connID = shimmer_connect([addr], PORT)
        #	if conn == 1:
         #   		break
	#	else:
	#	    time.sleep(5)		    
	#time.sleep(5)
	if conn == 1:
		break
	else:
	    time.sleep(5)

	string = struct.pack("HHHHh",0,0,0,0,0)   
	#string = "{0:05d},{1:04d},{2:04d},{3:04d},{4:03d},\n".format(0,0,0,0,0)
    	try:
	    accelSock.sendall(string + "~~")
	    #accelSock.recv(2048)
	except:
	    print "wifi connection error"
	    sys.exit()
	
	if noRecvCount == 2:
	    try:
		accelSock.recv(2048)
	    except:
		print "exiting Accel"
		sys.exit()
	    else:
		noRecvCount = 0

	#time.sleep(5)
	noRecvCount = noRecvCount + 1

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

    startTime = datetime.datetime.now() 
    ferror.write("Connection Established to {}. Time: {}\n".format(connID, datetime.datetime.now()-startTime))
           
    #if streaming:
    #    accelSock.sendall("Accelerometer" + actualTime + "\n")

    # get start time of the BBB clock to calculate time deltas        
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
    
    string = struct.pack("HHHHh",0,0,0,0,0)   
    try:
    	accelSock.sendall(string + "~~")
    except:
    	print "wifi connection error"
    	sys.exit()
    
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
		    ferror.write("Connection Lost from {}. Time: {}\n".format(connID, datetime.datetime.now()-startTime))

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
		    print "Exiting Accel on Send"
		    sys.exit()
	    # create a new socket object because the old one cannot be used
	    # close the socket if whe still have a reference to it 
            try:
		s.close()
	    except:
		pass

            #attempt to reconnect
            conn, s, connID = shimmer_connect(ShimmerIDs, PORT)
            #for addr in ShimmerIDs:
	    #	conn,s,connID = shimmer_connect([addr], PORT)
	    #	if conn == 1:
	#	    break
	#	else:
	#	    time.sleep(5)

	    if (conn == 1):
		print "Connection Est. to {}".format(connID)
                time.sleep(1)
		actualTime = -1
		while(actualTime == -1):
                	actualTime = getDateTime()
		# log reconnect events to a file
    		ferror.write("Connection Re-established to {}. Time: {}\n".format(connID, datetime.datetime.now()-startTime))

                if logging:
                    accelWriter.writerow(("Accelerometer", actualTime))
                print "Sending Start Streaming Command"
		for attempt in range(10):
		    if (startStreaming(s) != -1):
                	streamingError = 0
                	string = struct.pack("HHHHh",0,0,0,0,0)   
    			try:
    			     accelSock.sendall(string + "~~")
    			except:
    			    print "wifi connection error"
    			    sys.exit()
			break	
		#while (startStreaming(s) == -1):
		#	pass
            else:
                print "Error Connecting to Shimmer"
		noRecvCount += 10
		time.sleep(5)
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
			    print "Exiting acel on Send"
			    sys.exit()
    
        time.sleep(0.5)
        
	if noRecvCount >= 30:
	    try:
		accelSock.recv(2048)
		noRecvCount = 0
	    except:
		print "exiting accel on recv"
		sys.exit()
	
	noRecvCount = noRecvCount + 1
