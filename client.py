import socket
from ClientWindowEngine import ClientWindowEngine
from DataSegmentator import DataSegmentator
from Protocol import Protocol
from ConfigLoader import ConfigLoader




class ReliableClient:
    def __init__(self, server_ip, server_port , config_file):
        # Constructor: Save the server's address details
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = None

        self.config = ConfigLoader.load_config(config_file, False)
        self.file_path = "client_config.txt"
        self.mesage = self.config["message"]
        self.window_size = self.config["window_size"]
        self.timeout = self.config["timeout"]

        # for now - until the answer from server
        self.maximum_msg_size = 5
        self.dynamic_message_size = None

    def connect(self):
        print(f"Trying to connect to server at {self.server_ip}:{self.server_port}...")

        # Create a TCP/IP socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Connect to the server
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
                return True
            else:
                print("Error: Handshake failed")
                return False


        except Exception as e:
            print(f" Connection failed: {e}")
            return False

    # The question about size - for server
    def get_max_message_size(self):
        print("Requesting max message size from server...")
        try:
            # Creat the "max_size" request
            req_packet = Protocol.make_packet(Protocol.MSG_REQ_SIZE, 0, "")

            #Sending in socket (from "handshake")
            self.client_socket.sendall(req_packet)

            # The answer
            response = self.client_socket.recv(1024)
            msg_type, seq_num, payload = Protocol.get_packet(response)

            # Chack and update (dynamic/num)
            if msg_type == Protocol.MSG_SIZE_RESP:
                print(f"Received message size response : {payload}")
                #!!!!!!!!!!!!!!

                if payload.isdigit() :
                    self.maximum_msg_size = int(payload)
                    return True

                if "dynamic" in payload:
                    self.dynamic_message_size = True
                    print("The message size is set to  dynamic")
                    print(f"[Client] Max size set to: {self.maximum_msg_size}")
                    return True
                else :
                    self.dynamic_message_size = False
                    return False

        except Exception as e:
            print(f"Error during size negotiation: {e}")
            return False

    #not for now
    def close(self):
        # Always close the socket at the end
        if self.client_socket:
            self.client_socket.close()
            print("Connection closed.")


    def run(self):
        #Handshake
        if self.connect():
            print("Ready to send file...")
            # 2. The "max_size" request
            if self.get_max_message_size():
                print("Ready to send")
        #The sliding window functionality
        segmentator_client = DataSegmentator(self.file_path, self.config)
        window = ClientWindowEngine(self.client_socket, segmentator_client, self.file_path, self.dynamic_message_size,self.config, self.maximum_msg_size)
        window.run()
        answer = input("Press Enter to continue... y/n")
        if "y" in answer.lower():
            self.config = ConfigLoader.load_config(self.file_path, False)
            self.run()
        else:
            self.close()




# --- Main Execution ---
if __name__ == "__main__":
    # Creat "client"
    client = ReliableClient('127.0.0.1', 12345, "client_config.txt")

    client.run()

