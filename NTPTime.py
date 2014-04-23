#taken from http://stackoverflow.com/questions/12664295/ntp-client-in-python
from socket import AF_INET, SOCK_DGRAM
import sys
import socket
import struct, time



# # Set the socket parameters 
def getDateTime():
    host = "pool.ntp.org"
    port = 123
    buf = 1024
    address = (host,port)
    msg = '\x1b' + 47 * '\0'
    
    
    # reference time (in seconds since 1900-01-01 00:00:00)
    NO_DST = 3600   # move time ahead 1 hour
    TIME1970 = 2208988800L - NO_DST # 1970-01-01 00:00:00
    
    # connect to server
    client = socket.socket( AF_INET, SOCK_DGRAM)
    client.sendto(msg, address)
    msg, address = client.recvfrom( buf )
    
    t = struct.unpack( "!12I", msg )[10]
    print t
    t -= TIME1970
    print t
    
    
    return time.ctime(t)