import sys
import RxPServer
from socket import *

def main():
	if len(sys.argv) < 3:
		usage()
	else:
		port = eval(sys.argv[1])
		s = socket(AF_INET, SOCK_DGRAM)
		s.bind(('', port))
		RxPServer.start(s)
		
def usage():
	sys.stdout = sys.stderr
	print 'Usage: FxAServer X A P'
	print 'X: the odd port # for FxAClient socket'
	print 'A: the IP address of NetEmu'
 	print 'P: the UDP port number of NetEmu'
	sys.exit(2)

def terminate():
	pass

main()