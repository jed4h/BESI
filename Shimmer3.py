#!/usr/bin/env python
from gpio_utils import *
from ShimmerBT import *
from Constants import *
from NTPTime import *
import socket
import time
import csv

def shimmerSense(accelWriter, accelSock):
    streamingError = 0  # set to 1 if we lose connecting while streaming
    lastTimeStamp = 0
    
    s = lightblue.socket()
    # attempt to connect until successful
    while True:
        conn = shimmer_connect(s, SHIMMER_BASE + SHIMMER_ID, PORT)
        if conn == 1:
            break
    
    # give sensors some time to start up
    time.sleep(1)
    #read calibration info
    calib = readCalibInfo(s)
    #calib.printCalib()
    #time.sleep(1)
    
    #write metadata at beginning of files (time and sensor for now)
    actualTime = getDateTime()
    accelWriter.writerow(("Accelerometer", actualTime))
    #accelSock.sendall("Accelerometer" + actualTime + "\n")
    startTime = datetime.datetime.now()
    #time.sleep(1)
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
            writeAccel(accelWriter, [0], [0], [0] ,[0])
            s.close()
            s = lightblue.socket()
            #attempt to reconnect
            if (shimmer_connect(s, SHIMMER_BASE + SHIMMER_ID, PORT) == 1):
                time.sleep(1)
                actualTime = getDateTime()
                accelWriter.writerow(("Accelerometer", actualTime))
                startStreaming(s)
                streamingError = 0
            else:
                print "Error Connecting to Shimmer"
        else:
            #write accel values to a csv file
            writeAccel(accelWriter, timestamp, x_accel, y_accel, z_accel)
            
            for i in range(len(z_accel)):
                accelSock.sendall("{0:05d},{1:04d},{2:04d},{3:04d},\n".format(timestamp[i], x_accel[i], y_accel[i], z_accel[i]))
            #accelSock.sendall("{0}\n".format(timestamp))
            #accelSock.sendall("{0}\n".format(x_accel))
            #accelSock.sendall("{0}\n".format(y_accel))
            #accelSock.sendall("{0}\n".format(z_accel))
    
        time.sleep(LOOP_DELAY * UPDATE_DELAY)
        