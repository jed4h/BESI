from gpio_utils import *
from ShimmerBT import *
from Constants import *
from NTPTime import *
import socket
import time
import csv
#application to interface with the LM60BIZ analog temperature sensor
# continouously samples and writes to the given csv
from gpio_utils import *
from ShimmerBT import *
from Constants import *
from NTPTime import *
import socket
import time
import csv



def soundSense(soundWriter):
    adc_setup()
    
    actualTime = getDateTime()
    soundWriter.writerow(("sound", actualTime))
    startTime = datetime.datetime.now() # used to calculate time deltas
    
    while True:
        # calculate time since start
        currTime = datetime.datetime.now()
        currTimeDelta = (currTime - startTime).seconds + (currTime - startTime).microseconds / 1000000.0
        # read temperature sensor
        sound = adc_get_value("AIN1")
        soundWriter.writerow(("{0:.5f}".format(currTimeDelta), "{0:.2f}".format(sound)))
        #tempWriter.writerow(("{0:.5f}".format(currTimeDelta), 0, 0))
        #time.sleep(LOOP_DELAY * UPDATE_DELAY)
        
    
fsound = open("adc_test", 'w')
soundWriter = csv.writer(fsound)
try:
    soundSense(soundWriter)
except KeyboardInterrupt:
    print ""
    print "interrupted"
finally:
    fsound.close()
    print "Done"