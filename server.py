import socket
import threading

# Connection Data
host = '127.0.0.1'
port = 55000

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Lists For Clients and Their Nicknames
clients = []
clients_names = []

# Sending Messages To All Connected Clients
def broadcast(message):
    print("broadcast func")
    for client in clients:
        client.send(message)

# Sending Messages To Specific Connected Clients
def send_message(message, client):
    print("send func")
    flag = False
    for name in clients_names:
        if message.startswith(str(name)):
            msg = message.encode('utf-8')[(len(name)):]
            index = clients_names.index(name)
            clients[index].send(msg)
            client.send(msg)
            flag = True
            break
    if not flag:
        client.send("wrong name... try again".encode('utf-8'))

def send_clients(client):
    msg = "The Online Members Are:\n"
    for name in clients_names:
        msg = msg + "         " + str(name) + "\n"
    client.send(msg.encode('utf-8'))

# Handling Messages From Clients
def handle(client):
    while True:
        try:
            # recv the messages
            message = client.recv(1024).decode('utf-8')

            if message.startswith('0'):
                msg = message.encode('utf-8')[1:]
                broadcast(msg)

            elif message.startswith('1'):
                send_message(message[1:], client)

            elif message.startswith('2'):
                send_clients(client)

        except:
            # Removing And Closing Clients
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = clients_names[index]
            broadcast(f"{nickname} left!".encode('utf-8'))
            print(f"{nickname} left!")
            clients_names.remove(nickname)
            break

def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print(f"Connected with {(str(address))}")

        # Request And Store Nickname
        client.send('NAME'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        clients_names.append(nickname)
        clients.append(client)

        # Print And Broadcast Nickname
        print(f"Nickname is {nickname}")
        broadcast(f"{nickname} joined!".encode('utf-8'))
        client.send("Connected to server!".encode('utf-8'))

        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("Server is listening...")
receive()
