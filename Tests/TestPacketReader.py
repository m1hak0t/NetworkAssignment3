import unittest


class TestPacketReader(unittest.TestCase):
    def setUp(self):
        self.recv_buffer = ""

    def get_next_packet(self):

        if "\n" in self.recv_buffer:
            packet_str, self.recv_buffer = self.recv_buffer.split("\n", 1)
            return packet_str
        return None

    def test_concatenated_packets(self):


        received_data = "ACK|0|20\nACK|1|20\n"
        self.recv_buffer += received_data

        p1 = self.get_next_packet()
        self.assertEqual(p1, "ACK|0|20")


        p2 = self.get_next_packet()
        self.assertEqual(p2, "ACK|1|20")


        self.assertIsNone(self.get_next_packet())

    def test_fragmented_packet(self):
        """Тест: Пакет пришел по частям (Фрагментация)"""

        self.recv_buffer += "DATA|5|hel"
        self.assertIsNone(self.get_next_packet(), "Нельзя извлекать пакет без \\n")


        self.recv_buffer += "lo\n"
        p = self.get_next_packet()
        self.assertEqual(p, "DATA|5|hello")

    def test_mixed_flow(self):
        """Тест: Смешанный поток (полный пакет + кусок следующего)"""
        self.recv_buffer += "ACK|3|40\nDATA|4|partia"


        p1 = self.get_next_packet()
        self.assertEqual(p1, "ACK|3|40")


        self.assertIsNone(self.get_next_packet())
        self.assertEqual(self.recv_buffer, "DATA|4|partia")


if __name__ == "__main__":
    unittest.main()