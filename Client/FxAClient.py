import sys
import os.path
from socket import *
import RxPClient

status = "NO_CONNECTION"
PACKETSIZE = 1024

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
	global status
	if(status == "NO_CONNECTION"):
		if(RxPClient.connect(bindport, addr)):
			status = "CONNECTED"
			print(status + "connected to server at " + `addr`)
		else:
			print "Client could not establish connection"
	else:
		print "connection already exists"

def function():
	pass

def get(fileName):
	# print "FxC: Name of file is " + fileName
	global status
	if(status == "CONNECTED"):
		packetArr = RxPClient.receive(fileName)
		print("Packet size is: " + `len(packetArr)`)
		if(len(packetArr)):
			convertPacketArr(packetArr, fileName)
		else:
			print "File could not be downloaded"
	else:
		print("Need to establish a connection first!")
		return

def post(fileName):	
	print "Name of file is " + fileName
	global status
	if(status == "CONNECTED"):
			packetArr = makePacketArr(fileName)
			if(packetArr):
				RxPClient.send(packetArr, fileName)
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
	global PACKETSIZE
	if(not os.path.isfile(fileName)):
		return packetArr
	file = open(fileName, 'rb')
	nxtPkt = file.read(PACKETSIZE)
	while(nxtPkt):
		packetArr.append(nxtPkt)
		nxtPkt = file.read(PACKETSIZE)
	return packetArr



def disconnect():
	global status
	status = "NO_CONNECTION"
	RxPClient.closeSockets()

main()









# def get(fileName, s, addr):
# 	#can split filename based on "." to get file type for header reasons 
# 	print("on get the value of status is: " + status)
# 	if(status == "CONNECTED"):
# 		packetArr = makePacketArr(fileName)
# 		if (not packetArr):
# 			print("This file does not exist")
# 		else:
# 			RxPClient.recieve(fileName, addr)
# 	else:
# 		print("Need to establish a connection first!")
# 		return