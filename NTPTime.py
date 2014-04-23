
#taken from http://stackoverflow.com/questions/12664295/ntp-client-in-python
from socket import AF_INET, SOCK_DGRAM
import sys
import socket
import struct, time



# # Set the socket parameters 
def getDateTime():
    print "starting getDateTime()"
    host = "pool.ntp.org"
    port = 123
    buf = 1024
    address = (host,port)
    msg = '\x1b' + 47 * '\0'
    
    
    # reference time (in seconds since 1900-01-01 00:00:00)
    DST = 3600   # move time ahead 1 hour
    TIMEZONE = 4 * 3600 # EST
    TIME1970 = 2208988800L + TIMEZONE # 1970-01-01 00:00:00
    
    # connect to server
    client = socket.socket( AF_INET, SOCK_DGRAM)
    client.settimeout(2)    

    try:
    	client.sendto(msg, address)
    	msg, address = client.recvfrom( buf )
    except:
	print "Error Accessing NTP Server"
        return -1
    else:
    	t = struct.unpack( "!12I", msg )[10]
    	#print t
    	t -= TIME1970
    	#print t
    
   	print "Conpleted getDateTime()"
	try:
    	    return time.ctime(t)
	except:
	    print "Error Processing Time"
	    return -1
