import unittest

# pylint: disable=import-error
from src.models.command import MathCommand, OSCommand


class TestMathCommand(unittest.TestCase):
    def test_valid_expression(self):
        cmd = MathCommand("((30+10)*5+1)")
        res = cmd.run()
        self.assertEqual(res, ("((30+10)*5+1)", 201, True))

    def test_invalid_expression(self):
        cmd = MathCommand("((30+10))*5+1)")
        res = cmd.run()
        self.assertFalse(res.success)

    def test_unallowed_expersion(self):
        cmd = MathCommand("__import__('os').system('rm -rf test.txt')")
        res = cmd.run()
        self.assertFalse(res.success)


class TestOSCommand(unittest.TestCase):
    def test_valid_command(self):
        cmd = OSCommand("ls", ["-ahl"])
        res = cmd.run()
        self.assertTrue(res.success)

    def test_invalid_command(self):
        cmd = OSCommand("ls", ["-2"])
        res = cmd.run()
        self.assertFalse(res.success)

    def test_unallowed_command(self):
        cmd = OSCommand("rm", ["test.txt", "-rf"])
        res = cmd.run()
        self.assertFalse(res.success)
