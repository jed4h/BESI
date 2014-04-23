import lightblue
import socket as Socket
import sys

s=lightblue.socket()

try:
	s.connect(("00:06:66:66:94:A0",1))
except Socket.error as e:
	print type(e)
	print e.args
	print e
	print str(e).split(",")[0][1:]

else:
	print "Connected"
