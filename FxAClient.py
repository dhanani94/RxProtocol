import sys
import os.path
from socket import *
import RxPClient

status = "NO_CONNECTION"

def main():
	if len(sys.argv) < 3:
		usage(1)
	else:
		bindport = eval(sys.argv[1])
		addr = sys.argv[2], eval(sys.argv[3])
		s = socket(AF_INET, SOCK_DGRAM)
		s.bind(('', bindport))
		print "Please type a command:"
	while 1:
		line = sys.stdin.readline().strip()
		if not line:
			break
		elif(line == "connect"):
			tcpConnect(s, addr)
		elif(line[:3] == "get"):
			get(line[4:].strip(), s, addr)
		elif (line[:4] == "post"):
			post(line[4:].strip(), s, addr)
		elif (line == "disconnect"):
			disconnect(s)
		else:
			usage(2)

def usage(errorNum):
	sys.stdout = sys.stderr
	if(errorNum == 1):
		print 'Usage: FxAServer X A P'
		print 'X: the Even port # for FxAClient socket'
		print 'A: the IP address of NetEmu'
	 	print 'P: the UDP port number of NetEmu'
	 	sys.exit(2)
 	if(errorNum == 2):
 		print 'Please type another command: '
	

def tcpConnect(s, addr):
	global status
	if(status == "NO_CONNECTION"):
		if(RxPClient.connect(s, addr)):
			status = "CONNECTED"
			print(status + "connected to server at " + `addr`)
	else:
		print "connection already exists"
		


def get(fileName, s, addr):
	print("on get the value of status is: " + status)
	if(status == "CONNECTED"):
		RxPClient.recieve(fileName, s, addr)
	else:
		print("Need to establish a connection first!")
		return

def post(fileName, s, addr):
	if(status == "CONNECTED"):
		if(os.path.isfile(fileName)):
			file = open(fileName, 'rb')
			RxPClient.send(file, s, addr)
		else:
			print("The file: '" + fileName + "' could not be located")
			return
	else:
		print("Need to establish a connection first!")
		return

def disconnect(s):
	global status
	status = "NO_CONNECTION"
	s.close()	
	sys.exit(2)

main()
