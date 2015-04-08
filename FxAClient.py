import sys
import os.path
from socket import *
import RxPClient

status = "NO CONNECTION"

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
		if(line == "connect"):
			tcpConnect(s, addr)
		if(line[:3] == "get"):
			get(line[4:].strip(), s, addr)
		if (line[:4] == "post"):
			post(line[4:].strip(), s, addr)
		if (line == "disconnect"):
			disconnect()
		else:
			usage(2)

def usage(errorNum):
	sys.stdout = sys.stderr
	if(errorNum == 1):
		print 'Usage: FxAServer X A P'
		print 'X: the Even port # for FxASevers socket'
		print 'A: the IP address of NetEmu'
	 	print 'P: the UDP port number of NetEmu'
	 	sys.exit(2)
 	if(errorNum == 2):
 		print 'Please type another command: '
	

def tcpConnect(s, addr):
	print("attempting to connect")
	if(RxPClient.connect(s, addr)):
		status = "CONNECTED"
		print(status + "connected to server at " + `addr`)
		


def get(fileName, s, addr):
	# if(status == "CONNECTED"):
	RxPClient.recieve(fileName, s, addr)
	# else:
	# 	print("Need to establish a connection first!")
	# 	return

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

def disconnect():
	status = "NO CONNECTION"

main()
