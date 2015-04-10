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
				sendPacket(synPacket, DEST_ADDR, SOCKET)
				SOCKET.settimeout(1)
				data, serverAddr = SOCKET.recvfrom(BUFSIZE)
				if data != "":
						synAck = checkSumCheck(data)
						print 'client received', `synAck`, 'from', `serverAddr`
						if(synAck and synAck[:6] == "SYNACK"):
							sendingSyn = False
							SOCKET.settimeout(None)
							ackPacket = "ACK"
							sendPacket(ackPacket, DEST_ADDR, SOCKET)
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

def send(packetArr, fileName):
	global SOCKET, DEST_ADDR
	numPackets = len(packetArr)
	sendingPacket = "SEND_"+ fileName + ","+ `numPackets`
	sendPacket(sendingPacket, DEST_ADDR, SOCKET)
	print("this many packets: " + `numPackets`)
	data, clientAddr = SOCKET.recvfrom(BUFSIZE)
	data = checkSumCheck(data)
	if data == "ACK":
		sendPacket(packetArr.pop(0), DEST_ADDR, SOCKET)
		for packet in packetArr:
			data, clientAddr = SOCKET.recvfrom(BUFSIZE)
			data = checkSumCheck(data)
			if data == "ACK":
				sendPacket(packet, DEST_ADDR, SOCKET)
			elif data == False:
				"There was an error with the packet"
	elif data == False:
		"There was an error with the packet"


def receive(fileName):
	global SOCKET, DEST_ADDR
	packets = []
	requestPacket = "RECV_" + fileName
	sendPacket(requestPacket, DEST_ADDR, SOCKET)
	data, serverAddr = SOCKET.recvfrom(BUFSIZE)
	data = checkSumCheck(data)
	if data[:7] == "SENDING":
		ackPacket = "ACK"
		sendPacket(ackPacket, DEST_ADDR, SOCKET)
		numPackets = eval(data[8:])
		print("RXPC is gonna receive this many packets: " + `numPackets`)
		for i in xrange(numPackets):
			data, serverAddr = SOCKET.recvfrom(BUFSIZE)
			# print data
			# data = checkSumCheck(data)
			packets.append(data)
			sendPacket("ACK", DEST_ADDR, SOCKET)
		return packets
	pass

def sendPacket(line, addr, s):
	print 'client sending', line, 'to', `addr`
	s.sendto(createChecksumPacket(line), addr)


def closeSockets():
	SOCKET.close()

