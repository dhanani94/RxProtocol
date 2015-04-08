import sys
from socket import *

BUFSIZE = 1024

def main():
	if len(sys.argv) < 4:
		usage()
		bindport = eval(sys.argv[1])
	else:
		bindport = 8080
	host = sys.argv[2]
	if len(sys.argv) > 4:
		port = eval(sys.argv[3])
		fileName = sys.argv[4]
	addr = host, port
	s = socket(AF_INET, SOCK_DGRAM)
	s.bind(('', bindport))
	print 'udp echo client ready, reading stdin'
	connect(s, addr)
	recieve(fileName, s, addr)
	
def recieve(fileName, s, addr):
	sendThis("GET" + "_" + fileName, addr, s)
	file = open(fileName, 'wb')
	data, addr = s.recvfrom(BUFSIZE)
	# check sequencenumber
	while(data):
		sendThis("ACK", addr, s)
		file.write(data)
		data, addr = s.recvfrom(BUFSIZE)
		if(data[:4] == "DONE"):
			file.close()
			s.close()
			break
	print("done recieving")


def connect(s, addr):
	sendThis("SYN", addr, s)
	data, fromaddr = s.recvfrom(BUFSIZE)
	print 'client received', `data`, 'from', `fromaddr`
	# check sequencenumber
	if(data == "SYNACK" and addr == fromaddr):
		sendThis("ACK", addr, s)



def sendThis(line, addr, s):
	print 'client sending', `line`, 'to', `addr`
	s.sendto(line, addr)



# update this with the correct arguments
def usage():
	sys.stdout = sys.stderr
	print 'Usage: udpecho -s [port] (server)'
	print 'or:    udpecho -c bindport desthost [destport] <file (client)'
	sys.exit(2)



main()





# todo: have the user input the filename, 
# ask the server to get the file, put
#  the file into a "buffer" and send back ACKs