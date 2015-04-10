import sys
from socket import *
import md5


BUFSIZE = 1024
SOCKET = None
S_PORT = ""
DEST_ADDR = None

def handshake():
	global SOCKET, S_PORT, DEST_ADDR
	awaitingSyn = True
	while awaitingSyn:
		try:
			SOCKET.settimeout(1)
			data, clientAddr = SOCKET.recvfrom(BUFSIZE)
			if data != "":
				try:
					data, dataChecksum = data.split("_")
					print 'client received', `data`, 'from', `clientAddr`
				except:
					continue
				if(compDataSum(data, dataChecksum) and data[:3] == "SYN"):
					awaitingSyn = False
					sendingSynAck = True
					while sendingSynAck:
						try:
							synAckPacket = "SYNACK"
							synAckCheckSum = createChecksum(synAckPacket)
							synAckPacket = synAckPacket + "_" + synAckCheckSum
							sendPacket(synAckPacket, DEST_ADDR, SOCKET)
							SOCKET.settimeout(1)
							data, clientAckAddr = SOCKET.recvfrom(BUFSIZE)
							if (data != "" and clientAddr == clientAckAddr):
								try:
									data, dataChecksum = data.split("_")
									print 'server received', `data`, 'from', `clientAckAddr`
								except:
									continue
								if(compDataSum(data, dataChecksum) and data[:3] == "ACK"):
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


	


	# while 1:
	# 	data, addr = s.recvfrom(BUFSIZE)
	# 	print 'server received', `data`, 'from', `addr`
	# 	if(data == "SYN"):
	# 		data +="ACK_" + `seqNum`
	# 		conAddr = addr
	# 		s.sendto(data, addr)
	# 	elif(data[:3] == "ACK" and eval(data[4:]) == seqNum):
	# 		print("successfully conencted to", `conAddr`)
	# 	elif(data[:3] == "GET"):
	# 		fileName = data[4:]
	# 		send(fileName, s, addr)
	# 	else:
	# 		print "unknown request"

def listen():
	SOCKET.settimeout(None)
	data, clientAddr = SOCKET.recvfrom(BUFSIZE)
	print("server recieved" + data)
	# sourcePort, destPort, sequenceNumber, data = decodeHeader(data)
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

def addHeader(packet, sequenceNumber):
	global C_PORT, DEST_ADDR
	packet = `C_PORT` + "," + `DEST_ADDR[1]` + "," + `sequenceNumber` + "," + `packet`
	return packet


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

def receive(numStr):
	global SOCKET, DEST_ADDR
	packets = []
	numPackets = eval(numStr)
	# requestPacket = "RECV_" + fileName
	# requestPacket = addHeader(requestPacket, 0)
	# sendPacket(requestPacket, DEST_ADDR, SOCKET)
	# data, serverAddr = SOCKET.recvfrom(BUFSIZE)
	sendPacket("ACK", DEST_ADDR, SOCKET)
	print("RXPC is gonna receive this many packets: " + `numPackets`)
	for i in xrange(numPackets):
		data, serverAddr = SOCKET.recvfrom(BUFSIZE)
		packets.append(data)
		sendPacket("ACK", DEST_ADDR, SOCKET)
	return packets


# def sendFile(fileName):


def send(packetArr):
	global SOCKET, DEST_ADDR
	numPackets = len(packetArr)
	print("this many packets: " + `numPackets`)
	sendPacket("SENDING_"+`numPackets`, DEST_ADDR, SOCKET)
	data, clientAddr = SOCKET.recvfrom(BUFSIZE)
	if data == "ACK":
		sendPacket(packetArr.pop(0), DEST_ADDR, SOCKET)
		for packet in packetArr:
			data, clientAddr = SOCKET.recvfrom(BUFSIZE)
			if data == "ACK":
				sendPacket(packet, DEST_ADDR, SOCKET)
	# if data[:3] == "FNF":


def sendPacket(line, addr, s):
	print 'client sending', `line`, 'to', `addr`
	s.sendto(line, addr)

def closeSocket():
	SOCKET.close()




	






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


# todo: if packet recieved is a "GET fileName",
#  run code to send filename, wait for ACKS! 