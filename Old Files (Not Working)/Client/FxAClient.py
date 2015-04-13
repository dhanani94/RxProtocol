import sys
import os.path
from socket import *
import RxPClient
import md5

STATUS = "NO_CONNECTION"
DATASIZE = 1024
HOSTPORT = ""
DESTPORT = ""
DEST_ADDR = ""
WINDOWSIZE = 1


def addHeader(packet, sequenceNumber):
	global C_PORT, DEST_ADDR
	packet = `C_PORT` + "," + `DEST_ADDR[1]` + "," + `sequenceNumber` + "," + `packet`
	return packet

# def createHeader(packets, fileType):
#   port_number             = hostPort
#   emulator_port_number    = netEmuPort
#   packet_sequence_number  = 0
#   total_packets           = len(packets)

#   i = 0
#   final_packets = []

#   for packet in packets:
#     header = "" + str(port_number) + "," + str(emulator_port_number) + "," + str(packet_sequence_number) + "," + str(total_packets) + "," + str(isServer) + "," + fileType + "," + str(file_id) + separator;

#     packet = header +  str(packet)

#     m = md5.new()
#     m.update(packet)
#     checksum = m.hexdigest() #69 bytes = 552 Bits.

#     packet = checksum + "," + packet

#     final_packets.insert(i,(packet,0))
#     i = i + 1

#     packet_sequence_number = 1 + packet_sequence_number

#   return final_packets


def createHeader(packets, fileType):
  port_number             = HOSTPORT
  emulator_port_number    = DESTPORT
  packet_sequence_number  = 0
  total_packets           = len(packets)
  separator               = "|"
  i = 0
  final_packets = []
  for packet in packets:
    header = "" + str(port_number) + "," + str(emulator_port_number) + "," + str(packet_sequence_number) + "," + str(total_packets) +  "," + fileType + separator;
    packet = header +  str(packet)
    print(header)
    m = md5.new()
    # m.update(packet)
    m.update(header)
    checksum = m.hexdigest() #69 bytes = 552 Bits.
    print(checksum)
    packet = checksum + "," + packet

    final_packets.insert(i,(packet,0))
    i = i + 1

    packet_sequence_number = 1 + packet_sequence_number

  return final_packets

def decodeHeader(packet):
	sourcePort, destPort, sequenceNumber, data = packet.split(',')
	return eval(sourcePort), eval(destPort), eval(sequenceNumber), data




def main():
	if len(sys.argv) != 4:
		usage(1)
	else:
		try:
			bindport = eval(sys.argv[1])
			addr1, addr2, addr3, addr4 = sys.argv[2].split('.')
			addr = sys.argv[2] , eval(sys.argv[3])
		except:
			usage(1)
		print "Please type a command:"

	while True:
		line = sys.stdin.readline().strip()   
		if not line:
			break
		elif(line.lower() == "connect"):
			rxpConnect(bindport, addr)
		elif(line[:3].lower() == "get"):
			get(line[4:].strip())
		elif (line[:4].lower() == "post"):
			post(line[4:].strip())
		elif (line.lower() == "disconnect"):
			disconnect()
		elif (line[:6].lower() == "window"):
			try: 
				WINDOWSIZE = eval(line[7:].strip())
				print "Window Size changed to " + str(WINDOWSIZE)
			except:
				usage(2)
		else:
			usage(2)

def usage(errorNum):
	sys.stdout = sys.stderr
	if(errorNum == 1):
		print 'Usage: FxAServer X A P'
		print 'X: the Even port (####) for FxAClient socket'
		print 'A: the IP address (###.###.###.###) of NetEmu'
	 	print 'P: the UDP port number (####) of NetEmu'
	 	sys.exit(2)
 	if(errorNum == 2):
 		print 'Please type another command: '
	
def rxpConnect(bindport, addr):
	global STATUS
	if(STATUS == "NO_CONNECTION"):
		if(RxPClient.connect(bindport, addr)):
			STATUS = "CONNECTED"
			print(STATUS + "connected to server at " + `addr`)
		else:
			print "Client could not establish connection"
	else:
		print "connection already exists"


def get(fileName):
	# print "FxC: Name of file is " + fileName
	global STATUS
	if(STATUS == "CONNECTED"):
		packetArr = RxPClient.receive(fileName)
		try:
			if(len(packetArr)):
				convertPacketArr(packetArr, fileName)
				print "Successfully Downloaded File: " + fileName
			else:
				print "File could not be downloaded"
		except error:
			print "File could not be downloaded"
	else:
		print("Need to establish a connection first!")
		return

def post(fileName):	
	print "Name of file is " + fileName
	global STATUS, WINDOWSIZE
	if(STATUS == "CONNECTED"):
			outgoingPacketArr = makePacketArr(fileName)
			if(outgoingPacketArr):
				fileType = fileName.split(".")[1]
				outgoingPacketArr = createHeader(outgoingPacketArr, fileType)
				RxPClient.send(outgoingPacketArr, fileName, WINDOWSIZE)
			else:
				print("The file: '" + fileName + "' could not be located")
				return
	else:
		print("Need to establish a connection first!")
		return

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
	return packetArr

def disconnect():
	global STATUS
	STATUS = "NO_CONNECTION"
	RxPClient.closeSockets()
	print ("Client Connection Closed!")

main()









# def get(fileName, s, addr):
# 	#can split filename based on "." to get file type for header reasons 
# 	print("on get the value of STATUS is: " + STATUS)
# 	if(STATUS == "CONNECTED"):
# 		packetArr = makePacketArr(fileName)
# 		if (not packetArr):
# 			print("This file does not exist")
# 		else:
# 			RxPClient.recieve(fileName, addr)
# 	else:
# 		print("Need to establish a connection first!")
# 		return