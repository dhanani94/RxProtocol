import sys
import RxPServer

def main():
	if len(sys.argv) < 3:
		usage()
	else:
		portNumber = eval(sys.argv[1])
	s = socket(AF_INET, SOCK_DGRAM)
	s.bind(('', port))
	print 'udp echo server ready'
	addr = connect(s)
	data, addr = s.recvfrom(BUFSIZE)
	if(data[:3] == "GET"):
		fileName = data[4:]
		send(fileName, s, addr)

def usage():
	sys.stdout = sys.stderr
	print 'Usage: FxAServer X A P'
	print 'X: the port number at which the FxA­server’s UDP socket should bind to (odd number) 
	print 'A: the IP address of NetEmu'
 	print 'P: the UDP port number of NetEmu'
	sys.exit(2)

def connect():

def get():
	pass

def post():
	pass

def disconnect():
