import socket

from Protocol import Protocol
class ReliableServer:
    class ReliableServer:

        #"constructor" - in python
        def __init__(self, port):
            # Constructor: Initialize the server with a specific port
            self.port = port
            self.server_socket = None
            self.client_socket = None
            self.client_addr = None

        def run(self):
            # 1. Create a TCP/IP socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # (Optional) Allow the server to reuse the address immediately after closing

            # This prevents the "Address already in use" error during testing
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # 2. Bind the socket to the address and port
            self.server_socket.bind(('0.0.0.0', self.port))

            # 3. Listen for incoming connections
            self.server_socket.listen(1)
            print(f"Server listening on port {self.port}...")

            # 4. Accept a connection
            # The program will pause (block) here until a client connects
            self.client_socket, self.client_addr = self.server_socket.accept()
            print(f"Client connected from: {self.client_addr}")

            try:
                data = self.client_socket.recv(1024)
                msg_type, seq_num, payload = Protocol.get_packet(data)
                if msg_type == Protocol.MSG_SYN:
                    print("Received SYN. Sending SYN-ACK...")

                    # create answer "syn/ack"
                    syn_ack_packet = Protocol.make_packet(Protocol.MSG_SYN_ACK, 0, "")
                    self.client_socket.sendall(syn_ack_packet)
                    print("Sent SYN-ACK successfully, Waiting for ACK..")

                    final_data = self.client_socket.recv(1024)
                    msg_type, seq_num, payload = Protocol.get_packet(final_data)
                    if msg_type == Protocol.MSG_ACK:
                        print("Received ACK. Connection Established ")
                    else:
                        print("Error: Expected ACK, but got {msg_type}")

                else:
                    print("Error: Expected SYN packet.")


            except Exception as e:
                print(f"Error: {e}")

           #close
            self.client_socket.close()
            self.server_socket.close()


    # --- Main Execution ---
    if __name__ == "__main__":
        server = ReliableServer(13588)  # Create a server instance on port 8888
        server.run()