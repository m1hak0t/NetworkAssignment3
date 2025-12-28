import random
import socket

from Protocol import Protocol


class ServerWindowEngine():
    def __init__(self, server_socket, filepath: str, sabotage_mode=False, sabotage_probability=0.3, drop = -1, timeout  = 1):
        self.filepath = filepath
        self.server_socket = server_socket
        self.recv_buffer = ""
        self.expected_seq = 0
        self.current_seq = 0
        self.result = b""
        self.lostnfound = []
        self.seq_num = 0
        # Simple cumulative ACK buffer: stores out-of-order packets
        self.packet_buffer = {}  # {seq_num: payload}

        # Sabotage mode settings
        self.sabotage_mode = sabotage_mode
        self.sabotage_probability = float(sabotage_probability)
        self.dropped_acks = 0

        #When to start dropping packages
        self.drop = drop
        # new -timer
        self.server_socket.settimeout(1)  # 10 שניות timeout

    def update(self, drop , sabotage):
        self.drop = drop
        self.sabotage_mode = sabotage

    def receive_and_buffer(self):
        try:
            data = self.server_socket.recv(1024)
            if data:
                self.recv_buffer += data.decode("utf-8")
            else:
                # אם recv מחזיר ריק - החיבור נסגר
                raise ConnectionError("Client closed connection")
        except TimeoutError:
            raise

    def get_next_packet(self):
        if "\n" in self.recv_buffer:
            packet_str, self.recv_buffer = self.recv_buffer.split("\n", 1)
            return packet_str
        return None

    def send_ack(self, seq_num, dynamic_size):
        # Sabotage mode: randomly drop ACKs
        if self.sabotage_mode and random.random() < self.sabotage_probability:
            self.dropped_acks += 1
            print(f"[SABOTAGE] Dropping ACK for seq {seq_num} (Total dropped: {self.dropped_acks})")
            return  # Don't send the ACK
        # Drop all the packages after some specific number
        if seq_num > self.drop and self.sabotage_mode and self.drop > -1:
            print(f"Sabotaging the package: {seq_num}")
            return

        packet = Protocol.make_packet(Protocol.MSG_ACK, seq_num, str(dynamic_size))
        self.server_socket.sendall(packet)

    def get_random_size(self):
        return random.randint(1, 6)

    def process_buffered_packets(self):
        """Process any consecutively buffered packets starting from expected_seq"""
        while self.expected_seq in self.packet_buffer:
            # Get the buffered payload
            payload = self.packet_buffer.pop(self.expected_seq)
            # Add to result
            self.result += payload.encode("utf-8")
            # Move to next expected sequence
            self.expected_seq += 1

    def run(self):

        # new - timer
        consecutive_timeout = 0
        max_timeouts = 3

        while True:
            try:
                self.receive_and_buffer()
                consecutive_timeouts = 0

                #Keep pulling packets only as long as they are complete (\n found)
                while True:
                    raw_data = self.get_next_packet()
                    if raw_data is None:
                        break  # No more complete packets in buffer, go back to recv()

                    # Unpack the data safely
                    msg_type, seq_num, payload = Protocol.get_packet_from_str(raw_data)

                    if msg_type == Protocol.MSG_FIN:
                        print("The following string received from the client: " + self.result.decode("utf-8"))
                        if self.sabotage_mode:
                            print(f"[SABOTAGE STATS] Total ACKs dropped: {self.dropped_acks}")
                        return  # Use 'return' to exit the entire engine



                    if msg_type == Protocol.MSG_DATA:
                        if seq_num == self.expected_seq:
                            self.result += payload.encode("utf-8")
                            self.expected_seq += 1
                            self.process_buffered_packets()
                            # Send ACK for the last successfully received in-order packet
                            self.send_ack(self.expected_seq - 1, self.get_random_size())
                            print(f"Sending the ACK with sequence number : {self.expected_seq}")
                        if seq_num > self.expected_seq:
                            self.packet_buffer[seq_num] = payload
                            # Send cumulative ACK for last in-order packet received
                            self.send_ack(self.expected_seq - 1, self.get_random_size())

            except socket.timeout:
                consecutive_timeouts += 1
                print(f"[Server] Timeout {consecutive_timeouts}/{max_timeouts}")

                if consecutive_timeouts >= max_timeouts:
                    print("[Server] Max timeouts reached. Closing connection.")
                    print("The following string received from the client: " + self.result.decode("utf-8"))
                    return

            except Exception as e:
                print(f"Engine Error: {e}")
                break