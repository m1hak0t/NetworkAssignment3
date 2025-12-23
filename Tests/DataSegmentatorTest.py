import unittest
import os
from DataSegmentator import DataSegmentator


class TestDataSegmentator(unittest.TestCase):
    def setUp(self):
        # Создаем временный конфиг для теста
        self.config_file = "test_config.txt"
        self.test_message = "ABCDEFGHIJ"  # 10 символов
        with open(self.config_file, "w") as f:
            f.write(f'message: "{self.test_message}"\n')
            f.write("maximum_msg_size: 5\n")
            f.write("window_size: 2\n")
            f.write("timeout: 5\n")
            f.write("dynamic message size: False\n")

    def tearDown(self):
        # Удаляем временный файл после теста
        if os.path.exists(self.config_file):
            os.remove(self.config_file)

    def test_segmentation_flow(self):
        seg = DataSegmentator(self.config_file)

        # Тест 1: Первый сегмент
        # Если ты используешь +1 в коде, проверь, сколько реально байт придет
        s1 = seg.next(2)
        self.assertIsNotNone(s1)
        print(f"Segment 0: {s1}")

        # Тест 2: Проверка получения по индексу (для таймаутов)
        g1 = seg.get(0)
        self.assertEqual(s1, g1, "Метод get(0) должен вернуть тот же контент, что и первый next()")

        # Тест 3: Последовательность
        seq = seg.get_seq_number()
        self.assertEqual(seq, 1, "Счетчик сегментов должен увеличиться")

        # Тест 4: Второй сегмент
        s2 = seg.next(2)
        print(f"Segment 1: {s2}")
        self.assertNotEqual(s1, s2, "Следующий сегмент должен содержать новые данные")

    def test_end_of_data(self):
        seg = DataSegmentator(self.config_file)
        # Вычитываем всё большими кусками
        seg.next(5)
        seg.next(5)
        last = seg.next(5)
        # Проверяем, что за пределами данных не падает, а возвращает None или пустой байт
        self.assertTrue(last is None or len(last) == 0)


if __name__ == "__main__":
    unittest.main()