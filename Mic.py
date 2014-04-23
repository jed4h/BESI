from gpio_utils import *
from ShimmerBT import *
from Constants import *
from NTPTime import *
import socket
import time
import csv
import subprocess


def soundSense():
    actualTime = getDateTime()
    subprocess.call(["./ADC", "{0}".format(actualTime)])
