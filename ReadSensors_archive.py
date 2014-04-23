#!/usr/bin/env python
from gpio_utils import *
from ShimmerBT import *
from Constants import *
import socket
import time
import csv


# reads analog in from temperature sensor connected to AIN0
# reads Montion sensor connected to GPIO0_7 and writes value to 
# LED coneected to GPIO1_28
# Light sensor connected to I2C bus 1
#   SCL             P9_19
#   SDA             P9_20
#   
#   LED             P9_12
#
#   TMP             P9_39
#
#   MOTION OUT      P9_42
#
#
#
#



i=0
streamingError = 0  # set to 1 if we lose connecting while streaming


ftemp = open("temp", 'w')
flight = open("light", "w")
faccel = open("accel", 'w')

accelWriter = csv.writer(faccel)
lightWriter = csv.writer(flight)
tempWriter = csv.writer(ftemp)

#initialize sensors
light_i2c = i2c_light_init(LIGHT_ADDR)
gpio_output("GPIO1_28")
gpio_input("GPIO0_7")
adc_setup()

s = lightblue.socket()
# attempt to connect until successful
while True:
    conn = shimmer_connect(s, SHIMMER_BASE + SHIMMER_ID, PORT)
    if conn == 1:
        break

# give sensors some time to start up
time.sleep(1)
startTime = datetime.datetime.now()

#write metadata at beginning of files (time and sensor for now)
accelWriter.writerow(("Accelerometer", startTime))
lightWriter.writerow(("Lux", startTime))
tempWriter.writerow(("temperature", startTime))

startStreaming(s)


try:
    while True:
        i = i + 1
        # temperary motion detector code
        if gpio_get_value("GPIO0_7"):
            gpio_set_value("GPIO1_28", 1)
        else:
            gpio_set_value("GPIO1_28", 0)
            
        if ((i % UPDATE_DELAY) == 0):
            # calculate time sonce start
            currTime = datetime.datetime.now()
            currTimeDelta = (currTime - startTime).seconds + (currTime - startTime).microseconds / 1000000.0
            #read temperature sensor
            (tempC, tempF) = calc_temp(adc_get_value("AIN0"))
            tempWriter.writerow(("{0:.2f}".format(currTimeDelta), "{0:.2f}".format(tempC), "{0:.2f}".format(tempF)))
           
            #read light sensor
            #error reading i2c bus. Try to reinitialize sensor
            lightLevel = lux_calc(light_i2c.readU16(LIGHT_REG_LOW), light_i2c.readU16(LIGHT_REG_HIGH))
            if lightLevel == -1:
                light_i2c = i2c_light_init(LIGHT_ADDR)
                
            lightWriter.writerow(("{0:.2f}".format(currTimeDelta), "{0:.2f}".format(lightLevel)))
            
            #read accelerometers from shimmer
            print "querying shimmer"
            
            try:
                if streamingError == 0:
                    (timestamp, x_accel, y_accel, z_accel) = sampleAccel(s)
                else:
                    raise socket.error
            # if the connection is lost: close the socket, create an new one and try to reconnect
            except socket.error:
                streamingError = 1
                print "error sampling accelerometers"
                s.close()
                s = lightblue.socket()
                #attempt to reconnect
                if (shimmer_connect(s, SHIMMER_BASE + SHIMMER_ID, PORT) == 1):
                    time.sleep(1)
                    startStreaming(s)
                    streamingError = 0
                print "Error Connecting to Shimmer"
            else:
                #wire accel values to a csv file
                writeAccel(accelWriter, timestamp, x_accel, y_accel, z_accel)
    
        time.sleep(LOOP_DELAY)
    
except KeyboardInterrupt:
    print "interrupted"
finally:
    ftemp.close()
    flight.close()
    faccel.close()
    print "Done"