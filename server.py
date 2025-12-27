import socket

from Protocol import Protocol
from ConfigLoader import ConfigLoader
from ServerWindowEngine import ServerWindowEngine


class ReliableServer:

    # "constructor" - in python
    def __init__(self, port, config_file_path):
        # Constructor: Initialize the server with a specific port
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.client_addr = None

        # Reading from file
        self.config_file_path = config_file_path
        self.full_config = ConfigLoader.load_config(self.config_file_path, True)
        self.maximum_msg_size = self.full_config["maximum_msg_size"]
        self.dynamic_message_size = self.full_config["dynamic message size"]
        self.sabotage_mode = self.full_config["sabotage_mode"]
        self.sabotage_probability = self.full_config["sabotage_probability"]
        self.drop_point = 10

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

        if self.sabotage_mode:
            print(f"[SABOTAGE MODE ENABLED] ACK drop probability: {self.sabotage_probability}")
            answer = input("Do you want to drop all the packages after the 10's package or drop them randomly? 1/2?")
            if answer == "1" :
                self.sabotage_mode = True
                self.sabotage_probability = 0
            elif answer == "2" :
                pass
            else:
                print("Error, sabotage mode deactivated")
                self.sabotage_mode = False


        while True:
            print("Waiting for a new client to connect...")

            # Accept a connection
            # The program will pause (block) here until a client connects

            try:
                self.client_socket, self.client_addr = self.server_socket.accept()
                print(f"New connected from: {self.client_addr}")
                # The "handshake"
                if self.get_connection():
                    # True - start to get request
                    self.handle_client_requests()
                else:
                    print("Handshake failed. Disconnecting client.")
                    self.client_socket.close()

            except Exception as e:
                print(f"Server Error: {e}")
                if self.client_socket:
                    self.client_socket.close()

    # "handshake" part
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

    # Get req of "max_size" - return resp by the file
    def handle_client_requests(self):
        try:
            data = self.client_socket.recv(1024)

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

            window = ServerWindowEngine(self.client_socket, self.config_file_path,
                                        self.sabotage_mode, self.sabotage_probability, self.drop_point)
            window.run()

        except Exception as e:
            print(f"Error: {e}")

    # if self.client_socket: self.client_socket.close()

    # --- Main Execution ---


if __name__ == "__main__":
    server = ReliableServer(12345, "server_config.txt")  # Create a server instance on port 8888
    server.run()