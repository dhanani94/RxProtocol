import sys
from socket import *
import os.path


BUFSIZE = 1024

def main():
	if len(sys.argv) > 2:
		port = eval(sys.argv[2])
	else: 
		port = 8081
	# else:
	# 	port = ECHO_PORT
	s = socket(AF_INET, SOCK_DGRAM)
	s.bind(('', port))
	print 'udp echo server ready'
	addr = connect(s)
	data, addr = s.recvfrom(BUFSIZE)
	if(data[:3] == "GET"):
		fileName = data[4:]
		send(fileName, s, addr)


def connect(s):
	while 1:
		data, addr = s.recvfrom(BUFSIZE)
		print 'server received', `data`, 'from', `addr`
		if(data == "SYN"):
			data +="ACK"
			conAddr = addr
			s.sendto(data, addr)
		if(data == "ACK" and addr == conAddr):
			print("successfully conencted to", `conAddr`)
			return conAddr

def send(fileName, s, addr):
	if(os.path.isfile(fileName)):
		file = open(fileName, 'rb')
	else:
		print("This file does not exist")
		return
	nxtPkt = file.read(BUFSIZE)
	while(nxtPkt):
		sendThis(nxtPkt, addr, s)
		data, fromaddr = s.recvfrom(BUFSIZE)
		print 'server received', `data`, 'from', `fromaddr`
		#check sequence# and retransmit if necessary
		if(data == "ACK"):
			nxtPkt = file.read(BUFSIZE)
	sendThis("DONE", addr, s)
	file.close()
	s.close()


def sendThis(line, addr, s):
	print 'server sending data to', `addr`
	s.sendto(line, addr)



main()


# todo: if packet recieved is a "GET fileName",
#  run code to send filename, wait for ACKS! 