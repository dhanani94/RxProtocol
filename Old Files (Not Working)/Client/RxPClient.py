import sys
from socket import *
import md5

BUFSIZE = 1024 + 16
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
				sendPacket2(synPacket)
				SOCKET.settimeout(1)
				data, serverAddr = SOCKET.recvfrom(BUFSIZE)
				if data != "":
						synAck = checkSumCheck(data)
						print 'client received', `synAck`, 'from', `serverAddr`
						if(synAck and synAck[:6] == "SYNACK"):
							sendingSyn = False
							SOCKET.settimeout(None)
							ackPacket = "ACK"
							sendPacket2(ackPacket)
							connection = True
			except error:
				#timeout occured
				sendingSyn = True
	except error:
		print "The client could not bind to port: " + C_PORT
		connection = False
	return connection

def checkSumCheck(packet):
	data, checkSum = packet.split("|")
	message = md5.new()
	message.update(data)
	checksumData = message.hexdigest()
	if(checksumData == checkSum):
		return data
	return False


def compDataSum(data, checkSum):
	message = md5.new()
	message.update(data)
	checksumData = message.hexdigest()
	if(checksumData == checkSum):
		return True
	return False

def createChecksumPacket(data):
	message = md5.new()
	message.update(data)
	checksumData = message.hexdigest()
	dataPacket = data + "|" + checksumData.strip()
	print "made this checksum" + checksumData
	return dataPacket




# def send(packetArr, fileName):
# 	global SOCKET, DEST_ADDR
# 	numPackets = len(packetArr)
# 	sendingPacket = "SEND_"+ fileName + ","+ `numPackets`
# 	sendPacket2(sendingPacket)
# 	print("this many packets: " + `numPackets`)
# 	data, clientAddr = SOCKET.recvfrom(BUFSIZE)
# 	data = checkSumCheck(data)
# 	if data == "ACK":
# 		sendPacket2(packetArr.pop(0))
# 		for packet in packetArr:
# 			data, clientAddr = SOCKET.recvfrom(BUFSIZE)
# 			data = checkSumCheck(data)
# 			if data == "ACK":
# 				sendPacket2(packet)
# 			elif data == False:
# 				"There was an error with the packet"
# 	elif data == False:
# 		"There was an error with the packet"

def send(packetArr, fileName, windowSize):
	global SOCKET, DEST_ADDR
	base = 0
	nextPacketNum = 0
	sentAll = False
	numAcksRecv = 0
	numOutOfOrder = 0
	numPackets = len(packetArr)
	ackArr = [False]*numPackets

	sendingPacket = "SEND_"+ fileName + ","+ `numPackets`
	sendPacket2(sendingPacket)
	print("this many packets: " + `numPackets`)
	data, clientAddr = SOCKET.recvfrom(BUFSIZE)
	data = checkSumCheck(data)
	if data == "ACK":

		while ((not sentAll) or (numAcksRecv < numPackets)):
			if ((nextPacketNum < base + windowSize) and not sentAll):
				##fix this method!!! send packet
				sendPacket(packetArr, nextPacketNum)
				if nextPacketNum == numPackets:
					print "All Packets Successfully Sent!"
					sentAll = True
			else:
				print "window is full. Waiting for more ACKs!"
				data, clientAddr = SOCKET.recvfrom(9500)
				ackData = checkSumCheck(packet)
				if (not ackData):
					print "Invalid ACK received."
	       			continue
	       		ackNum = parseAckNum(input_data)
	      		print "Selective ACK for only Packet " + str(ackNum) + " received."

	      		if ackArr[ackNum] == True:
	      			print "Duplicate ACK received. Dropping Packet"

	      		numAcksRecv = numAcksRecv + 1
	      		ackArr[ackNum] = True

	      		if ackNum == base:
	      			totalPackets = numPackets - base
	      			for x in xrange(1,totalPackets):
	      				if (ackArr[base + x] == True):
	      					numOutOfOrder = numOutOfOrder + 1
	      				else:
	      					break
	  				base = base + 1 + numOutOfOrder
	  				numOutOfOrder = 0

	# 	sendPacket2(packetArr.pop(0))
	# 	for packet in packetArr:
	# 		data, clientAddr = SOCKET.recvfrom(BUFSIZE)
	# 		data = checkSumCheck(data)
	# 		if data == "ACK":
	# 			sendPacket2(packet)
	# 		elif data == False:
	# 			"There was an error with the packet"
	# elif data == False:
	# 	"There was an error with the packet"


def receive(fileName):
	global SOCKET, DEST_ADDR
	packets = []
	requestPacket = "RECV_" + fileName
	sendPacket2(requestPacket)
	data, serverAddr = SOCKET.recvfrom(BUFSIZE)
	data = checkSumCheck(data)
	if data[:7] == "SENDING":
		ackPacket = "ACK"
		sendPacket2(ackPacket)
		numPackets = eval(data[8:])
		print("RXPC is gonna receive this many packets: " + `numPackets`)
		for i in xrange(numPackets):
			data, serverAddr = SOCKET.recvfrom(BUFSIZE)
			# print data
			# data = checkSumCheck(data)
			packets.append(data)
			sendPacket2("ACK")
		return packets
	pass

def sendPacket2(line):
	global SOCKET, DEST_ADDR
	print 'client sending', line, 'to', `DEST_ADDR`
	SOCKET.sendto(createChecksumPacket(line), DEST_ADDR)

# def sendPacket(line):
# 	global SOCKET, DEST_ADDR
# 	print 'client sending', line, 'to', `DEST_ADDR`
# 	SOCKET.sendto(line, DEST_ADDR)


def sendPacket(packets, numPacket):
	global SOCKET, DEST_ADDR
	packet, ack =  packets[numPacket]
	SOCKET.sendto(packet, DEST_ADDR)
	print "Packet " + str(numPacket) + " sent"


def closeSockets():
	SOCKET.close()

