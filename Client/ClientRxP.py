####### IMPORTS #########

import sys
from socket import *
import md5

# format of ACK packets are header, body 
# where header = checksum, (sequencenumber) and body = ACK


####### GLOBAL VARIABLES! #########
PACKET_SIZE = 9500
SOCKET = None
C_PORT = ""
DEST_ADDR = None


####### CLIENT METHODS #########

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
				checkandSend(synPacket)
				SOCKET.settimeout(1)
				data, serverAddr = SOCKET.recvfrom(PACKET_SIZE)
				if data != "":
						checksum, synAck = data.split(',', 1)
						print 'client received ', `synAck`, 'from ', `serverAddr`
						if(checkSumCheck(checksum, synAck) and synAck[:6] == "SYNACK"):
							sendingSyn = False
							SOCKET.settimeout(None)
							ackPacket = "ACK"
							checkandSend(ackPacket)
							connection = True
			except error:
				sendingSyn = True
	except error:
		print "The client could not bind to port: " + str(C_PORT)
		connection = False
	return connection

def receive(fileName):
	global DEST_ADDR, SOCKET
	outOfOrderBuffer = []
	packetBuffer = []
	ackArr= []
	expectedSequenceNum = 0
	receiving = True
	once = True
	ackPacket = "ACK"

	requestPacket = "PULL_" + fileName
	checkandSend(requestPacket)
	data, serverAddr = SOCKET.recvfrom(PACKET_SIZE)
	try:
		checksum, data = data.split(',', 1)
		print str(data)
	except:
		print "This file could not be pulled"
		return
	if data == "ACK" and checkSumCheck(checksum, data):
		print "Ready to Receive Data..."
		while(receiving): 
			SOCKET.settimeout(None)
			data, clientAddr = SOCKET.recvfrom(PACKET_SIZE)
			try:
				checksum, body = data.split(',', 1)
				header, body = data.split('|', 1)
			except:
				print "This packet is invalid and will be dropped"
				continue
			headerArr = header.split(",")
			if(len(headerArr) < 5 ):
				if(body == "SYN"):
					handshake()
				continue

			clientPort,serverPort,sequenceNum, packets,fileType,checksum = decodeHeader(header)
			if (not clientPort and not serverPort and not sequenceNum and not packets and not isServer and not fileType and not checksum):
				print "This header is invalid and will be dropped"
				continue
			if(once):
				i = 0
				while(i <= packets):
					ackArr.insert(i,False)
					outOfOrderBuffer.insert(i,"empty")
					i = i + 1

				ackArr.insert(-1,False)
				once = False

			m = md5.new()
			c, header_without_checksum = header.split(",",1)
			check = header_without_checksum + "|" + body
			print (header_without_checksum)
			m.update(check)
			blah = m.hexdigest()
			m = md5.new()
			m.update(header_without_checksum + "|")
			new_checksum = m.hexdigest()

			if(new_checksum != checksum):
				print "This packet is invalid and will be dropped: " + str(seqNum)
				continue

			if ackArr[sequenceNum] == True :
				print "This packet is a duplicate and will be dropped: " + str(sequenceNum)
				continue

			if(sequenceNum > expectedSequenceNum and not ackArr[sequenceNum]):
				outOfOrderBuffer.insert(sequenceNum,body)
				print "The packet " + str(sequenceNum) + " is out of order and will be placed on the buffer"

			if(sequenceNum == expectedSequenceNum):
				packetBuffer.insert(sequenceNum,body)
				expectedSequenceNum = expectedSequenceNum + 1
				print "The packet " + str(sequenceNum) + " was Successfully received"
			
			if(expectedSequenceNum <= packets):
				while(ackArr[expectedSequenceNum]):
					outOfOrderPacket = outOfOrderBuffer.pop(expectedSequenceNum)
					outOfOrderBuffer.insert(expectedSequenceNum,"Used")
					packetBuffer.insert(expectedSequenceNum,outOfOrderPacket)
					print "The outOfOrderPacket packet " + str(expectedSequenceNum) + " was successfully reordered"

					if(expectedSequenceNum <= packets):
						expectedSequenceNum = expectedSequenceNum + 1
			newAckPacket = str(sequenceNum) + "|" + ackPacket
			message = md5.new()
			message.update(newAckPacket)
			c = message.hexdigest()
			newAckPacket = c + "," + newAckPacket
			print "Sending ACK for: " + str(sequenceNum)
			SOCKET.sendto(newAckPacket, DEST_ADDR)
			ackArr[sequenceNum] = True
			if(all(x is True for x in ackArr[1:-1])):
				receiving = False
			else:
				receiving = True
		print "Successfully Received all Data Packets!"
		return(packetBuffer)

