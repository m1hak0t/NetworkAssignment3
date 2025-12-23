import socket

from Protocol import Protocol
from ConfigLoader import ConfigLoader

class ReliableServer:

    #"constructor" - in python
    def __init__(self, port, config_file_path):
        # Constructor: Initialize the server with a specific port
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.client_addr = None

        # Reading from file
        self.full_config = ConfigLoader.load_config(config_file_path)
        self.maximum_msg_size = self.full_config["maximum_msg_size"]
        self.dynamic_message_size = self.full_config["dynamic message size"]
        self.window_size = self.full_config["window_size"]




    def run(self):
        # 1. Create a TCP/IP socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow reuse
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind the socket to the address and port
        self.server_socket.bind(('0.0.0.0', self.port))
        # Listen for incoming connections
        self.server_socket.listen(1)
        print(f"Server listening on port {self.port}...")


        while True:
            print("Waiting for a new client to connect...")

            # Accept a connection
            # The program will pause (block) here until a client connects

            try:
                self.client_socket, self.client_addr = self.server_socket.accept()
                print(f"New connected from: {self.client_addr}")
                # The "handshake"
                if self.get_connection():
                    # if True - start to get request
                    self.handle_client_requests()
                else:
                    print("Handshake failed. Disconnecting client.")
                    self.client_socket.close()

            except Exception as e:
                print(f"Server Error: {e}")
                if self.client_socket:
                    self.client_socket.close()

    #"handshake" part
    def get_connection(self):

        try:
            data = self.client_socket.recv(1024)
            msg_type, seq_num, payload = Protocol.get_packet(data)

            if msg_type != Protocol.MSG_SYN:
                print(f"Handshake Error: Expected SIN but got {msg_type}")
                return False

            print("Received SIN. Sending SIN-ACK...")

            # SYN-ACK
            syn_ack_packet = Protocol.make_packet(Protocol.MSG_SYN_ACK, 0, "")
            self.client_socket.sendall(syn_ack_packet)

            # Get ACK
            final_data = self.client_socket.recv(1024)
            msg_type, seq_num, payload = Protocol.get_packet(final_data)

            if msg_type == Protocol.MSG_ACK:
                print("Received ACK. Handshake Established!")
                return True
            else:
                print(f"Handshake Error: Expected ACK but got {msg_type}")
                return False

        except Exception as e:
            print(f"Handshake Exception: {e}")

            return False
    #Get req of "max_size" - return resp by the file
    def handle_client_requests(self):
        while True:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break

                msg_type, seq_num, payload = Protocol.get_packet(data)
                if msg_type == Protocol.MSG_REQ_SIZE:

                    if self.dynamic_message_size:
                        # The flag for "dynamic situation"
                        print("[Server] Sending dynamic flag.")
                        response_payload = "dynamic message size = true"

                    else:
                        # if it is "Static situation"
                        print(f"[Server] Sending static size: {self.maximum_msg_size}")
                        response_payload = str(self.maximum_msg_size)

                    # Sending the answer
                    response = Protocol.make_packet(Protocol.MSG_SIZE_RESP, 0, response_payload)
                    self.client_socket.sendall(response)

                #If not require data, and i want to do something....

            except Exception as e:
                print(f"Error: {e}")
                break

        #if self.client_socket: self.client_socket.close()



    # --- Main Execution ---
if __name__ == "__main__":
    server = ReliableServer(12345,"server_config.txt" )  # Create a server instance on port 8888
    server.run()