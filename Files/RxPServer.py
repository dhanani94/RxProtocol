import sys
from socket import *
import os.path


BUFSIZE = 1024
seqNum = 1000

# def main():
# 	if len(sys.argv) > 2:
# 		port = eval(sys.argv[2])
# 	else: 
# 		port = 8081
# 	# else:
# 	# 	port = ECHO_PORT
# 	s = socket(AF_INET, SOCK_DGRAM)
# 	s.bind(('', port))
# 	print 'udp echo server ready'
# 	addr = connect(s)
# 	data, addr = s.recvfrom(BUFSIZE)
# 	if(data[:3] == "GET"):
# 		fileName = data[4:]
# 		send(fileName, s, addr)


def start(s):
	global seqNum
	while 1:
		data, addr = s.recvfrom(BUFSIZE)
		print 'server received', `data`, 'from', `addr`
		if(data == "SYN"):
			data +="ACK_" + `seqNum`
			conAddr = addr
			s.sendto(data, addr)
		elif(data[:3] == "ACK" and eval(data[4:]) == seqNum):
			print("successfully conencted to", `conAddr`)
		elif(data[:3] == "GET"):
			fileName = data[4:]
			send(fileName, s, addr)
		else:
			print "unknown request"

def send(fileName, s, addr):
	if(os.path.isfile(fileName)):
		file = open(fileName, 'rb')
	else:
		print("This file does not exist")
		return
	nxtPkt = file.read(BUFSIZE)
	while(nxtPkt):
		sendLine(nxtPkt, addr, s)
		data, fromaddr = s.recvfrom(BUFSIZE)
		print 'server received', `data`, 'from', `fromaddr`
		#check sequence# and retransmit if necessary
		if(data == "ACK"):
			nxtPkt = file.read(BUFSIZE)
	s.sendto("DONE", addr)
	file.close()


def sendLine(line, addr, s):
	global seqNum
	seqNum = seqNum + 1
	print 'server sending data to', `addr`
	s.sendto(`seqNum` + line, addr)




# main()


# todo: if packet recieved is a "GET fileName",
#  run code to send filename, wait for ACKS! 