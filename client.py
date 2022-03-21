from socket import *
import sys

serverName, serverIP, serverPort, clientPort = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
clientSocket = socket(AF_INET, SOCK_DGRAM)
info = (serverName, serverIP, serverPort)
clientSocket.bind(('', clientPort))
print(info, clientPort)
message = 'test'
clientSocket.sendto(message.encode(), (serverIP, serverPort))

