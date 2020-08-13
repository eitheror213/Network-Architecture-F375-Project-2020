from socket import *
import socket
import os
import sys
import struct
import time
import select
import binascii  
		
ICMP_ECHO_REQUEST = 8
MAX_HOPS = 15
TIMEOUT  = 3.0 
TRIES    = 2

def checksum(string):
	string = bytearray(string)
	csum = 0
	countTo = (len(string) // 2) * 2

	for count in range(0, countTo, 2):
		thisVal = string[count+1] * 256 + string[count]
		csum = csum + thisVal
		csum = csum & 0xffffffff

	if countTo < len(string):
		csum = csum + string[-1]
		csum = csum & 0xffffffff

	csum = (csum >> 16) + (csum & 0xffff)
	csum = csum + (csum >> 16)
	answer = ~csum
	answer = answer & 0xffff
	answer = answer >> 8 | (answer << 8 & 0xff00)
	return answer

def build_packet():
	myChecksum = 0
	myID = os.getpid() & 0xFFFF
	header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, myID, 1)
	data = struct.pack("d", time.time())
	myChecksum = checksum(header + data)

	if sys.platform == 'darwin':
		myChecksum = socket.htons(myChecksum) & 0xffff
	else:
		myChecksum = htons(myChecksum)
	header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, myID, 1)
	packet = header + data
	return packet

def get_route(hostname):
	timeLeft = TIMEOUT
	for ttl in range(1,MAX_HOPS):
		for tries in range(TRIES):

			destAddr = gethostbyname(hostname)
			icmp = socket.getprotobyname("icmp")
			mySocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, icmp)
                
			mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
			mySocket.settimeout(TIMEOUT)
			try:
				d = build_packet()
				mySocket.sendto(d, (hostname, 0))
				t= time.time()
				startedSelect = time.time()
				whatReady = select.select([mySocket], [], [], timeLeft)
				howLongInSelect = (time.time() - startedSelect)
				if whatReady[0] == []: # Timeout
					print("	*        *        *    Request timed out.")
				recvPacket, addr = mySocket.recvfrom(1024)
				timeReceived = time.time()
				timeLeft = timeLeft - howLongInSelect
				if timeLeft <= 0:
					print("	*        *        *    Request timed out.")
				
			except timeout:
				continue			
			
			else:
				icmpHeader = recvPacket[20:28]
				types, code, checksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader)

				if types == 11:
					bytes = struct.calcsize("d") 
					timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
					print("	%d	rtt=%.0f ms	%s" %(ttl, (timeReceived -t)*1000, addr[0]))
				
				elif types == 3:
					bytes = struct.calcsize("d") 
					timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
					print("	%d    rtt=%.0f ms\t%s" %(ttl, (timeReceived-t)*1000, addr[0]))
				
				elif types == 0:
					bytes = struct.calcsize("d") 
					timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
					print("	%d    rtt=%.0f ms\t%s" %(ttl, (timeReceived - timeSent)*1000, addr[0]))
					return
			
				else:
					print("error")			
				break	
			finally:				
				mySocket.close()		
print("\n\t Route for The Local news in English\n")
#get_route("google.com")
#get_route("baidu.cn")
get_route("thelocal.fr")	


