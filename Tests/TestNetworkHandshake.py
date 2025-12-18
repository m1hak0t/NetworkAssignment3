import sys
import os

# --- הוספת התיקייה הראשית לנתיב החיפוש ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import unittest
import socket
import threading
import time

from Protocol import Protocol  # הייבוא שלך

HOST = '127.0.0.1'
PORT = 23456


class TestNetworkHandshake(unittest.TestCase):

    def setUp(self):
        self.server_socket = None
        self.client_socket = None

    def tearDown(self):
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()

    def run_temp_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((HOST, PORT))
            self.server_socket.listen(1)

            client_conn, addr = self.server_socket.accept()

            # --- תיקון 1: קבלת Bytes בלבד (בלי decode) ---
            raw_data = client_conn.recv(1024)

            # עכשיו get_packet יקבל Bytes ויעשה decode בעצמו
            parsed_msg = Protocol.get_packet(raw_data)

            # שליחת תשובה
            response_bytes = Protocol.make_packet("DATA", 1, "Pong")
            client_conn.send(response_bytes)

            client_conn.close()
        except Exception as e:
            print(f"Server Error: {e}")

    def test_handshake_flow(self):
        server_thread = threading.Thread(target=self.run_temp_server)
        server_thread.start()
        time.sleep(0.1)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((HOST, PORT))

        # שליחה
        msg_bytes = Protocol.make_packet("DATA", 0, "Ping")
        self.client_socket.send(msg_bytes)

        # --- תיקון 2: קבלת Bytes בלבד (בלי decode) ---
        raw_response = self.client_socket.recv(1024)

        # הפרוטוקול יטפל בהמרה
        parsed_response = Protocol.get_packet(raw_response)

        print(f"\n[TEST LOG] Raw bytes received length: {len(raw_response)}")

        # בדיקה שהתקבל משהו
        self.assertTrue(len(raw_response) > 0, "Server did not respond")

        server_thread.join()


if __name__ == '__main__':
    unittest.main()