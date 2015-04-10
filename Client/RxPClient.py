import sys
from socket import *
import md5

BUFSIZE = 1024
SOCKET = None
C_PORT = ""
DEST_ADDR = None

def connect(bindport, addr):
	global SOCKET, C_PORT, DEST_ADDR
	connection = False
	C_PORT = bindport
	DEST_ADDR = addr
	try:
		SOCKET = socket(AF_INET, SOCK_DGRAM)
		SOCKET.bind(('', C_PORT))
		sendingSyn = True
		while sendingSyn:
			try:
				synPacket = "SYN"
				synCheckSum = createChecksum(synPacket)
				synPacket = synPacket + "_" + synCheckSum
				sendPacket(synPacket, DEST_ADDR, SOCKET)
				SOCKET.settimeout(1)
				data, serverAddr = SOCKET.recvfrom(BUFSIZE)
				if data != "":
					try:
						synAck, dataChecksum = data.split("_")
						print 'client received', `synAck`, 'from', `serverAddr`
					except:
						continue
					if(compDataSum(synAck, dataChecksum) and synAck[:6] == "SYNACK"):
						sendingSyn = False
						SOCKET.settimeout(None)
						ackPacket = "ACK"
						ackCheckSum = createChecksum(ackPacket)
						ackPacket = ackPacket + "_" + ackCheckSum
						sendPacket(ackPacket, DEST_ADDR, SOCKET)
						connection = True
					else:
						print "wtf"
			except error:
				#timeout occured
				sendingSyn = True
	except error:
		print "The client could not bind to port: " + C_PORT
		connection = False
	return connection

def addHeader(packet, sequenceNumber):
	global C_PORT, DEST_ADDR
	packet = `C_PORT` + "," + `DEST_ADDR[1]` + "," + `sequenceNumber` + "," + `packet`
	return packet

def decodeHeader(packet):
	sourcePort, destPort, sequenceNumber, data = packet.split(',')
	return eval(sourcePort), eval(destPort), eval(sequenceNumber), data

def compDataSum(data, checkSum):
	message = md5.new()
	message.update(data)
	checksumData = message.hexdigest()
	if(checksumData == checkSum):
		return True
	return False

def createChecksum(data):
	message = md5.new()
	message.update(data)
	checksumData = message.hexdigest()
	return checksumData

def send(packetArr, fileName):

	global SOCKET, DEST_ADDR
	numPackets = len(packetArr)
	sendPacket("SEND_"+ fileName + ","+ `numPackets`, DEST_ADDR, SOCKET)
	print("this many packets: " + `numPackets`)
	# sendPacket("SENDING_"+`numPackets`, DEST_ADDR, SOCKET)
	data, clientAddr = SOCKET.recvfrom(BUFSIZE)
	if data == "ACK":
		sendPacket(packetArr.pop(0), DEST_ADDR, SOCKET)
		for packet in packetArr:
			data, clientAddr = SOCKET.recvfrom(BUFSIZE)
			if data == "ACK":
				sendPacket(packet, DEST_ADDR, SOCKET)
	# if data[:3] == "FNF":


def receive(fileName):
	global SOCKET, DEST_ADDR
	packets = []
	requestPacket = "RECV_" + fileName
	# requestPacket = addHeader(requestPacket, 0)
	sendPacket(requestPacket, DEST_ADDR, SOCKET)
	data, serverAddr = SOCKET.recvfrom(BUFSIZE)
	if data[:7] == "SENDING":

		sendPacket("ACK", DEST_ADDR, SOCKET)
		numPackets = eval(data[8:])
		print("RXPC is gonna receive this many packets: " + `numPackets`)
		for i in xrange(numPackets):
			data, serverAddr = SOCKET.recvfrom(BUFSIZE)
			packets.append(data)
			sendPacket("ACK", DEST_ADDR, SOCKET)
		return packets

	# if data[:3] == "FNF":
	# 	return False
	# return True

	pass

def sendPacket(line, addr, s):
	print 'client sending', `line`, 'to', `addr`
	s.sendto(line, addr)


def closeSockets():
	SOCKET.close()










# def main():
# 	if len(sys.argv) < 4:
# 		usage()
# 		bindport = eval(sys.argv[1])
# 	else:
# 		bindport = 8080
# 	host = sys.argv[2]
# 	if len(sys.argv) > 4:
# 		port = eval(sys.argv[3])
# 		fileName = sys.argv[4]
# 	addr = host, port
# 	s = socket(AF_INET, SOCK_DGRAM)
# 	s.bind(('', bindport))
# 	print 'udp echo client ready, reading stdin'
# 	connect(s, addr)
# 	recieve(fileName, s, addr)





# todo: have the user input the filename, 
# ask the server to get the file, put
#  the file into a "buffer" and send back ACKs

# def recieve(fileName, addr):
# 	sendPacket("GET" + "_" + fileName, addr, SOCKET)
# 	file = open(fileName, 'wb')
# 	data, addr = SOCKET.recvfrom(BUFSIZE)
# 	# check sequencenumber
# 	# check if file exists before creating
# 	while(data):
# 		if(data)
# 		sendPacket("ACK", addr, SOCKET)
# 		file.write(data)
# 		data, addr = SOCKET.recvfrom(BUFSIZE)
# 		if(data[:4] == "DONE"):
# 			file.close()
# 			break
# 	print("done recieving")


# update this with the correct arguments
# def usage():
# 	sys.stdout = sys.stderr
# 	print 'Usage: udpecho -s [port] (server)'
# 	print 'or:    udpecho -c bindport desthost [destport] <file (client)'
# 	sys.exit(2)



# def send(packetArr):
# 	global SOCKET, DEST_ADDR
	# if(os.path.isfile(fileName)):
	# 	file = open(fileName, 'rb')
	# else:
	# 	print("This file does not exist")
	# 	return
	# nxtPkt = file.read(BUFSIZE)
	# while(nxtPkt):
	# 	sendPacket(nxtPkt, addr, s)
	# 	data, fromaddr = s.recvfrom(BUFSIZE)
	# 	print 'server received', `data`, 'from', `fromaddr`
	# 	#check sequence# and retransmit if necessary
	# 	if(data == "ACK"):
	# 		nxtPkt = file.read(BUFSIZE)