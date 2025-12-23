from socket import socket


class ServerWindowEngine():
    def __init__(self, server_socket : socket.socket, filepath : str):
            self.server_socket = server_socket
            self.filepath = filepath
            self.server_socket = server_socket
            self.recv_buffer = ""
            self.expected_seq = 0
            self.current_seq = 0
            self.result = b""
            self.lostnfound = []


    def receive_and_buffer(self):
        try:
            data = self.server_socket.recv(1024)
            if data:
                self.recv_buffer += data.decode("utf-8")
        except socket.timeout:
            raise

    def get_next_packet(self):
        if "\n" in self.recv_buffer:
            packet_str, self.recv_buffer = self.recv_buffer.split("\n", 1)
            return packet_str
        return None

    def send_packet(self, payload):
        pass

    def run(self):
        pass
        #while
        #Check if there is a package to recieve
        #If the package sequence number >= 1