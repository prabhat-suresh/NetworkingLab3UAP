#! /usr/bin/python3
import os
import random
import threading
import socket
import sys

#Constants defined

magic = 0xC461
version = 1
commandMapper = {"HELLO":0, "DATA":1, "ALIVE":2, "GOODBYE":3}
sequence_number = 0 # initialized to 0, will increment
session_id = random.getrandbits(32) #generate a random 32 bit integer

timerVal = 15
receivedPacket = None
s = socket.socket(family= socket.AF_INET, type= socket.SOCK_DGRAM)
ipAddr, portNo = sys.argv[1], sys.argv[2]
# s.bind((ipAddr, int(portNo)))

def runTimer():
    print("Timer ran out...disconnecting")
    sendPacket("GOODBYE")
    os._exit(0)

timer = None

#Utility Functions
def sendPacket(command):
    global sequence_number
    global timer
    if command[0] == 'D':
        command = (command.split('!!!!'))
        message = "!!!!".join([str(magic), str(version), str(commandMapper[command[0].strip()]), str(sequence_number),str(session_id),command[1].strip()])
    else:
        message = "!!!!".join ([str(magic), str(version), str(commandMapper[command]), str(sequence_number), str(session_id)])
    sequence_number = sequence_number+1
    s.sendto(message.encode(),(ipAddr , int(portNo)))
    timer = threading.Timer(timerVal, runTimer)
    timer.start()


def receivePacket():
    global timer
    while True:
        receivedPacket = s.recvfrom(1024)
        receivedPacket = receivedPacket[0].decode().split('!!!!')
        if int(receivedPacket[0]) != magic or int(receivedPacket[1]) != version :
            continue
        comm = int(receivedPacket[2])
        if comm == 0: #HELLO
            if timer:
                timer.cancel() #cancel timer
        elif comm == 2: #ALIVE
            if timer:
                timer.cancel() #cancel timer
        elif comm == 3: #GOODBYE
            os._exit(0)
        comm = ''



receiverThread = threading.Thread(target=receivePacket)
receiverThread.start()
sendPacket("HELLO")

while True:
    try:
        userInput = input()
        if userInput == 'q':
            raise Exception
        else:
            sendPacket(f"DATA!!!!{userInput}")
    except EOFError:
        print("eof")
        sendPacket("GOODBYE")
        os._exit(0)
    except:
        sendPacket("GOODBYE")
        os._exit(0)

