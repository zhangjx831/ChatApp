from socket import *
import sys

serverPort = int(sys.argv[1])
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
clients = []
index = 1

while True:
    conn, address = serverSocket.recvfrom(2048)
    addr, port = address[0], address[1]
    name = 'client' + str(index)
    index += 1
    info = (name, addr, port, True)
    clients.append(info)
    print(address)
    print('connection to address {} and port {}'.format(addr, port))
    print(clients)
