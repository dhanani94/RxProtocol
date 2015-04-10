import sys
import os.path
import RxPServer
from socket import *

PACKETSIZE = 1024


def main():
	if len(sys.argv) != 4:
		usage()
	else:
		try:
			bindport = eval(sys.argv[1])
			addr1, addr2, addr3, addr4 = sys.argv[2].split('.')
			addr = sys.argv[2] , eval(sys.argv[3])
		except:
			usage()
		print "Type \"start\" to run the Server or Terminate to Stop"
		while True:
			line = sys.stdin.readline().strip()
			if not line:
				break
			elif(line == "terminate"):
				terminate()
			elif(line == "start"):
				print "Starting the server on port: " + `bindport`
				RxPServer.start(bindport, addr)
				while True:
					print "Starting to listen"
					returnVal = RxPServer.listen()
					if not returnVal:
						pass
					elif returnVal[:4] == "RECV":
						getFile(returnVal[5:].strip())
					elif returnVal[:4] == "POST":
						print("FXA: checking for file")
						postFile(returnVal[5:].strip())
			else:
				print "command not understood!"


def convertPacketArr(packetArr, fileName):
	f = open(fileName, 'wb')
	while(len(packetArr)):
		f.write(packetArr.pop(0))
	f.close()

def getFile(fileNameAndNumber):
	fileName, numPackets = fileNameAndNumber.split(",")
	packetArr = RxPServer.receive(numPackets)
	print("Packet size is: " + `len(packetArr)`)
	if(len(packetArr)):
		convertPacketArr(packetArr, fileName)
	else:
		print "File could not be downloaded"


def makePacketArr(fileName):
	packetArr = []
	global PACKETSIZE
	if(not os.path.isfile(fileName)):
		return packetArr
	file = open(fileName, 'rb')
	nxtPkt = file.read(PACKETSIZE)
	while(nxtPkt):
		packetArr.append(nxtPkt)
		nxtPkt = file.read(PACKETSIZE)
	return packetArr


def postFile(fileName):
	print "Name of file is " + fileName
	packetArr = makePacketArr(fileName)
	print("FxAServer is gonan send this many packets: " + `len(packetArr)`)
	RxPServer.send(packetArr)		


def usage():
	sys.stdout = sys.stderr
	print 'Usage: FxAServer X A P'
	print 'X: the odd port # for FxAClient socket'
	print 'A: the IP address of NetEmu'
 	print 'P: the UDP port number of NetEmu'
	sys.exit(2)

def terminate():
	RxPServer.closeSocket()

main()