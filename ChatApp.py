#!/usr/bin/python3

import sys
import time
import threading
import datetime
import collections
from socket import *


class Server:
    def __init__(self, serverPort):
        self.serverSocket = socket(AF_INET, SOCK_DGRAM)
        self.serverSocket.bind(('', serverPort))
        self.clientsTable = []
        self.messageBox = collections.defaultdict(list)
        self.checking = [False for _ in range(len(self.clientsTable))]
        self.checkAlive = False

    def checkingGroup(self, sendername, savem):
        time.sleep(0.5)
        update = False
        for i, client in enumerate(self.clientsTable):
            if client[0] == sendername:
                continue
            if not self.checking[i]:
                self.messageBox[client[0]].append(savem)
                if client[3] == 'Yes':
                    client[3] = 'No'
                    update = True
        if update:
            broadcastmessage = 'Update' + '\t' + ' '.join([','.join(item) for item in self.clientsTable])
            for client in self.clientsTable:
                if client[3] == 'Yes':
                    self.serverSocket.sendto(broadcastmessage.encode(), (client[1], int(client[2])))

    def checkingAlive(self, receiverName, senderName, senderAddress, timestamp, m):
        time.sleep(0.5)
        if self.checkAlive:
            err = 'Message' + '[Client {} exists!!]'.format(receiverName)
            self.serverSocket.sendto(err.encode(), senderAddress)
            self.checkAlive = False
        else:
            update = False
            for client in self.clientsTable:
                if client[0] == receiverName and client[3] == 'Yes':
                    client[3] = 'No'
                    update = True
            if update:
                broadcastmessage = 'Update' + '\t' + ' '.join([','.join(item) for item in self.clientsTable])
                for client in self.clientsTable:
                    if client[3] == 'Yes':
                        self.serverSocket.sendto(broadcastmessage.encode(), (client[1], int(client[2])))
            self.messageBox[receiverName].append(senderName + ': ' + timestamp + ' ' + m)

    def server(self):
        while True:
            messages, address = self.serverSocket.recvfrom(2048)
            message = messages.decode().split('\t')
            tag = message[0]
            if tag == 'Reg':
                name = message[1]
                append = True
                for client in self.clientsTable:
                    if client[0] == name:
                        client[3] = 'Yes'
                        append = False
                        # Re-register and send offline message
                        if name in self.messageBox and self.messageBox[name]:
                            reply = 'Message' + '\t' + '[You have messages]'
                            self.serverSocket.sendto(reply.encode(), (client[1], int(client[2])))
                            for m in self.messageBox[name]:
                                offlinemessage = 'Message' + '\t ' + m
                                self.serverSocket.sendto(offlinemessage.encode(), (client[1], int(client[2])))
                            self.messageBox[name] = []
                if append:
                    addr, port = str(address[0]), str(address[1])
                    info = [name, addr, port, 'Yes']
                    self.clientsTable.append(info)
                    ack = 'ACK' + '\t' + 'RegOK'
                    self.serverSocket.sendto(ack.encode(), address)
                broadcastmessage = 'Update' + '\t' + ' '.join([','.join(item) for item in self.clientsTable])
                for client in self.clientsTable:
                    if client[3] == 'Yes':
                        self.serverSocket.sendto(broadcastmessage.encode(), (client[1], int(client[2])))

            elif tag == 'DeReg':
                name = message[1]
                for client in self.clientsTable:
                    if client[0] == name:
                        client[3] = 'No'
                m = 'ACK' + '\t' + 'DeReg'
                self.serverSocket.sendto(m.encode(), address)
                broadcastmessage = 'Update' + '\t' + ' '.join([','.join(item) for item in self.clientsTable])
                for client in self.clientsTable:
                    if client[3] == 'Yes':
                        self.serverSocket.sendto(broadcastmessage.encode(), (client[1], int(client[2])))

            elif tag == 'Save-Message':
                sendername, receivername, m = message[1], message[2], message[3]
                timestamp = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                ack = 'ACK' + '\t' + 'Save'
                self.serverSocket.sendto(ack.encode(), address)
                for client in self.clientsTable:
                    if receivername == client[0]:
                        ack = 'ACK' + '\t' + 'checkAlive' + '\t' + receivername
                        self.serverSocket.sendto(ack.encode(), (client[1], int(client[2])))
                        check = threading.Thread(target=self.checkingAlive,
                                                 args=(receivername, sendername, address, timestamp, m))
                        check.start()

            elif tag == 'ACK' and message[1] == 'All':
                for i, client in enumerate(self.clientsTable):
                    if client[0] == message[2]:
                        self.checking[i] = True

            elif tag == 'ACK' and message[1] == 'checkAlive':
                self.checkAlive = True

            elif tag == 'Message_all':
                reply = 'ACK' + '\t' + 'Server_all'
                self.serverSocket.sendto(reply.encode(), address)
                sendername = ''
                for client in self.clientsTable:
                    if client[1] == address[0] and int(client[2]) == address[1]:
                        sendername = client[0]

                for client in self.clientsTable:
                    if client[0] == sendername or client[3] == 'No':
                        continue
                    m = 'Message_all' + '\t' + sendername + '\t' + ' '.join(message[1:])
                    self.serverSocket.sendto(m.encode(), (client[1], int(client[2])))
                self.checking = [False for _ in range(len(self.clientsTable))]
                savem = sendername + ': ' + datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") \
                        + ' Channel-Message ' + sendername + ': ' + ' '.join(message[1:])
                c = threading.Thread(target=self.checkingGroup, args=(sendername, savem))
                c.start()

