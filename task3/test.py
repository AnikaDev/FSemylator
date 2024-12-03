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

if __name__ == "__main__":
    unittest.main()