def send(packetArr, fileName, windowSize):
	global SOCKET, DEST_ADDR
	base = 0
	nextPacketNum = 0
	sentAll = False
	numAcksRecv = 0
	numOutOfOrder = 0
	numPackets = len(packetArr)
	ackArr = [False]*numPackets
	print "There are  " + str(numPackets) + " packets and the windowSize is" + str(windowSize)
	sendingPacket = "PUSH_"+ fileName
	checkandSend(sendingPacket)
	data, clientAddr = SOCKET.recvfrom(PACKET_SIZE)
	try:
		checksum, data = data.split(',', 1)
	except:
		print "There was an error processing that request!"
	
	if (data == "ACK" and checkSumCheck(checksum, data)):
		while ((not sentAll) or (numAcksRecv < numPackets)):
			if ((nextPacketNum < base + windowSize) and not sentAll):
				sendDataPacket(packetArr, nextPacketNum)
				nextPacketNum = nextPacketNum + 1
				if nextPacketNum == numPackets:
					print "All Packets Successfully Sent!"
					sentAll = True
			else:
				print "Window has been filled. Waiting on acknowledgement to continue"
				try:
					SOCKET.settimeout(2)
					ackData, clientAddr = SOCKET.recvfrom(PACKET_SIZE)
				except:
					continue
				try:
					ackCheckSum, ackData = ackData.split(',', 1)
					ackNumStr, body = ackData.split("|")
					ackNum = eval(ackNumStr)
					print "Received ACK for Packet " + str(ackNum)
					if (not checkSumCheck(ackCheckSum, ackData)):
						print "The ACK received is invalid"
						continue
					if ackNum > numPackets:
						print "The ACK received is invalid, packet dropped"
						continue
					if ackArr[ackNum] == True:
						print "The ACK received is a duplicate, packet dropped"
						continue
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

				except:
					print "This packet is invalid and will be dropped"
					continue
	else:
		print "There was an error sending that packet!"

def closeSockets():
	try:
		SOCKET.close()
	except:
		pass
	


####### HELPER METHODS #########

def checkSumCheck(checksum, restOfPacket):
	message = md5.new()
	message.update(restOfPacket)
	checksumData = message.hexdigest()
	if(checksumData == checksum):
		return True
	return False

def decodeHeader(header):
    try:
        headerSplit = header.split(',')
        checksum = headerSplit[0]
        hostport = eval(headerSplit[1])
        destport = eval(headerSplit[2])
        sequencenumber = eval(headerSplit[3])
        numPackets = eval(headerSplit[4])
        filetype = headerSplit[5]
        return hostport, destport, sequencenumber, numPackets - 1, filetype, checksum
    except:
        return False,False,False,False,False,False

def sendDataPacket(packets, numPacket):
	global SOCKET, DEST_ADDR
	packet, ack =  packets[numPacket]
	SOCKET.sendto(packet, DEST_ADDR)
	print "Packet " + str(numPacket) + " sent"

def checkandSend(line):
	global SOCKET, DEST_ADDR
	print 'Client Sending ', line, ' to ', `DEST_ADDR`
	message = md5.new()
	message.update(line)
	checksumData = message.hexdigest()
	line = checksumData.strip() + "," + line
	SOCKET.sendto(line, DEST_ADDR)
