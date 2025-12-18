import socket
from Protocol import Protocol
import time


class ReliableClient:
    def __init__(self, server_ip, server_port):
        # Constructor: Save the server's address details
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = None

    def connect(self):
        print(f"Trying to connect to server at {self.server_ip}:{self.server_port}...")

        # 1. Create a TCP/IP socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # 2. Connect to the server
            # This is where the "Handshake" happens
            self.client_socket.connect((self.server_ip, self.server_port))
            print("Successfully connected to the server!")

            # create the packet
            syn_packet = Protocol.make_packet(Protocol.MSG_SYN, 0, "")

            print("Sending SYN packet...")

           #send in socket
            self.client_socket.sendall(syn_packet)

            server_data = self.client_socket.recv(1024)
            msg_type, seq_num, payload = Protocol.get_packet(server_data) # could in python
            if msg_type == Protocol.MSG_SYN_ACK:
                print("Received SYN ACK")
                next_packet = Protocol.make_packet(Protocol.MSG_ACK, 1, "")
                self.client_socket.sendall(next_packet)
                print("Sending ACK")
                print ("Finished handshake")

        except Exception as e:
            print(f" Connection failed: {e}")

        finally:
            # Always close the socket at the end
            if self.client_socket:
                self.client_socket.close()
                print("Connection closed.")


# --- Main Execution ---
if __name__ == "__main__":
    # 127.0.0.1 refers to "This Computer" (Localhost)
    client = ReliableClient('127.0.0.1', 13588)
    client.connect()