from gpio_utils import *
from ShimmerBT import *
from Constants import *
from NTPTime import *
import socket
import time
import csv
import subprocess


#def soundSense(temp_writer, sound_writer, adcSock):
proc = subprocess.Popen(["./ADC"], stdout=subprocess.PIPE,)
output = proc.communicate()[0]
split_output = output.split(',')

for i in range((len(split_output) / 2) - 1):
    
    sound_writer.writerow(split_output[2 * i], split_output[2 * i + 1])

    temp_writer.writerow(split_output[-2], split_output[-1]


