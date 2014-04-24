#!/usr/bin/env python
import Adafruit_BBIO.GPIO as GPIO
import time
import Adafruit_BBIO.ADC as ADC
import datetime
import math
from Adafruit_I2C import Adafruit_I2C

# adds a length field at the beginning of the data string
def packetize(data):
	lenHeader = "{0:04},".format(len(data))
	return lenHeader + data
	

def gpio_output(pin):
        GPIO.setup(pin, GPIO.OUT)

def gpio_input(pin):
        GPIO.setup(pin, GPIO.IN)

def gpio_set_value(pin, value):
        if value == 0:
                GPIO.output(pin, GPIO.LOW)
        else:
                GPIO.output(pin, GPIO.HIGH)

def gpio_get_value(pin):
        if GPIO.input(pin):
                return 1
        else:
                return 0
def cleanup():
        GPIO.cleanup()

def adc_setup():
        ADC.setup()

def adc_get_value(chan):
        return ADC.read(chan) * 1800

def calc_temp(mv):
        temp_c = (mv - 424)/6.25
        temp_f = (temp_c * 1.8) + 32
        return (temp_c, temp_f)
def i2c_light_init(addr):
        i2c =  Adafruit_I2C(addr)
        i2c.write8(0x80, 3) # initialize sensor
        i2c.write8(0x81, 16 + 2) # set Integration time to 402ms and gain to 16x
        return i2c

def lux_calc(ch0, ch1):
        #constants for lux algorithm
        RATIO1 = 0.50   
        RATIO2 = 0.61
        RATIO3 = 0.80
        RATIO4 = 1.30
        
        COEFF11 = 0.0304
        COEFF12 = 0.0620
        COEFF21 = 0.0224
        COEFF22 = 0.0310
        COEFF31 = 0.0128
        COEFF32 = 0.0153
        COEFF41 = 0.00146
        COEFF42 = 0.00112
        
        EXP = 1.4
        
        if ch0 > 0:
            ratio = float(ch1)/ch0
            if ratio <= RATIO1:
                return COEFF11 * ch0 - COEFF12 * ch0 * math.pow(ratio, EXP)
                
            elif ratio <= RATIO2:
                return COEFF21 * ch0 - COEFF22 * ch1
                
            elif ratio <= RATIO3:
                return COEFF31 * ch0 - COEFF32 * ch1
                
            elif ratio <= RATIO4:
                return COEFF41 * ch0 - COEFF42 * ch1
                
            elif ratio > RATIO4:
                return 0.0
        else:
            return -1.0
            
        
