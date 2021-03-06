# ChatApp

Name: Jingxiang Zhang

UNI: jz3313

## Instruction

This is a simple chat application with clients and server using UDP.

### Registration

Server registration: give a port number between 1024 and 65535 to register.

```shell
python3 ChatApp.py -s portNumber
```

Client registration: give client nickname, server IP, server port and client port to register. Client registration should be after server registration, and command line argument should match server IP and server port. Client port number should be between 1024 and 65536.

```shell
python3 ChatApp.py -c clientName serverIP serverPort clientPort
```

### Chatting

Chat: A client could communicate with other clients by given client name and message in the client mode.

```
send name message
```

### De-registration

De-registration: A client could de-register using dereg command or simply close the SSH window or Ctrl+c. A client can not de register other clients.

```
dereg clientName
```

### Offline Chat

When communicating, if the receiver is offline, the message should be saved and displayed when the receiver is online.

Client could use reg to re-register. After re-registration, the offline message should be displayed if any.

```
reg name
```

### Group Chat

All the clients are added to a channel when registration, messages sent to the channel should be broadcast to all online clients.

send_all command could send the message to all other online clients

```
send_all message
```

## Test

- Test-case 1:

1. start server
2. start client x(the table should be sent from server to x)
3. start client y(the table should be sent from server to x and y)
4. start client z(the table should be sent from server to x and y and z)
5. chat x -> y, y->z, ... , x ->z (All combinations)
6. dereg x (the table should be sent to y, z. x should receive ’ack’)
7. chat y->x (this should fail and message should be sent to server, and message has to be saved for x in the server)
8. chat z->x (same as above)
9. reg x (messages should be sent from server to x, x’s status has to be broadcasted to all the other clients)
10. x, y, z:exit

Client x Input and Output:

```
>>> [Welcome, You are registered.]
>>> [Client table updated.]
>>> [Client table updated.]
>>> [Client table updated.]
>>> send y test x y
>>> [Message received by y.]
>>> send z test x z
>>> [Message received by z.]
>>> test y x
>>> test z x
>>> dereg x
>>> [You are offline. Bye.]
>>> reg x
>>> [You have messages]
>>>  y: 03/25/2022, 20:21:21 testxoffline
>>>  z: 03/25/2022, 20:21:39 testxoffline
>>> [Client table updated.]
```

Client y Input and Output:

```
>>> [Welcome, You are registered.]
>>> [Client table updated.]
>>> [Client table updated.]
>>> testxy
>>> send x testyx
>>> [Message received by x.]
>>> send z testyz
>>> [Message received by z.]
>>> testzy
>>> [Client table updated.]
>>> send x testofflinex
>>> [x offline, message sent to server.]
>>> [Client table updated.]
```

Client z Input and Output:

```
>>> [Welcome, You are registered.]
>>> [Client table updated.]
>>> testxz
>>> testyz
>>> send x testzx
>>> [Message received by x.]
>>> send y testzy
>>> [Message received by y.]
>>> [Client table updated.]
>>> send x testofflinex
>>> [x offline, message sent to server.]
>>> >>> [Client table updated.]
```

- Test-case 2:

1. start server
2. start client x (the table should be sent from server to x )
3. start client y (the table should be sent from server to x and y)
4. dereg y
5. server exit
6. send message x-> y (will fail with both y and server, so should make 5 attempts and exit)

Client x Input and Output:

```
>>> [Welcome, You are registered.]
>>> [Client table updated.]
>>> [Client table updated.]
>>> [Client table updated.]
>>> send y testmessage
>>> [Server not responding]
>>> [Exiting]
```

Client y Input and Output:

```
>>> [Welcome, You are registered.]
>>> [Client table updated.]
>>> dereg y
>>> [You are offline. Bye.]
```

- Test-case 3:

1. start server
2. start client x (the table should be sent from server to x )
3. start client y (the table should be sent from server to x and y)
4. start client z (the table should be sent from server to x , y and z) 
5. send group message x-> y,z

Client x Input and Output:

```
>>> [Welcome, You are registered.]
>>> [Client table updated.]
>>> [Client table updated.]
>>> [Client table updated.]
>>> send_all testgroupmessage
>>> [Message received by Server.]
```

Client y Input and Output:

```
>>> [Welcome, You are registered.]
>>> [Client table updated.]
>>> [Client table updated.]
>>> [Channel_message x: testgroupmessage]
```

Client z Input and Output:

```
>>> [Welcome, You are registered.]
>>> [Client table updated.]
>>> [Channel_message x: testgroupmessage]
```

