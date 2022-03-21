from socket import *
import sys

serverName, serverIP, serverPort, clientPort = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
clientSocket = socket(AF_INET, SOCK_DGRAM)
info = (serverName, serverIP, serverPort)
print(info, clientPort)
clientSocket.connect((serverIP, serverPort))

