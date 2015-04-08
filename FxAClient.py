import sys

def main():
	if len(sys.argv) < 3:
		usage()
	else:
		bindport = eval(sys.argv[1])
		addr = eval(sys.argv[2]), eval(sys.argv[3])
	while 1:
		line = sys.stdin.readline()
		if not line:
			break
		if(line == "connect"):
			connect()
		if(line[:3] == "get"):
			get(line[4:])
		if (line[:4] == "post"):
			post(line[4:])
		if (line == "disconnect"):
			disconnect()

def usage():
	sys.stdout = sys.stderr
	print 'Usage: FxAServer X A P'
	print 'X: the Even port # for FxASevers socket'
	print 'A: the IP address of NetEmu'
 	print 'P: the UDP port number of NetEmu'
	sys.exit(2)

def connect():
	print("attempting to connect")
	s = socket(AF_INET, SOCK_DGRAM)
	s.bind(('', bindport))
	RxPClient.connect(s, addr)


def get(cal):
	print("attempting to get")
	pass

def post():
	print("attempting to post")
	pass

def disconnect():
	print("attempting to disconnect")

main()
