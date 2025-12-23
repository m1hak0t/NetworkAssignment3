import socket
import time
import os
import sys

# Assuming these exist based on your imports
import DataSegmentator
from ConfigLoader import ConfigLoader
from Protocol import Protocol


class ClientWindowEngine:
    def __init__(self, Clientobject: socket.socket, segmentator: DataSegmentator, filename: str):
        self.config = ConfigLoader.load_config(filename)
        self.Clientobject = Clientobject
        self.message = self.config["message"]
        self.window_size = self.config["window_size"]
        self.wait_timeout = self.config["timeout"]

        # Assuming segmentator is a class passed in
        self.segmentator = segmentator
        self.windowbase = 0
        self.segmentsize = 2
        self.acked = []
        self.recv_buffer = ""

        # State for visualization
        self.next_seq = 0

        Clientobject.settimeout(self.wait_timeout)

    # --- VISUALIZATION ENGINE ---

    def clear_screen(self):
        # Check if the operating system is Windows ('nt')
        if os.name == 'nt':
            os.system('cls')
        # Otherwise, assume it's Mac or Linux
        else:
            os.system('clear')

    def render_window(self, status_message="Processing..."):
        """
        Clears console and draws the current state of the sliding window.
        """
        # 1. Clear Screen (Cross-platform)
        os.system('cls' if os.name == 'nt' else 'clear')

        print(f"=== LIVE SLIDING WINDOW VISUALIZATION ===")
        print(f"Window Base: {self.windowbase:<5} | Next Seq: {self.next_seq:<5} | Window Size: {self.window_size}")
        print("-" * 60)

        # 2. visual construction
        # We visualize a range of packets around the current window
        buffer_view_size = self.window_size + 4
        start_index = max(0, self.windowbase - 2)
        end_index = start_index + buffer_view_size

        visual_line = ""

        for i in range(start_index, end_index):
            seq_str = f"{i:02d}"  # format number as 2 digits

            # LOGIC FOR COLORING
            if i < self.windowbase:
                # ACKED (Green Block)
                # \033[92m is Green, \033[0m is Reset
                visual_line += f"\033[92m[{seq_str}]\033[0m "

            elif i >= self.windowbase and i < (self.windowbase + self.window_size):
                # INSIDE WINDOW
                if i < self.next_seq:
                    # SENT BUT NOT ACKED (Yellow/Orange)
                    visual_line += f"\033[93m({seq_str})\033[0m "
                else:
                    # USABLE WINDOW SPACE (Empty/White)
                    visual_line += f" {seq_str}  "

            else:
                # OUTSIDE WINDOW (Grey/Dim)
                visual_line += f"\033[90m {seq_str} \033[0m "

        print(f"Stream: {visual_line}")
        print("-" * 60)
        print(f"Legend: \033[92m[ACKED]\033[0m  \033[93m(SENT/WAITING)\033[0m  OPEN  \033[90mFUTURE\033[0m")
        print(f"Event:  {status_message}")
        print("=" * 60)

        # 3. Animation Delay
        # Small sleep so the human eye can see the movement
        time.sleep(0.3)

        # --- MODIFIED LOGIC ---

    def send_packet(self, packet):
        self.Clientobject.sendall(packet)

    def get_segment(self):
        return self.Clientobject.recv(1024)

    def ack_segment(self, segment):
        self.acked.append(segment)

    def move_window(self, sequence_number):
        old_base = self.windowbase
        self.windowbase = sequence_number + 1
        # Trigger animation
        self.render_window(f"ACK Received! Window moved from {old_base} to {self.windowbase}")

    def send_unacked(self, sequence_number):
        self.render_window(f"\033[91mTIMEOUT! Retransmitting {self.windowbase} to {sequence_number}\033[0m")
        for i in range(self.windowbase, sequence_number + 1):
            # Note: You need a way to get specific packets again if relying on a generator.
            # Assuming segmentator.get(i) can retrieve past data
            payload = self.segmentator.get(i)
            # Check if payload exists to avoid errors
            if payload:
                payload_decoded = payload.decode("utf-8") if isinstance(payload, bytes) else str(payload)
                package = Protocol.make_packet(Protocol.MSG_DATA, i, payload_decoded)
                self.send_packet(package)
                time.sleep(0.1)  # slight visual delay for retransmits

    def set_segmentsize(self, val):
        self.segmentsize = val

    def get_next_packet(self):
        if "\n" in self.recv_buffer:
            packet_str, self.recv_buffer = self.recv_buffer.split("\n", 1)
            return packet_str
        return None

    def receive_and_buffer(self):
        try:
            data = self.Clientobject.recv(1024)
            if data:
                self.recv_buffer += data.decode("utf-8")
        except socket.timeout:
            raise

    def run(self):
        max_retries = 3
        retry_count = 0
        self.next_seq = 0

        # Initial Render
        self.render_window("Starting Transmission...")

        # fill the window until the file is sent
        while not self.segmentator.isfinished() or self.windowbase < self.next_seq:

            # SENDING LOOP
            while self.segmentator.get_seq_number() < self.windowbase + self.window_size:
                # Check bounds or stop if source finished
                if self.segmentator.isfinished():
                    break

                payload = self.segmentator.next(self.segmentsize)
                if payload:
                    packet = Protocol.make_packet(Protocol.MSG_DATA, self.next_seq, payload.decode("utf-8"))
                    self.send_packet(packet)

                    # VISUALIZATION UPDATE
                    current_seq = self.next_seq
                    self.next_seq += 1
                    self.render_window(f"Sent packet {current_seq}")

            # RECEIVING LOOP
            try:
                self.receive_and_buffer()
                retry_count = 0  # Reset retry on successful receive attempt (logic depends on if we actually get an ACK)

                while True:
                    packet_str = self.get_next_packet()
                    if not packet_str:
                        break

                    msg_type, seq_num, payload = Protocol.get_packet_from_str(packet_str)

                    if msg_type == Protocol.MSG_ACK:
                        if seq_num >= self.windowbase:
                            if payload and payload.isdigit():
                                self.set_segmentsize(int(payload))

                            # This moves the window and triggers the Green Animation
                            self.move_window(seq_num)

            except socket.timeout:
                retry_count += 1
                if retry_count >= max_retries:
                    print("Max retries exceeded")
                    break
                # RENDER TIMEOUT
                self.send_unacked(self.next_seq - 1)
