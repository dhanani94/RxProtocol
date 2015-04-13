#######  IMPORTS  #########

import sys
import ServerRxP
import os
import md5

#######  GLOBAL VARIABLES!  #########
STATUS = "NO_CONNECTION"
DATASIZE = 9038
PACKET_SIZE = 9500
HOSTPORT = ""
DESTPORT = ""
DEST_ADDR = ""
WINDOWSIZE = 1

####### MAIN AND HELPER #########

def main():
	global WINDOWSIZE, HOSTPORT, DESTPORT, DEST_ADDR
	if len(sys.argv) != 4:
		usage()
	else:
		try:
			HOSTPORT = eval(sys.argv[1])
			addr1, addr2, addr3, addr4 = sys.argv[2].split('.')
			DESTPORT = eval(sys.argv[3])
			DEST_ADDR = sys.argv[2] , DESTPORT
		except:
			usage()
		print "Please type a command or help for futher instructions:"
		try:
			while True:
				line = sys.stdin.readline().strip()
				if not line:
					break
				elif(line == "terminate"):
					terminate()
				elif (line[:6].lower() == "window"):
					try:
						WINDOWSIZE = eval(line[7:].strip())
						print "Window Size changed to " + str(WINDOWSIZE)
					except:
						usage()
				elif (line.lower() == "help"):
					print "Try the Following Commands: "
					print "start 		      - To start to the server"
					print "terminate          - To terminate the server"
					print "window ##          - To change the window size"
				elif(line == "start"):
					print "Starting the server on port: " + `HOSTPORT`
					ServerRxP.start(HOSTPORT, DEST_ADDR)
					while True:
						# print "Starting to listen"
						returnVal = ServerRxP.listen()
						if not returnVal:
							pass
						elif returnVal[:4] == "RECV":
							pull(returnVal[5:].strip())
						elif returnVal[:4] == "SEND":
							print("Checking for file")
							postFile(returnVal[5:].strip())
			else:
				print "Please enter a valid command or type help for assistance!"
		except KeyboardInterrupt:
			terminate()
		

def usage():
	sys.stdout = sys.stderr
	print 'Usage: ServerFxA X A P'
	print 'X: the odd port # for FxA Server socket'
	print 'A: the IP address of NetEmu'
 	print 'P: the UDP port number of NetEmu'
	sys.exit(2)


####### APPLICATION METHODS #########

def pull(fileName):
	packetArr = ServerRxP.receive()
	if(len(packetArr)):
		convertPacketArr(packetArr, fileName)
		print "Successfully Downloaded file: " + fileName
	else:
		print "File could not be downloaded"

def postFile(fileName):
	print "FxA: Name of file is " + fileName
	packetArr = makePacketArr(fileName)
	print("FxAServer is gonan send this many packets: " + `len(packetArr)`)
	ServerRxP.send(packetArr, fileName, WINDOWSIZE)	

def terminate():
	print "Gracefully shutting down Server"
	ServerRxP.closeSockets()
	exit()

####### HELPER METHODS #########

def createHeader(packets, fileType):
	global DESTPORT, DEST_ADDR, HOSTPORT
	sequenceNumber  = 0
	numPackets = len(packets)
	newPackets = []
	for packet in packets:
		header = "" + str(HOSTPORT) + "," 
		header = header + str(DESTPORT) + "," 
		header = header + str(sequenceNumber) + "," 
		header = header + str(numPackets) + "," 
		header = header + fileType + "|"
		packet = header +  str(packet)
		# print(header)
		m = md5.new()
		# m.update(packet)
		m.update(header)
		checksum = m.hexdigest() #69 bytes = 552 Bits.
		print(checksum)
		packet = checksum + "," + packet
		newPackets.insert(sequenceNumber,(packet,0))
		sequenceNumber = 1 + sequenceNumber
	return newPackets

def makePacketArr(fileName):
	packetArr = []
	incrementor = 0
	global packet_S
	if(not os.path.isfile(fileName)):
		return packetArr
	reader = open(fileName, 'rb')
	nxtPkt = reader.read(DATASIZE)
	while(nxtPkt):
		packetArr.insert(incrementor,nxtPkt)
		nxtPkt = reader.read(DATASIZE)
		incrementor = incrementor + 1
	reader.close()
	fileType = fileName.split(".")[1]
	print(fileType)
	packetArr = createHeader(packetArr, fileType)
	return packetArr

def convertPacketArr(packetArr, fileName):
	f = open(fileName, 'wb')
	while(len(packetArr)):
		f.write(packetArr.pop(0))
	f.close()


main()