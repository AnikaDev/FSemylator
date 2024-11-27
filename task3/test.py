import unittest
from unittest.mock import patch
from interpritator import ConfigParser
import json

class TestConfigParser(unittest.TestCase):

    def test_remove_comments(self):
        parser = ConfigParser()
        input_text = """
        /* This is a comment */
        key = 123;
        /* Another
        multiline
        comment */
        value = 'test';
        """
        expected_output = "key = 123;\nvalue = 'test';\n"
        self.assertEqual(parser.remove_comments(input_text), expected_output)

    def test_remove_dicts_block(self):
        parser = ConfigParser()
        input_text = """
        {key1 = 123;
        key2 = 'value';}
        key3 = 456;
        """
        expected_output = "key3 = 456;\n"
        self.assertEqual(parser.remove_dicts_block(input_text), expected_output)

    def test_parse_dicts(self):
        parser = ConfigParser()
        input_text = """
        {key1 = 123;
        key2 = 'value';
        key3 = 456;}
        """
        parser.parse_dicts(input_text)
        expected_variables = {
            "key1": 123,
            "key2": "value",
            "key3": 456
        }
        self.assertEqual(parser.variables, expected_variables)

    def test_evaluate_expressions(self):
        parser = ConfigParser()
        parser.variables = {
            "key1": 2,
            "key2": 3
        }
        input_text = "key3 = key1 + key2;"
        parser.evaluate_expressions(input_text)
        expected_variables = {
            "key1": 2,
            "key2": 3,
            "key3": 5
        }
        self.assertEqual(parser.variables, expected_variables)

    def test_evaluate_expressions_invalid(self):
        parser = ConfigParser()
        parser.variables = {
            "key1": 2
        }
        input_text = "key2 = key3 + 4;"
        with self.assertRaises(ValueError) as context:
            parser.evaluate_expressions(input_text)
        self.assertTrue("Error evaluating expression for key2" in str(context.exception))

    def test_save_to_json(self):
        parser = ConfigParser()
        parser.variables = {
            "key1": 123,
            "key2": "value"
        }
        with patch("builtins.open", unittest.mock.mock_open()) as mocked_file:
            parser.save_to_json(parser.variables, "output.json")
            mocked_file.assert_called_once_with("output.json", 'w')
            mocked_file().write.assert_called_once_with(
                json.dumps({"variables": parser.variables}, indent=4)
            )

if __name__ == "__main__":
    unittest.main()
