import lightblue
import binascii
import struct
import time
import socket as Socket

# accelerometer packet format is:
# 0  |  timestamp_low  |  timestamp_high  |  x_accel_low  |  x_accel_high ...



#connects to a shimmer with the given address
def shimmer_connect(socket, addr, port):
    deviceFound = 1
    print "attempting to connect"
    # HDE Bluetooth dongle does not find shimmer, but can connect
    #devices = lightblue.finddevices()
  
   #for device in devices:
    #        if device[0] == addr:
     #           deviceFound = 1
    
        
    if deviceFound == 1:   
        #attemp to connect to shimmer    
        try:
            socket.connect((addr, port))
            toggleLED(socket)
            time.sleep(1)
            toggleLED(socket)
            socket.settimeout(0)    # make receive nonblocking
            print "successfully connected"
            return 1
        except Socket.error:
            print "failed to connect"
            return 0
    else:
        print "failed to find device"
        return 0
        
        
        
def startStreaming(socket):
    socket.send("\x07")
    if struct.unpack('B',socket.recv(1))[0] == 255:
        print "Started Streaming..."
    
    
def stopStreaming(socket):
    socket.send("\x20")
    
    
def toggleLED(socket):
    socket.send("\x06")
    
# reads accelerometer data from the Bluetooth
#returns lists of timestamps and accel. data
def sampleAccel(socket):
    maxSize = 1000      #1000 / 51.2Hz sampling rate * 9 bytes/sample = 2.17 seconds of data
    start = 0
    timestamp = []
    x_accel = []
    y_accel = []
    z_accel = []
    
    data = socket.recv(maxSize)
    sizeRecv = len(data)
    accel_tuple = struct.unpack('B'*sizeRecv, data)
    
    # find the start of a packet
    for byte in accel_tuple:
        start = start + 1
        if byte == 0:
            break
        
    for i in range(sizeRecv-start):
       # print "i = {0}".format(i)
        if (i % 9) == 1:
            timestamp.append((accel_tuple[i + start]<< 8) + accel_tuple[i-1 + start]) 

        if (i % 9) == 3:
            x_accel.append((accel_tuple[i + start]<< 8) + accel_tuple[i-1 + start])

        if (i % 9) == 5:
            y_accel.append((accel_tuple[i + start]<< 8) + accel_tuple[i-1 + start])

        if (i % 9) == 7:
            z_accel.append((accel_tuple[i + start]<< 8) + accel_tuple[i-1 + start])


        #for val in range(len(z_accel)):
        #    print("{0} {1} {2} {3}".format(timestamp[val], x_accel[val], y_accel[val], z_accel[val]))
            
    return timestamp, x_accel, y_accel, z_accel

def writeAccel(accelWriter, timestamp, x_accel, y_accel, z_accel):
    for value in range(len(z_accel)):
        accelWriter.writerow((timestamp[value], x_accel[value], y_accel[value], z_accel[value]))
        

# get the LNA calibration data from the shimmer
# calib message format is ACK | 0x12 | X Offset | Y Offset | Z Offset | X Sens | Y Sens | Z Sens | Alignment Matrix
# Assumes allisgment is 1 0 0
#                       0 1 0
#                       0 0 1
def readCalibInfo(socket):
    messageLen = 23
    base = 0    #in some test cases an extra 0xff byte is read at the beginning
  
    time.sleep(0.5)
    socket.send("\x13")
    time.sleep(0.5) 
    data = socket.recv(messageLen)
    calib_tuple = struct.unpack('B'*messageLen, data)
    #print calib_tuple
    Xoff = (calib_tuple[2 + base] << 8) + calib_tuple[3 + base]
    Yoff = (calib_tuple[4 + base] << 8) + calib_tuple[5 + base]
    Zoff = (calib_tuple[6 + base] << 8) + calib_tuple[7 + base]
    
    Xsens = (calib_tuple[8 + base] << 8) + calib_tuple[9 + base]
    Ysens = (calib_tuple[10 + base] << 8) + calib_tuple[11 + base]
    Zsens = (calib_tuple[12 + base] << 8) + calib_tuple[13 + base]
    
    calib_info = LNACalib(Xoff, Yoff, Zoff, Xsens, Ysens, Zsens)
    return calib_info
    
class LNACalib:
    def __init__(self, Xoff = 0, Yoff = 0, Zoff = 0, Xsens = 0, Ysens = 0, Zsens = 0):
        self.Xoff = Xoff
        self.Yoff = Yoff
        self.Zoff = Zoff
        self.Xsens = Xsens
        self.Ysens = Ysens
        self.Zsens = Zsens
        
    def printCalib(self):
        print "X Offset: {0}".format(self.Xoff)
        print "Y Offset: {0}".format(self.Yoff)
        print "Z Offset: {0}".format(self.Zoff)
        print "X Sensitivity: {0}".format(self.Xsens)
        print "Y Sensitivity: {0}".format(self.Ysens)
        print "Z Sensitivity: {0}".format(self.Zsens)

"""       
SHIMMER_BASE = "00:06:66:66:"   # base bt address of Shimmer        
SHIMMER_ID = "94:A0"            # varies among shimmers        
s=lightblue.socket()
shimmer_connect(s, SHIMMER_BASE + SHIMMER_ID, 1)
calib = readCalibInfo(s)
calib.printCalib()
s.close()"""