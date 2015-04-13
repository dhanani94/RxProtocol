#######IMPORTS#########

import sys
import ClientRxP
import os
import md5

######IMPLEMENT KEYBOARD INTERRUPTS AND DOUBLE CHECK EXIT SEQUENCE!!!!!!!!!!!!!!!!!!!!!#######################################
####### GLOBAL VARIABLES! #########

STATUS = "NO_CONNECTION"
DATASIZE = 9038
PACKET_SIZE = 9500
HOSTPORT = ""
DESTPORT = ""
DEST_ADDR = ""
WINDOWSIZE = 1


####### MAIN AND HELPER #########

def main():
	global HOSTPORT, DESTPORT, DEST_ADDR, WINDOWSIZE
	if len(sys.argv) != 4:
		usage(1)
	else:
		try:
			HOSTPORT = eval(sys.argv[1])
			addr1, addr2, addr3, addr4 = sys.argv[2].split('.')
			DESTPORT = eval(sys.argv[3])
			DEST_ADDR = sys.argv[2] , DESTPORT
		except:
			usage(1)
		print "Please type a command or help for futher instructions:"
	try:
		while True:
			line = sys.stdin.readline().strip()   
			if not line:
				break
			elif(line.lower() == "connect"):
				rxpConnect(HOSTPORT, DEST_ADDR)
			elif(line[:4].lower() == "pull"):
				pull(line[4:].strip())
			elif (line[:4].lower() == "push"):
				push(line[4:].strip())
			elif (line.lower() == "disconnect"):
				disconnect()
			elif (line[:6].lower() == "window"):
				try:
					WINDOWSIZE = eval(line[7:].strip())
					print "Window Size changed to " + str(WINDOWSIZE)
				except:
					usage(2)
			elif (line.lower() == "disconnect"):
				disconnect()
			elif (line.lower() == "help"):
				print "Try the Following Commands: "
				print "connect 			- To connect to the server"
				print "pull name.type     - To pull a file from the server"
				print "push name.type     - To push a file to the server"
				print "window ##          - To change the window size"
				print "disconnect         - To disconnect from the server"
			else:
				usage(2)
	except KeyboardInterrupt:
		disconnect()
		print "Gracefully quitting Client"
		exit()


def usage(errorNum):
	sys.stdout = sys.stderr
	if(errorNum == 1):
		print 'Usage: ServerFxA X A P'
		print 'X: the Even port (####) for FxA Client socket'
		print 'A: the IP address (###.###.###.###) of NetEmu'
	 	print 'P: the UDP port number (####) of NetEmu'
	 	sys.exit(2)
 	if(errorNum == 2):
 		print 'Please type another command: '


####### APPLICATION METHODS #########

def rxpConnect(bindport, addr):
	global STATUS
	if(STATUS == "NO_CONNECTION"):
		if(ClientRxP.connect(bindport, addr)):
			STATUS = "CONNECTED"
			print("connected to server at " + `addr`)
		else:
			print "Client could not establish connection"
	else:
		print "connection already exists"
	
def disconnect():
	global STATUS
	STATUS = "NO_CONNECTION"
	ClientRxP.closeSockets()
	print ("Client Connection Closed!")

def pull(fileName):
	global STATUS
	if(STATUS == "CONNECTED"):
		packetArr = ClientRxP.receive(fileName)
		try:
			if(len(packetArr)):
				convertPacketArr(packetArr, fileName)
				print "Successfully Downloaded File: " + fileName
			else:
				print "File could not be found"
		except:
			print "File could not be found"
	else:
		print("Need to establish a connection first!")
		return
	pass

def push(fileName):
	print "Name of file is " + fileName
	global STATUS, WINDOWSIZE
	if(STATUS == "CONNECTED"):
		outgoingPacketArr = makePacketArr(fileName)
		if(outgoingPacketArr):
			#the file has been made into packets and the packets have each been made with their headers + checksum in the following format
			# packet arry = ((sequence#, packet#), (sequence#, packet#))
			# packet# = checksum, hostport, destport, sequencenumber, numpackets, filetype | DATA
			#where checksum was calculated using everythinf behind it in the packet! 
			ClientRxP.send(outgoingPacketArr, fileName, WINDOWSIZE)
		else:
			print("The file: '" + fileName + "' could not be located")
			return
	else:
		print("Need to establish a connection first!")
		return


####### HELPER METHODS #########

def convertPacketArr(packetArr, fileName):
	f = open(fileName, 'wb')
	while(len(packetArr)):
		f.write(packetArr.pop(0))
	f.close()

def makePacketArr(fileName):
	packetArr = []
	incrementor = 0
	global DATASIZE
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


main()