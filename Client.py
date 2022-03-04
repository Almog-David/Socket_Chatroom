import socket
import sys
import threading
import pickle

SERVER_IP = '127.0.0.1'
SERVER_PORT = 50008  # TCP PORT
SERVER_UDP_PORT = 55001  # UDP PORT
UDP_CONNECTION = (SERVER_IP, SERVER_UDP_PORT)  # the information we need in order to send a message in UDP


class Client:
    def __init__(self):
        self.name = ""  # the name which be use in order to connect to the server and to send messages
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a new TCP socket for the client
        self.receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # create a new UDP socket for the client
        self.func = []

    def connect(self, name):  # the function that make the connection to the server
        self.name = name
        self.client.connect((SERVER_IP, SERVER_PORT))  # connecting to the TCP socket of the server
        self.start()

    def start(self):  # a function that start the thread of receiving messages
        receive_thread = threading.Thread(target=self.receive, args=())
        # we want to be able to receive messages in any time
        receive_thread.start()
        receive_thread.join()

    """" receive function is a function that choose the right response to the server's messages by giving a
    number of scenarios"""

    def receive(self):
        while True:  # always be able to receive messages from the server
            try:
                message = self.client.recv(1024).decode()  # we receive the message from the server's TCP socket
                if message == "name":  # if we get "name" - we will send the server our name
                    self.client.send(self.name.encode())
                elif message == "disconnected":  # if we get "disconnected" - we disconnect the client from the server
                    self.client.close()
                    sys.exit()
                elif "ready for download:" in message:
                    # this message tell us to switch to the UDP socket in order to download the file we want
                    file = message.split(':')[1]
                    self.receiver.sendto('connected'.encode(), UDP_CONNECTION)
                    # starting a 3way handshake with the server
                    threading.Thread(target=self.udp_connection, args=(file,)).start()
                    # we create a new thread in order to keep listening for new messages from the server's UDP socket
                    # self.udp_connection(file)
                else:
                    for i in self.func:  # a for loop to help us in the GUI - not really important
                        i(message)
            except:  # if we get an error - we didn't get any message -> we disconnect the client
                print("error")
                self.client.close()
                break

    """" write function is a function that write the messages to the server"""

    def write(self, message):
        self.client.send(message.encode())

    """ udp_connection function is the function we use in order to get the packets of the file we want to download"""

    def udp_connection(self, file_name):
        raw_data = {}
        while True:
            try:
                response = self.receiver.recvfrom(2048)
                try:
                    msg = response[0].decode()
                except:
                    msg = response[0]
                if msg == "connected":
                    # if we got "connected" (the second handshake) we send "start" (the third handshake)
                    self.receiver.sendto("start".encode(), UDP_CONNECTION)

                elif msg == "done":  # if the server tell us that he has no more data to send
                    self.receiver.sendto("got all the data".encode(), UDP_CONNECTION)
                    self.create_file(raw_data, file_name)  # now we will create the file
                else:
                    data = pickle.loads(msg)
                    # data has 2 parameters in it: data[0] has the ack number of the packet and data[1]
                    # has the packet's information/content
                    ack = data[0]
                    info = data[1]
                    if ack not in raw_data:
                        # if we didn't get this packet before - we will add it to the raw data dictionary
                        raw_data[ack] = info
                    print(f'packet {ack} has received')  # we print the packet number we received
                    self.receiver.sendto(ack.to_bytes(4, "big"), response[1])  # we send to the server's UDP socket the
                    # packet number/sequence in order to tell him not to send it again
            except:
                break

    """ after we got all the packets of the file we downloaded, we start building/creating him by sorting the keys 
    (the packet's sequence) of the data dictionary and writing the data to the new file"""

    def create_file(self, file_segments, file_name):
        print('creating file')
        path = './Downloads/' + file_name
        file = open(path, 'w')
        for key in sorted(file_segments.keys()):
            print(f'adding packet number {key} to the file')
            file.write(file_segments[key])
        file.close()
        print("file has successfully download!")
        sys.exit()

