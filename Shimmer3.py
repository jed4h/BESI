# Program to collect data from a Shimmer3 over Bluetooth
# Can log data to a file logally and/or stream to a host PC
# The shimmer ID and host addr. are hardcoded and need to be changed for
# different deployments


#!/usr/bin/env python
from gpio_utils import *
from ShimmerBT import *
from Constants import *
from NTPTime import *
import socket
import time
import csv


def shimmerSense(accelWriter, accelSock, streaming = True, logging = True):
    streamingError = 0  # set to 1 if we lose connecting while streaming
    
    
    # attempt to connect until successful
    while True:
        # need to create a new socket afer every disconnect/ failed connect
        s = lightblue.socket()
        conn = shimmer_connect(s, SHIMMER_BASE + SHIMMER_ID, PORT)
        if conn == 1:
            break
    
    # give sensors some time to start up
    time.sleep(1)
    #read calibration info
    try:            #disconnect while reading calib info can cause exception. Ignore for now
        calib = readCalibInfo(s)
    except:
        pass
    #calib.printCalib()
    #time.sleep(1)
    
    #write metadata at beginning of files (time and sensor for now)
    actualTime = getDateTime()
    if logging:
        accelWriter.writerow(("Accelerometer", actualTime))
        
    if streaming:
        accelSock.sendall("Accelerometer" + actualTime + "\n")
        
    startTime = datetime.datetime.now()
    time.sleep(1)
    startStreaming(s)
    
    while True:
        try:
            if streamingError == 0:
                (timestamp, x_accel, y_accel, z_accel) = sampleAccel(s)
            else:
                raise socket.error
            # if the connection is lost: close the socket, create an new one and try to reconnect
        except socket.error:
            streamingError = 1
            print "error sampling accelerometers"
            if logging:
                # 0, 0, 0, 0 indicates lost connection
                writeAccel(accelWriter, [0], [0], [0] ,[0])
            if streaming:
                string = "{0:05d},{1:04d},{2:04d},{3:04d},\n".format(0,0,0,0)
                accelSock.sendall(string)
            s.close()
            s = lightblue.socket()
            #attempt to reconnect
            if (shimmer_connect(s, SHIMMER_BASE + SHIMMER_ID, PORT) == 1):
                time.sleep(1)
                actualTime = getDateTime()
                if logging:
                    accelWriter.writerow(("Accelerometer", actualTime))
                startStreaming(s)
                streamingError = 0
            else:
                print "Error Connecting to Shimmer"
        else:
            #write accel values to a csv file
            if logging:
                writeAccel(accelWriter, timestamp, x_accel, y_accel, z_accel)
            
            if streaming:
                for i in range(len(z_accel)):
                    string = "{0:05d},{1:04d},{2:04d},{3:04d},\n".format(timestamp[i], x_accel[i], y_accel[i], z_accel[i])
                    if len(string) == 22:
                        accelSock.sendall(string)
    
        time.sleep(LOOP_DELAY * UPDATE_DELAY)
        