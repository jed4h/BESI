import socket
import subprocess
import time


while True:
    sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # if this fails, the BBB is not connected to the network
    try:
	sock.connect(("8.8.8.8", 80))
    except socket.error as e:
 	print "Network Error",e
	subprocess.Popen(["./wifi-reset.sh"])

    time.sleep(5)
