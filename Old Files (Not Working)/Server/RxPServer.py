import sys
from socket import *
import md5


BUFSIZE = 1024 + 16
SOCKET = None
S_PORT = ""
DEST_ADDR = None

def checkSumCheck(packet):
	data, checkSum = packet.split("|")
	message = md5.new()
	message.update(data)
	checksumData = message.hexdigest()
	if(checksumData == checkSum):
		return data
	return False

def createChecksumPacket(data):
	message = md5.new()
	message.update(data)
	checksumData = message.hexdigest()
	dataPacket = data + "|" + checksumData.strip()
	print "made this checksum" + checksumData
	return dataPacket

def handshake():
	global SOCKET, S_PORT, DEST_ADDR
	awaitingSyn = True
	while awaitingSyn:
		try:
			SOCKET.settimeout(1)
			data, clientAddr = SOCKET.recvfrom(BUFSIZE)
			if data != "":
				try:
					data = checkSumCheck(data)
					print 'client received', `data`, 'from', `clientAddr`
				except:
					continue
				if(data and data[:3] == "SYN"):
					awaitingSyn = False
					sendingSynAck = True
					while sendingSynAck:
						try:
							synAckPacket = "SYNACK"
							sendPacket(synAckPacket, DEST_ADDR, SOCKET)
							SOCKET.settimeout(1)
							data, clientAckAddr = SOCKET.recvfrom(BUFSIZE)
							if (data != "" and clientAddr == clientAckAddr):
								try:
									data = checkSumCheck(data)
									print 'server received', `data`, 'from', `clientAckAddr`
								except:
									continue
								if(data and data[:3] == "ACK"):
									SOCKET.settimeout(0)
									sendingSynAck = False
									connection = True
						except error:
							print "No ACK recieved from Client"
							SOCKET.settimeout(0)
							sendingSynAck = False
							connection = True
		except error:
			#Still need initial connection request from Client 
			awaitingSyn = True

def start(bindport, addr):
	global SOCKET, S_PORT, DEST_ADDR
	connection = False
	S_PORT = bindport
	DEST_ADDR = addr
	try:
		SOCKET = socket(AF_INET, SOCK_DGRAM)
		SOCKET.bind(('', S_PORT))
		print("Socket created and bound")
		handshake()

	except error:
		print "The Server could not bind to port: " + S_PORT
		connection = False
	return connection

def listen():
	SOCKET.settimeout(None)
	data, clientAddr = SOCKET.recvfrom(BUFSIZE)
	data = checkSumCheck(data)
	print("server recieved" + data)
	if data[:3] == "SYN":
		handshake()
	elif data[:4] == "SEND":
		return "RECV_"+data[5:].strip()
	elif data[:4] == "RECV":
		print(data)
		return "POST_" + data[5:].strip()
	return 

def decodeHeader(packet):
	sourcePort, destPort, sequenceNumber, data = packet.split(',')
	return eval(sourcePort), eval(destPort), eval(sequenceNumber), data

def addHeader(packets, fileType):
	global S_PORT, DEST_ADDR
	sequenceNumber  = 0
	numPackets = len(packets)
	div = ","
	rtnPackets = []
	for packet in packets:
		header = ""
		header = header + str(S_PORT) + div
		header = header + str(DEST_ADDR[1]) + div
		header = header + sequenceNumber + div
		header = header + str(numPackets) + div
		packet = header +  str(packet)
		rtnPackets.insert(packet)
		sequenceNumber = 1 + sequenceNumber
	return rtnPackets

def getHeaderSourcePort(packet):
	stringArr = packet.split(",")
	return stringArr[0]

def getHeaderDestAddr(packet):
	stringArr = packet.split(",")
	return stringArr[1]

def getHeaderSeqNum(packet):
	stringArr = packet.split(",")
	return stringArr[2]

def getHeaderNumPackets(packet):
	stringArr = packet.split(",")
	return stringArr[3]

def getHeaderData(packet):
	stringArr = packet.split(",")
	return stringArr[4]


# def compDataSum(data, checkSum):
# 	message = md5.new()
# 	message.update(data)
# 	checksumData = message.hexdigest()
# 	if(checksumData == checkSum):
# 		return True
# 	return False

def receive(numStr):
	global SOCKET, DEST_ADDR
	packets = []
	numPackets = eval(numStr)
	ackPacket = "ACK"
	sendPacket(ackPacket, DEST_ADDR, SOCKET)
	print("RXPC is gonna receive this many packets: " + `numPackets`)
	for i in xrange(numPackets):
		data, serverAddr = SOCKET.recvfrom(BUFSIZE)
		data = checkSumCheck(data)
		packets.append(data)
		ackPacket = "ACK"
		sendPacket(ackPacket, DEST_ADDR, SOCKET)
	return packets

def send(packetArr):
	global SOCKET, DEST_ADDR
	numPackets = len(packetArr)
	print("this many packets: " + `numPackets`)
	sendingPacket = "SENDING_"+`numPackets`
	sendPacket(sendingPacket, DEST_ADDR, SOCKET)
	data, clientAddr = SOCKET.recvfrom(BUFSIZE)
	data = checkSumCheck(data)
	if data == "ACK":
		SOCKET.sendto(packetArr.pop(0), DEST_ADDR)
		# sendPacket(packetArr.pop(0), DEST_ADDR, SOCKET)
		for packet in packetArr:
			data, clientAddr = SOCKET.recvfrom(BUFSIZE)
			data = checkSumCheck(data)
			if data == "ACK":
				SOCKET.sendto(packet, DEST_ADDR)
				# sendPacket(packet, DEST_ADDR, SOCKET)


def sendPacket(line, addr, s):
	print 'client sending', line, 'to', `addr`
	packet = createChecksumPacket(line)
	s.sendto(packet, addr)
	print packet

# def sendPacket2(line, addr, s):
# 	# print 'client sending', `line`, 'to', `addr`
# 	print type(line)
# 	print type(`line`)
# 	print line == `line`
# 	s.sendto(line, addr)
	

def closeSocket():
	SOCKET.close()