class Client:
    def __init__(self, clientName, serverIP, serverPort, clientPort):
        # Register a client and create client socket
        self.clientName = clientName
        self.serverIP = serverIP
        self.serverPort = serverPort
        self.clientPort = clientPort
        self.clientsTable = []
        self.messageAck = False
        self.deregAck = False
        self.channelAck = False
        self.saveAck = False
        self.clientSocket = socket(AF_INET, SOCK_DGRAM)
        self.clientSocket.bind(('', clientPort))
        message = 'Reg' + '\t' + clientName
        self.clientSocket.sendto(message.encode(), (serverIP, serverPort))
        self.threadLock = threading.Lock()
        self.runSend = True
        self.runReceive = True

    def send(self):
        while self.runSend:
            input_message = input('>>> ')
            message = input_message.split(' ')
            tag = message[0]
            if tag == 'send':
                name = message[1]
                for client in self.clientsTable:
                    if name == client[0]:
                        address, port = client[1], int(client[2])
                        m = 'Message' + '\t' + ' '.join(message[2:])
                        if client[3] == 'Yes':
                            self.clientSocket.sendto(m.encode(), (address, port))
                            # Wait for ACK for 500 msecs
                            time.sleep(0.5)
                            if self.messageAck:
                                self.threadLock.acquire()
                                self.messageAck = False
                                self.threadLock.release()
                            else:
                                retry = 0
                                while retry < 5 and not self.saveAck:
                                    m = 'Save-Message' + '\t' + self.clientName + '\t' + name + '\t' + ' '.join(message[2:])
                                    self.clientSocket.sendto(m.encode(), (self.serverIP, self.serverPort))
                                    print('>>>', '[No ACK from {}, message sent to server.]'.format(message[1]))
                                    retry += 1
                                    time.sleep(0.5)
                                if retry == 5:
                                    print('>>>', '[Server not responding]')
                                    print('>>>', '[Exiting]')
                                    self.runSend = False
                                    self.runReceive = False
                                else:
                                    self.threadLock.acquire()
                                    self.saveAck = True
                                    self.threadLock.release()
                        else:
                            retry = 0
                            print('>>>', '[{} offline, message sent to server.]'.format(message[1]))
                            while retry < 5 and not self.saveAck:
                                m = 'Save-Message' '\t' + self.clientName + '\t' + message[1] + '\t' + message[2]
                                self.clientSocket.sendto(m.encode(), (self.serverIP, self.serverPort))
                                retry += 1
                                time.sleep(0.5)
                            if retry == 5:
                                print('>>>', '[Server not responding]')
                                print('>>>', '[Exiting]')
                                self.runSend = False
                                self.runReceive = False
                            else:
                                self.threadLock.acquire()
                                self.saveAck = True
                                self.threadLock.release()

            elif tag == 'dereg':
                if message[1] != clientName:
                    print('>>>', '[Error, you can not de-register others]')
                    continue
                m = 'DeReg' + '\t' + message[1]
                retry = 0
                # Retry for 5 times until receiving ack
                while retry < 5 and not self.deregAck:
                    self.clientSocket.sendto(m.encode(), (self.serverIP, self.serverPort))
                    retry += 1
                    time.sleep(0.5)
                if retry == 5:
                    print('>>>', '[Server not responding]')
                    print('>>>', '[Exiting]')
                    self.runSend = False
                    self.runReceive = False
                else:
                    self.threadLock.acquire()
                    self.deregAck = False
                    self.threadLock.release()

            elif tag == 'reg':
                m = 'Reg' + '\t' + message[1]
                self.clientSocket.sendto(m.encode(), (self.serverIP, self.serverPort))

            elif tag == 'send_all':
                m = 'Message_all' + '\t' + message[1]
                retry = 0
                while retry < 5 and not self.channelAck:
                    self.clientSocket.sendto(m.encode(), (self.serverIP, self.serverPort))
                    retry += 1
                    time.sleep(0.5)
                if retry == 5:
                    print('>>>', '[Server not responding]')
                    print('>>>', '[Exiting]')
                    self.runSend = False
                    self.runReceive = False
                else:
                    self.threadLock.acquire()
                    self.channelAck = False
                    self.threadLock.release()

            else:
                print('>>>', '[Bad request, please re-input]')

    def receive(self):
        while self.runReceive:
            messages, address = self.clientSocket.recvfrom(2048)
            message = messages.decode().split('\t')
            tag = message[0]
            if tag == 'Update':
                self.clientsTable = [item.split(',') for item in message[1].split(' ')]
                print('>>>', '[Client table updated.]')

            elif tag == 'Message':
                print('>>>', message[1])
                ack = 'ACK' + '\t' + 'RecOK' + '\t' + clientName
                self.clientSocket.sendto(ack.encode(), address)

            elif tag == 'Message_all':
                print('>>>', '[Channel_message {}: {}]'.format(message[1], message[2]))
                ack = 'ACK' + '\t' + 'All' + '\t' + clientName
                self.clientSocket.sendto(ack.encode(), (self.serverIP, self.serverPort))

            elif tag == 'ACK':
                if message[1] == 'Server':
                    print('>>>', '[Message received by the server and saved.]')
                elif message[1] == 'DeReg':
                    print('>>>', '[You are offline. Bye.]')
                    self.threadLock.acquire()
                    self.deregAck = True
                    self.threadLock.release()
                elif message[1] == 'Server_all':
                    print('>>>', '[Message received by Server.]')
                    self.threadLock.acquire()
                    self.channelAck = True
                    self.threadLock.release()
                elif message[1] == 'RegOK':
                    print('>>>', '[Welcome, You are registered.]')
                elif message[1] == 'RecOK':
                    print('>>>', '[Message received by {}.]'.format(message[2]))
                    self.threadLock.acquire()
                    self.messageAck = True
                    self.threadLock.release()
                elif message[1] == 'Save':
                    self.threadLock.acquire()
                    self.saveAck = True
                    self.threadLock.release()

            else:
                raise ValueError('Bad request, client down')

    def run(self):
        c_send = threading.Thread(target=self.send)
        c_receive = threading.Thread(target=self.receive)
        c_send.start()
        c_receive.start()
        c_send.join()
        c_receive.join()
        print('>>>', '[Client exit.]')


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == '-s':
        serverPort = int(sys.argv[2])
        if serverPort < 1024 or serverPort > 65535:
            raise ValueError('Bad server port')
        server = Server(serverPort)
        server.server()

    elif mode == '-c':
        clientName, serverIP, serverPort, clientPort = sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])

        for IP in serverIP.split('.'):
            if int(IP) < 0 or int(IP) > 255:
                raise ValueError('Bad IP address')
        if serverPort < 1024 or serverPort > 65535:
            raise ValueError('Bad server port')
        if clientPort < 1024 or clientPort > 65535:
            raise ValueError('Bad client port')

        client = Client(clientName, serverIP, serverPort, clientPort)
        client.run()

    else:
        raise ValueError('Bad mode')