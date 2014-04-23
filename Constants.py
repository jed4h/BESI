#Constants
SHIMMER_BASE = "00:06:66:66:"   # base bt address of Shimmer        
SHIMMER_ID = "94:A0"            # varies among shimmers
PORT = 1                        # common to all shimmers
LIGHT_ADDR = 0x39               # i2c address of light sensor
LIGHT_REG_LOW = 0xAC            # address of low bits of lux value
LIGHT_REG_HIGH = 0xAE           # address of low bits of lux value
UPDATE_DELAY = 10               # number of loop iterations between reading sensors
LOOP_DELAY = 0.1                # loop time in seconds
TEMP_PIN = "AIN6"               # ADC pin for temperature sensor input
MOTION_PIN = "P9_42"            # Montio detector out pin