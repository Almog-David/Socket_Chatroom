import sys
import threading
import socket
import os
import pickle

SERVER_IP = '127.0.0.1'
SERVER_PORT = 50008  # TCP Port
SERVER_UDP_PORT = 55001  # UDP Port


class Server:

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # creating an TCP socket for the server
        self.server.bind((SERVER_IP, SERVER_PORT))  # connecting the server to the IP and port
        self.server.listen()  # we are ready to listen - ready to get clients into the chat
        self.sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # creating a UDP socket for the server
        self.sender.bind((SERVER_IP, SERVER_UDP_PORT))  # connecting the sudp server to thr IP and port
        print("ready to listen")
        # we store all the users in a dictionary where the key is the client itself and the value is his name
        self.connected_clients = {}  # we save all the connected clients in a dictionary of address-> name
        self.server_files = {}  # we save all the "ready to send files" to save time (like local server) for future
        # downloads

    def broadcast_msg(self, msg):  # transfer a message to all the connected users.
        for client in self.connected_clients:
            # we go through the clients that connected to the server and send them the message
            client.send(msg)

    def get_msg(self, client):  # get the messages from the client and activate the right function based on the text
        while True:
            try:
                message = client.recv(1024).decode()
                if message == "<connect>":
                    self.connect()

                elif message == "<get_users>":
                    users = self.online_users()
                    client.send(f'users online: {users}'.encode())

                elif message == "disconnect":
                    self.disconnect(client)

                elif message[0] == '@':
                    message = message.split(':')
                    print(message)
                    print(message[0][1:])
                    self.private_msg(client, message[0][1:], message[1])

                elif message == "<get_files>":
                    files = self.get_files()
                    client.send(f'files on server: {files}'.encode())

                elif "download:" in message:
                    print("Server: Ask to ", message)
                    message = message.split(':')
                    list_of_files = self.get_files()
                    file_name = message[1]
                    if file_name not in list_of_files:
                        client.send(f'file is not in the server.try again'.encode())
                    else:
                        if file_name in self.server_files.keys():
                            file = self.server_files[file_name]
                        else:
                            file, num_of_packets = self.create_file_for_download(file_name)
                            self.server_files[file_name] = file
                            print("good")
                        client.send(f'ready for download: {file_name}'.encode())
                        threading.Thread(target=self.send_file, args=(file, num_of_packets)).start()

                else:
                    name = self.connected_clients[client]
                    self.broadcast_msg(f'{name} :{message}'.encode())
            except:
                self.disconnect(client)

    def connect(self):  # connect a client to the server
        while True:
            client, address = self.server.accept()
            print(f'connected with {str(address)}')
            client.send('name'.encode())
            name = client.recv(1024).decode()
            self.connected_clients[client] = name
            self.broadcast_msg(f'{name} joined the chat!'.encode())
            client.send('connected to the chat'.encode())

            thread = threading.Thread(target=self.get_msg, args=(client,))
            thread.start()

    def disconnect(self, client):  # disconnect a client from the server
        name = self.connected_clients[client]
        self.broadcast_msg(f'{name} left the chat!'.encode())
        del self.connected_clients[client]
        client.send("disconnected".encode())
        client.close()
        sys.exit()

    def get_files(self):  # get all the files that the server have
        file_name = ''
        files = os.listdir("./Files")
        for file in files:
            file_name += file + ','
        file_name = file_name[:len(file_name) - 1]
        return file_name

    def online_users(self):  # get the names of all the online users
        clients_name = ''
        for k, v in self.connected_clients.items():
            clients_name += v + ','
        clients_name = clients_name[:len(clients_name) - 1]

        return clients_name

    def private_msg(self, sent_from, name, msg):  # sends a private message to a person in the chat
        for client in self.connected_clients.keys():
            if self.connected_clients[client] == name:
                client.send(f'{self.connected_clients[sent_from]} -> {name}: {msg}'.encode())

    def create_file_for_download(self, file_name):
        print("Creating the segments for:", file_name)
        file_segments = {}
        path = './Files/' + file_name
        file = open(path, 'r')
        num_of_packets = os.path.getsize(path)
        num_of_packets = int(num_of_packets / 2044)
        # we take the size of the file and split it to chunks in size 2042, so we can add the ack number of the packet
        # (6 bytes) and save it in the dictionary, and we will use it to track the packets we send.
        chunk = file.read(2044)
        ack = 0
        while ack <= num_of_packets:
            info = [ack, chunk]
            msg = pickle.dumps(info)
            file_segments[ack] = msg
            ack += 1
            chunk = file.read(2044)
        file.close()
        print('SERVER: Data split to packets')
        return file_segments, num_of_packets

    def send_file(self, ready_file, num_of_packets):
        print("entered")
        received = 0
        ack_list = list(range(0, num_of_packets + 1))
        print(len(ack_list))
        while True:
            try:
                message, addr = self.sender.recvfrom(1024)
                message = message.decode()
                if message == "connected":
                    self.sender.sendto("connected".encode(), addr)

                elif message == "start":
                    while received <= num_of_packets:
                        expected = ack_list[0]
                        for i in range(0, 1):
                            num = ack_list[i]
                            print(f'sending packet number {num} to the client')
                            self.sender.sendto(ready_file[num], addr)
                            print("sent")
                        for i in range(0, 1):
                            print("waiting to receive")
                            answer = int.from_bytes(self.sender.recvfrom(4)[0], "big")
                            print(f'packet number {answer} has reached to the client')
                            if answer == expected:
                                expected += 1
                            else:
                                ack_list.remove(expected)
                                ack_list.append(expected)

                            ack_list.remove(answer)
                            ready_file.pop(answer)
                            received += 1

                elif message == "got all the data":
                    sys.exit()
                    break

                if received > num_of_packets:
                    self.sender.sendto("done".encode(), addr)

            except:
                pass


se = Server()
se.connect()
