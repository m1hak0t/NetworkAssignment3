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

        # 1. Create a UDP socket - just allow connection but without all things that we need to build
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.settimeout(2)

        try:

            # This is where the "Handshake" happens
            # create the packet and send syn - for start "handshake"
            syn_packet = Protocol.make_packet(Protocol.MSG_SYN, 0, "filename.text")

            print("Sending SYN packet...")

           #need to know every time to where send (sendto - not sendall like in tcp socket)
            self.client_socket.sendto(syn_packet, (self.server_ip, self.server_port))

            try:
                server_data, addr = self.client_socket.recvfrom(1024)

                msg_type, seq_num, payload = Protocol.get_packet(server_data) # could in python
                if msg_type == Protocol.MSG_SYN_ACK:
                    print("Received SYN-ACK from server")

                    ack_packet = Protocol.make_packet(Protocol.MSG_ACK, 1, "")
                    self.client_socket.sendto(ack_packet,(self.server_ip, self.server_port))
                    print("Sending ACK - Finished handshake")
                    return True
                else:
                    print(f"Error: Expected SYN-ACK, but got {msg_type}")
                    return False

            except socket.timeout:
                print("Timeout! Server did not respond to SYN (Packet lost or Server down).")
                return False
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def close(self):
        # Always close the socket at the end
        if self.client_socket:
            self.client_socket.close()
            print("Connection closed.")

# --- Main Execution ---
if __name__ == "__main__":
    # 127.0.0.1 refers to "This Computer" (Localhost)
    client = ReliableClient('127.0.0.1', 13588)
    if client.connect():
        print("Ready to send file...")
        # client.send_file(...)

    client.close()