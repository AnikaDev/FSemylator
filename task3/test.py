import unittest
from unittest.mock import patch
from interpritator import ConfigParser
import json

class TestConfigParser(unittest.TestCase):
    def test1(self):
        parser = ConfigParser()
        parser.variables = {
            "key1": 2
        }
        input_text = "def test = $key1 4 +$;"
        parser.evaluate_expressions(input_text)
        self.assertEqual(parser.variables['test'], 6)

    def test2(self):
        parser = ConfigParser()
        parser.variables = {
            "key1": -2
        }
        input_text = "def test = $key1 abs$;"
        parser.evaluate_expressions(input_text)
        self.assertEqual(parser.variables['test'], 2)

    def testRemoveComments(self):
        parser = ConfigParser()
        text = "/+ test\n test+/\nprivet"
        text = parser.remove_comments(text)
        self.assertEqual(text, "\nprivet")

if __name__ == "__main__":
    unittest.main()
