import socket
import sys
import csv

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#ip address of my laptop
host = '128.143.24.152'

# Connect the socket to the port on the server given by the caller
server_address = (host, 10000)
server_address2 = (host, 10001)
print >>sys.stderr, 'connecting to %s port %s' % server_address
print >>sys.stderr, 'connecting to %s port %s' % server_address2
sock.connect(server_address)
sock2.connect(server_address2)

faccel = open("accel", "r")
#reader = csv.reader(faccel)

try:
    for row in faccel:
        
        message = row.strip()
        print >>sys.stderr, 'sending "%s"' % message
        sock.sendall(message + "\n")
        sock2.sendall(message + "\n")
    
        """
        amount_received = 0
        amount_expected = len(message)
        while amount_received < amount_expected:
            data = sock.recv(16)
            amount_received += len(data)
            print >>sys.stderr, 'received "%s"' % data
        """

finally:
    faccel.close()
    sock.close()
    sock2.close()