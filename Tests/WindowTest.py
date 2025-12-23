import unittest
from unittest.mock import Mock, MagicMock, patch, call
import socket

from ClientWindowEngine import ClientWindowEngine
from Protocol import Protocol


class MockDataSegmentator:
    """Mock implementation of DataSegmentator for testing"""

    def __init__(self, filename):
        self.data = [b"chunk1", b"chunk2", b"chunk3", b"chunk4", b"chunk5"]
        self.current_index = 0

    def next(self, size):
        if self.current_index < len(self.data):
            result = self.data[self.current_index]
            self.current_index += 1
            return result
        return None

    def get(self, index):
        if 0 <= index < len(self.data):
            return self.data[index]
        return None

    def isfinished(self):
        return self.current_index >= len(self.data)

    def get_seq_number(self):
        return self.current_index


class TestClientWindowEngine(unittest.TestCase):
    #1
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.mock_socket = Mock(spec=socket.socket)
        self.test_config = {
            "message": "test_message",
            "window_size": 3,
            "wait_timeout": 2
        }

        # Patch ConfigLoader to return our test config
        self.config_patcher = patch('ClientWindowEngine.ConfigLoader.load_config')
        self.mock_config_loader = self.config_patcher.start()
        self.mock_config_loader.return_value = self.test_config

        # Create engine with mock segmentator
        self.engine = ClientWindowEngine(
            self.mock_socket,
            MockDataSegmentator,
            "test_config.json"
        )

    # 2
    def tearDown(self):
        """Clean up after each test"""
        self.config_patcher.stop()

    # 3
    def test_initialization(self):
        """Test that ClientWindowEngine initializes correctly"""
        self.assertEqual(self.engine.window_size, 3)
        self.assertEqual(self.engine.wait_timeout, 2.0)
        self.assertEqual(self.engine.windowbase, 0)
        self.assertEqual(self.engine.segmentsize, 20)
        self.assertEqual(self.engine.acked, [])
        self.assertEqual(self.engine.recv_buffer, "")
        self.mock_socket.settimeout.assert_called_once_with(2.0)

    # 4
    def test_send_packet(self):
        """Test sending a packet"""
        test_packet = "test_packet_data"
        self.engine.send_packet(test_packet)
        self.mock_socket.sendall.assert_called_once_with(test_packet)

    # 5
    def test_get_segment(self):
        """Test receiving a segment"""
        expected_data = b"test_data"
        self.mock_socket.recv.return_value = expected_data
        result = self.engine.get_segment()
        self.assertEqual(result, expected_data)
        self.mock_socket.recv.assert_called_once_with(1024)

    # 6
    def test_ack_segment(self):
        """Test acknowledging a segment"""
        test_segment = "segment_1"
        self.engine.ack_segment(test_segment)
        self.assertIn(test_segment, self.engine.acked)

        self.engine.ack_segment("segment_2")
        self.assertEqual(len(self.engine.acked), 2)

    # 7
    def test_move_window(self):
        """Test moving the window base"""
        self.engine.move_window(5)
        self.assertEqual(self.engine.windowbase, 6)

        self.engine.move_window(10)
        self.assertEqual(self.engine.windowbase, 11)

    # 8
    def test_set_segmentsize(self):
        """Test setting segment size"""
        self.engine.set_segmentsize(50)
        self.assertEqual(self.engine.segmentsize, 50)

    # 9
    def test_get_next_packet_with_complete_packet(self):
        """Test getting next packet when buffer contains complete packet"""
        self.engine.recv_buffer = "packet1\npacket2\npacket3"
        result = self.engine.get_next_packet()
        self.assertEqual(result, "packet1")
        self.assertEqual(self.engine.recv_buffer, "packet2\npacket3")

    # 10
    def test_get_next_packet_without_complete_packet(self):
        """Test getting next packet when buffer has incomplete packet"""
        self.engine.recv_buffer = "incomplete_packet"
        result = self.engine.get_next_packet()
        self.assertIsNone(result)
        self.assertEqual(self.engine.recv_buffer, "incomplete_packet")

    # 11
    def test_get_next_packet_empty_buffer(self):
        """Test getting next packet from empty buffer"""
        self.engine.recv_buffer = ""
        result = self.engine.get_next_packet()
        self.assertIsNone(result)

    # 11
    def test_receive_and_buffer_success(self):
        """Test receiving data and adding to buffer"""
        self.mock_socket.recv.return_value = b"new_data"
        self.engine.recv_buffer = "existing_"
        self.engine.receive_and_buffer()
        self.assertEqual(self.engine.recv_buffer, "existing_new_data")
    #12
    def test_receive_and_buffer_timeout(self):
        """Test that socket timeout is propagated"""
        self.mock_socket.recv.side_effect = socket.timeout()
        with self.assertRaises(socket.timeout):
            self.engine.receive_and_buffer()

    def test_receive_and_buffer_empty_data(self):
        """Test receiving empty data"""
        self.mock_socket.recv.return_value = b""
        initial_buffer = self.engine.recv_buffer
        self.engine.receive_and_buffer()
        self.assertEqual(self.engine.recv_buffer, initial_buffer)

    @patch.object(Protocol, 'make_packet')
    def test_send_unacked(self, mock_make_packet):
        """Test sending unacknowledged packets"""
        mock_make_packet.return_value = "mock_packet"

        self.engine.windowbase = 1
        self.engine.send_unacked(3)

        # Should send packets for sequence numbers 1, 2, 3
        self.assertEqual(mock_make_packet.call_count, 3)
        self.assertEqual(self.mock_socket.sendall.call_count, 3)

    @patch.object(Protocol, 'make_packet')
    @patch.object(Protocol, 'get_packet_from_str')
    def test_run_successful_transmission(self, mock_get_packet, mock_make_packet):
        """Test successful file transmission with ACKs"""
        mock_make_packet.return_value = "mock_packet"

        # Create a list to track all ACKs
        all_acks = [
            (Protocol.MSG_ACK, 0, ""),
            (Protocol.MSG_ACK, 1, ""),
            (Protocol.MSG_ACK, 2, ""),
            (Protocol.MSG_ACK, 3, ""),
            (Protocol.MSG_ACK, 4, ""),  # Final ACK - windowbase becomes 5
        ]
        ack_index = [0]

        def get_packet_side_effect(packet_str):
            if ack_index[0] < len(all_acks):
                result = all_acks[ack_index[0]]
                ack_index[0] += 1
                return result
            # After all ACKs processed, return the last one
            return all_acks[-1]

        mock_get_packet.side_effect = get_packet_side_effect

        # Control recv behavior precisely
        recv_call_count = [0]
        max_recv_calls = 20  # Safety limit to detect infinite loop

        def recv_side_effect(size):
            recv_call_count[0] += 1
            print(f"recv call #{recv_call_count[0]}")

            if recv_call_count[0] > max_recv_calls:
                raise RuntimeError(f"recv called {max_recv_calls} times - infinite loop detected!")

            # For first 5 calls, return data with newlines
            if recv_call_count[0] <= 5:
                return b"ACK_DATA\n"

            # After that, timeout to eventually trigger max retries
            print(f"Timing out on call #{recv_call_count[0]}")
            raise socket.timeout()

        self.mock_socket.recv.side_effect = recv_side_effect

        try:
            self.engine.run()
        except RuntimeError as e:
            self.fail(f"run() entered infinite loop: {e}")

        # Verify packets were sent
        self.assertTrue(mock_make_packet.called)
        print(f"Total packets sent: {mock_make_packet.call_count}")
        print(f"Final windowbase: {self.engine.windowbase}")
        print(f"Final next_seq: {self.engine.next_seq}")
        print(f"Total recv calls: {recv_call_count[0]}")

    @patch.object(Protocol, 'make_packet')
    @patch.object(Protocol, 'get_packet_from_str')
    def test_run_with_segment_size_change(self, mock_get_packet, mock_make_packet):
        """Test that segment size changes when payload contains digit"""
        mock_make_packet.return_value = "mock_packet"

        # Counter for tracking packet parsing
        ack_counter = [0]

        def get_packet_side_effect(packet_str):
            seq = ack_counter[0]
            ack_counter[0] += 1
            if seq == 0:
                # First ACK changes segment size to 30
                return (Protocol.MSG_ACK, 0, "30")
            elif seq < 5:
                return (Protocol.MSG_ACK, seq, "")
            return (Protocol.MSG_ACK, 4, "")

        mock_get_packet.side_effect = get_packet_side_effect

        recv_counter = [0]

        def recv_side_effect(size):
            recv_counter[0] += 1
            if recv_counter[0] <= 5:
                return b"ACK\n"
            raise socket.timeout()

        self.mock_socket.recv.side_effect = recv_side_effect

        initial_size = self.engine.segmentsize
        self.engine.run()

        # Verify segment size was changed
        self.assertEqual(self.engine.segmentsize, 30)
        self.assertNotEqual(self.engine.segmentsize, initial_size)

    @patch.object(Protocol, 'make_packet')
    def test_run_with_timeout_retransmission(self, mock_make_packet):
        """Test retransmission on timeout"""
        mock_make_packet.return_value = "mock_packet"

        # First recv times out, then succeeds
        self.mock_socket.recv.side_effect = [
            socket.timeout(),
            b"ACK\n",
            b"ACK\n",
            b"ACK\n",
            b"ACK\n",
            b"ACK\n",
            b""
        ]

        with patch.object(Protocol, 'get_packet_from_str') as mock_get:
            mock_get.side_effect = [
                (Protocol.MSG_ACK, 0, ""),
                (Protocol.MSG_ACK, 1, ""),
                (Protocol.MSG_ACK, 2, ""),
                (Protocol.MSG_ACK, 3, ""),
                (Protocol.MSG_ACK, 4, ""),
            ]

            self.engine.run()

            # Verify packets were sent (including retransmissions)
            self.assertTrue(self.mock_socket.sendall.called)

    def test_window_base_advancement(self):
        """Test that window base advances correctly"""
        initial_base = self.engine.windowbase
        self.engine.move_window(2)
        self.assertEqual(self.engine.windowbase, initial_base + 3)

    @patch.object(Protocol, 'make_packet')
    def test_send_unacked_respects_window_base(self, mock_make_packet):
        """Test that send_unacked only sends from windowbase"""
        mock_make_packet.return_value = "mock_packet"

        self.engine.windowbase = 5
        self.engine.send_unacked(7)

        # Should send for sequence numbers 5, 6, 7 (3 packets)
        self.assertEqual(mock_make_packet.call_count, 3)

        # Verify correct sequence numbers
        calls = mock_make_packet.call_args_list
        seq_nums = [call[0][1] for call in calls]
        self.assertEqual(seq_nums, [5, 6, 7])


if __name__ == '__main__':
    unittest.main()