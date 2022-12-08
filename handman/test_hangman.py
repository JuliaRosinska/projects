import unittest
import hangman as hm

class TestHangman(unittest.TestCase):

    def test_construct_char_dict(self):
        self.assertEqual(hm.construct_char_dict("win"), {"w": [0], "i": [1], "n": [2]})

    def test_construct_char_dict_upper(self):
        self.assertEqual(hm.construct_char_dict("Win"), {"w": [0], "i": [1], "n": [2]})

    def test_construct_char_dict_space(self):
        self.assertEqual(hm.construct_char_dict("w in"), {"w": [0]," ": [1], "i": [2], "n": [3]})

    def test_construct_char_dict_numeric(self):
        with self.assertRaises(ValueError):
            hm.construct_char_dict("w1n")

    def test_construct_char_dict_empty(self):
        with self.assertRaises(ValueError):
            hm.construct_char_dict("")

if __name__ == "__main__":
    unittest.main()
