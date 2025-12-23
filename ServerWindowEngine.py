import random
from socket import socket

from Protocol import Protocol


class ServerWindowEngine():
    def __init__(self, server_socket, filepath : str):
            self.filepath = filepath
            self.server_socket = server_socket
            self.recv_buffer = ""
            self.expected_seq = 0
            self.current_seq = 0
            self.result = b""
            self.lostnfound = []
            self.seq_num = 0


    def receive_and_buffer(self):
        try:
            data = self.server_socket.recv(1024)
            if data:
                self.recv_buffer += data.decode("utf-8")
        except TimeoutError:
            raise

    def get_next_packet(self):
        if "\n" in self.recv_buffer:
            packet_str, self.recv_buffer = self.recv_buffer.split("\n", 1)
            return packet_str
        return None

    def send_ack(self, seq_num ,dynamic_size):
        packet = Protocol.make_packet(Protocol.MSG_ACK, seq_num, str(dynamic_size) )
        self.server_socket.sendall(packet)

    def get_random_size(self):
         return random.randint(0,6)

    def run(self):

        while True:
            try :
            #Check if there is a package to recieve
                self.receive_and_buffer()
                #If there is a package
                while self.recv_buffer:
                    raw_data = self.get_next_packet()
                    # unpack the data
                    msg_type, seq_num, payload = Protocol.get_packet_from_str(raw_data)
                    # Check if the server has ended the connection
                    if msg_type == Protocol.MSG_FIN :
                        print("The following string recieved from the client: " + self.result.decode("utf-8"))
                        break
                    # Check if sequence is valid
                    if msg_type == Protocol.MSG_DATA and seq_num == self.expected_seq:
                        #if yes - > increace expeted by 1 and send ack
                        self.expected_seq += 1
                        #Add the payload to the result
                        self.result += payload.encode("utf-8")
                        # Send an ack with the expected seq number
                        self.send_ack(self.expected_seq, self.get_random_size())
                    #if no - > leave expected as is
            except BaseException as e:
                print(e)


