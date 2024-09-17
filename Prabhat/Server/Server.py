#! /usr/bin/python3

import socket
import threading
import sys
import os

# Dictionary to keep track of active sessions
sessions = {}
sessions_lock = threading.Lock()
expected_sequence_number = {}
portNo = int(sys.argv[1])
client_address_mapper = {}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(("127.0.0.1" , portNo))
def readFromTerminal():
    while True:
        try:
            server_inp = input()
            if server_inp == 'q':
                raise Exception
        except EOFError:
            kill_all_clients()
        except:
            kill_all_clients()

def kill_all_clients():
    with sessions_lock:
        for session_id in list(sessions):
            response = [str(0xC461),"1", '3', str(expected_sequence_number[session_id]), str(session_id)]
            response = handle_client(response, session_id)
            # print(response)
            if response:
                server_socket.sendto(response.encode("utf-8"), client_address_mapper[session_id])
            sessions.pop(session_id)

    os._exit(0)

def handle_client(data, session_id):
    global expected_sequence_number
    # Process the received data
    if int(data[0]) != 0xC461 or int(data[1]) != 1:
        return None
    if int(data[3]) == expected_sequence_number[session_id]:
        expected_sequence_number[session_id]+=1
    elif int(data[3]) > expected_sequence_number[session_id]:
        print("lost packet")
        return None
    elif int(data[3]) == expected_sequence_number[session_id]-1:
        print("duplicate packet")
        return None
    else:
        responseCommand = "3"
        response = "!!!!".join([str(0xC461),"1", responseCommand, data[3], data[4]])
        return response

    message = ""
    responseCommand = data[2]
    if data[2] == "0":
        message = "Session Created"
        print(f"{hex(int(data[4]))} [{data[3]}] {message}")
    elif data[2] == "1":
        if len(data) == 6:
            message = data[5]
        responseCommand = "2"
        print(f"{hex(int(data[4]))} [{data[3]}] {message}")
    else:
        message = f"GOODBYE from client"
        print(f"{hex(int(data[4]))} [{data[3]}] {message}")
        print(f"{hex(int(data[4]))} Session closed")
    response = "!!!!".join([str(0xC461),"1", responseCommand, data[3], data[4]])
    return response


def start_server(portNo):
    print(f"Waiting on port {portNo}...")

    while True:
        global client_address_mapper
        data, client_address = server_socket.recvfrom(1024)
        data = data.decode("utf-8").split('!!!!')
        
        # Extract session ID from the packet
        session_id = data[4]
        client_address_mapper[session_id] = client_address
        with sessions_lock:
            if session_id in sessions:
                # If session exists, use the existing session
                response = handle_client(data, session_id)
            else:
                expected_sequence_number[session_id] = 0
                # If session does not exist, create a new one
                response = handle_client(data, session_id)
                sessions[session_id] = 1

        # Check if the session already exists

        # Send the response back to the client
        if response == None or response.split('!!!!')[2] == 3:
            if session_id in sessions:
                sessions.pop(session_id)
            continue
        server_socket.sendto(response.encode("utf-8"), client_address)


if __name__ == "__main__":
    std_input_thread = threading.Thread(target=readFromTerminal)
    std_input_thread.start()
    start_server(portNo)
