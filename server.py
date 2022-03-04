import socket
from RDT import Sender
from RDT import Receiver
from threading import Thread
import os
from pathlib import Path
import sys


# Connection Data
host = '127.0.0.1'
port = 55000

# Starting Server With TCP Socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Starting Server With UDP Socket.
server_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Lists For Clients and Their Nicknames
clients = []
client_names = []
files_requests = []

# lock = Lock()

"""
In this func, the server connect with new client, asks for his name and informs about that
to all other members of the chat.
"""
def receive():
    udp_thread = Thread(target=send_file)
    udp_thread.start()
    while True:
        # Accept Connection
        client, address = server.accept()
        print(f"Connected with {(str(address))}")

        # Request And Store Nickname
        client.send('NAME'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        client_names.append(nickname)
        clients.append(client)

        # Print And Broadcast Nickname
        print(f"Nickname is {nickname}")
        broadcast(f"{nickname} joined!".encode('utf-8'))
        client.send("Connected to server!".encode('utf-8'))

        # Start Handling Thread For Client
        thread = Thread(target=handle, args=(client,))
        thread.start()

"""
This function is responsible for handling messages from clients.
The server receives the message to the client and classifies it 
according to the first character of the message:
    0 -> sending the client messages to all the connected clients.
    1 -> sending the client messages to specific connected clients.
    2 -> sending to the client the online chat members.
    3 -> sending to the client a list of server's files:
    4 -> sending to the client the requested file by UDP socket.
"""
def handle(client):
    while True:
        try:
            # recv the messages
            message = client.recv(1024).decode('utf-8')

            # 0) Sending Messages To All Connected Clients:
            if message.startswith('0'):
                msg = message.encode('utf-8')[1:]
                broadcast(msg)

            # 1) Sending Messages To Specific Connected Clients:
            elif message.startswith('1'):
                send_message(message[1:], client)

            # 2) this func send to the client the online chat members:
            elif message.startswith('2'):
                send_clients(client)

            # 3) this func sends to the client the server's files:
            elif message.startswith('3'):
                send_files_list(client)

            # 4) This function sends the requested file to the client:
            elif message.startswith('4'):
                input = message[1:].split(':')

                addr = input[0]
                addr = eval(addr[1:-1])
                file_name = input[1]
                save_as = input[2]

                # if the requested file doesn't exist:
                if file_name not in os.listdir('.'):
                    client.send(f"The Is No File Named: {file_name}")

                # if the requested file does exist:
                else:
                    files_requests.append(message[1:])
                    files_thread = Thread(target=send_file, args=(server_udp, addr, file_name, save_as,))
                    files_thread.start()


        except:
            # Removing And Closing Clients
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = client_names[index]
            broadcast(f"{nickname} left!".encode('utf-8'))
            print(f"{nickname} left!")
            client_names.remove(nickname)
            break

"""
0) Sending Messages To All Connected Clients
"""
def broadcast(message):
    print("broadcast func")
    for client in clients:
        client.send(message)

"""
1) Sending Messages To Specific Connected Clients.
"""
def send_message(message, client):
    print("send func")
    flag = False
    for name in client_names:
        if message.startswith(str(name)):
            msg = message.encode('utf-8')[(len(name)):]
            index = client_names.index(name)
            clients[index].send(msg)
            client.send(msg)
            flag = True
            break
    if not flag:
        client.send("wrong name... try again".encode('utf-8'))

"""
2) this func send to the client the online chat members.
"""
def send_clients(client):

    msg = "The Online Members Are:\n"
    for name in client_names:
        msg = msg + "         " + str(name) + "\n"
    client.send(msg.encode('utf-8'))

"""
3) this func sends to the client the server's files.
"""
def send_files_list(client):

    files = [x for x in os.listdir('.') if x.endswith(".txt")]
    if len(files) == 0:
        client.send("There Are No Files\n".encode('utf-8'))
    else:
        msg = "The Server Files Are:\n"
        for file in files:
            msg = msg + "     " + str(file) + "\n"
        client.send(msg.encode('utf-8'))

"""
4)
This part represents the sending of files by udp socket.
"""
def send_file():

    while True:

        if len(files_requests) > 0:

            info = files_requests.pop(0).split(':')
            file_name = info[1]
            save_as = info[2]
            str_addr = info[0]
            ADRR = eval(str_addr[1:-1])  # "remove" the from start '(' and "remove" from end ')' and convert the string to tuple.

            WINDOW_SIZE = 4
            BUFF = 1024
            FRAME_NUM = 0
            CURR_SIZE = 0  # represents the file size downloaded so far
            WINDOW = [-1] * WINDOW_SIZE
            FRAME_BUFF = [''] * (WINDOW_SIZE * 2)
            START_WINDOW = 0
            END_WINDOW = START_WINDOW + WINDOW_SIZE - 1
            boolean_ACK = [False] * WINDOW_SIZE
            print(WINDOW)

            # fileName = os.path.basename(file_name)
            file = Path(file_name)
            file_size = os.path.getsize(file)  # the file size in bytes

            print("size:", file.stat().st_size)

            # 1) sends the file details to client:
            data = (f"{save_as}|||{str(file_size)}|||{str(WINDOW_SIZE)}").encode('utf-8')
            server_udp.settimeout(2)
            server_udp.sendto(data, ADRR)
            f = open(file_name, 'rb')  # open the file.
            # print(file_size)

            while CURR_SIZE < file_size:
                index = 0
                print(12345)
                try:
                    print(1)
                    for i in range(START_WINDOW, END_WINDOW + 1):
                        WINDOW[index] = i
                        index += 1
                        print(WINDOW)

                    data = f.read(BUFF - 1)
                    if not data and False not in boolean_ACK:
                        print("successes")
                        break

                    # print("send checksum : ", calc_checksum(data))
                    # data = data = str(FRAME_NUM) + data + str(calc_checksum(data))
                    # data = data = str(FRAME_NUM) + data
                    data = str(FRAME_NUM) + data.decode()
                    FRAME_BUFF[FRAME_NUM] = data
                    server_udp.sendto(data.encode(), ADRR)
                    print(data)
                    FRAME_NUM += 1
                    FRAME_NUM %= WINDOW_SIZE * 2

                    print(FRAME_NUM)

                    if FRAME_NUM is WINDOW_SIZE * 2:
                        FRAME_NUM %= WINDOW_SIZE * 2

                    CURR_SIZE += len(data) - 1

                    if CURR_SIZE > file_size:
                        CURR_SIZE = file_size

                    rate = round(float(CURR_SIZE) / float(file_size) * 100, 2)
                    print(CURR_SIZE, "/", file_size, rate, "%\n")
                    if CURR_SIZE == file_size:
                        print("Success")

                    print(WINDOW)

                    ACK, address = server_udp.recvfrom(BUFF)
                    if "ACK" in ACK.decode():
                        if int(ACK.decode()[3]) is START_WINDOW:
                            # if START_WINDOW is WINDOW_SIZE * 2:
                            #     START_WINDOW %= WINDOW_SIZE * 2
                            START_WINDOW += 1
                            START_WINDOW %= WINDOW_SIZE * 2
                            END_WINDOW = START_WINDOW + WINDOW_SIZE - 1
                            END_WINDOW %= WINDOW_SIZE * 2

                        print("received ACK number is ", ACK.decode()[3])
                        boolean_ACK[WINDOW.index(int(ACK.decode()[3]))] = True

                except socket.timeout:
                    print("Time out")
                    for i in range(START_WINDOW, END_WINDOW + 1):
                        if boolean_ACK[i] is False:
                            server_udp.sendto(FRAME_BUFF[WINDOW.index(i)].encode(), ADRR)

            f.close()
            # lock.release()  # releasing the above part

class RDT()


print("Server is listening...")
receive()
