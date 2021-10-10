import unittest
from argparse import ArgumentTypeError

from src.utils.functions import valid_port  # pylint: disable=import-error


class TestValidPort(unittest.TestCase):
    def test_valid_port(self):
        self.assertEqual(valid_port("5555"), 5555)

    def test_invalid_port(self):
        with self.assertRaises(ArgumentTypeError):
            valid_port("999")
            valid_port("65536")


if __name__ == "__main__":
    unittest.main()
