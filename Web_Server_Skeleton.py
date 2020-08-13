#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 29 16:20:02 2020

@author: parallels
"""

#import socket module
#from socket import *
import socket
import sys # In order to terminate the program

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Prepare a sever socket
#Fill in start
PortA = 6789
serverSocket.bind(('localhost', PortA))
serverSocket.listen(1)
print("server running on port:", PortA)
#Fill in end

while True:
   #Establish the connection
   print('Ready to serve...')
   connectionSocket, addr = serverSocket.accept() #Fill in end
   
   try:
      message = connectionSocket.recv(1024) #Fill in end
      #print(message)
      filename = message.split()[1]
      f = open(filename[1:])
      outputdata = f.read() #Fill in end
      print(outputdata)
      #Send one HTTP header line into socket
      connectionSocket.send(bytes('\nHTTP/1.1 200 OK\n\n', 'UTF-8'))
      #Fill in end
      #Send the content of the requested file to the client
      for i in range(0, len(outputdata)):
         connectionSocket.send(outputdata[i].encode())
         connectionSocket.send("".encode())
      connectionSocket.close()
   except IOError:
      #Send response message for file not found
      connectionSocket.send(bytes('\nHTTP/1.1 404 Not Found\n\n', 'UTF-8'))
      #Fill in end
      #Close client socket
      connectionSocket.close()
      #Fill in end
serverSocket.close()
sys.exit()#Terminate the program after sending the corresponding data