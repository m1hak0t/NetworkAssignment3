import socket

from Protocol import Protocol

class ReliableServer:

    #"constructor" - in python
    def __init__(self, port):
        # Constructor: Initialize the server with a specific port
        self.port = port
        self.server_socket = None
        self.client_addr = None

    def run(self):
        # 1. Create a UDP socket - just allow connection but without all things that we need to build
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.server_socket.bind(('0.0.0.0', self.port))
        print(f"Server listening on UDP port {self.port}...")

        while True:
            try:
                data, addr = self.server_socket.recvfrom(1024)
                msg_type, seq_num, payload = Protocol.get_packet(data)

                if msg_type == Protocol.MSG_SYN:
                    print(f"[Handshake] Received SYN from {addr}")

                    #save the recent client
                    self.client_addr = addr
                    # create answer "syn/ack"
                    syn_ack_packet = Protocol.make_packet(Protocol.MSG_SYN_ACK, 0, "")
                    self.server_socket.sendto(syn_ack_packet,self.client_addr)
                    print("[Handshake] Sent SYN-ACK. Waiting for final ACK...")
                elif msg_type == Protocol.MSG_ACK and seq_num == 1:
                    if addr == self.client_addr:
                        print("[Handshake] Received Final ACK. Connection Established!")
                        print("Ready to receive file...")
                    else:
                        print(f"Ignored ACK from unknown source: {addr}")


                elif msg_type == "DATA":
                    pass

            except Exception as e:
                print(f"Error: {e}")

    # --- Main Execution ---
if __name__ == "__main__":
    server = ReliableServer(13588)  # Create a server instance on port 8888
    server.run()