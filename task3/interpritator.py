import re
import json
import sys
from typing import Any, Dict

class ConfigParser:
    def __init__(self):
        self.constants = {}
        self.variables = {}

    def parse(self, text: str) -> Dict[str, Any]:
        text = self.remove_comments(text)
        self.parse_dicts(text)
        text = self.remove_dicts_block(text)
        self.evaluate_expressions(text)
        return self.variables

    def remove_comments(self, text: str) -> str:
        text = re.sub(r'/\+.*?\+/s', '', text, flags=re.DOTALL)  # Remove multiline comments
        return text

    def remove_dicts_block(self, text: str) -> str:
        text = re.sub(r"\{(.*?)\}", '', text, flags=re.DOTALL)  # Remove multiline comments
        return text

    def infixToPostfix(self, expression: str) -> str:
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2, 'abs': 3, 'mod': 3}
        output = []
        stack = []
        tokens = expression.split(' ')

        for token in tokens:
            if (token.isdigit() or (token.startswith('-') and token[1:].isdigit())) or token in ['abs', 'mod']:  # Если это операнд (число или функция)
                output.append(token)
            elif token.isalnum():  # Если это переменная
                output.append(token)
            elif token in precedence:  # Если это оператор
                while (stack and stack[-1] != '(' and
                       precedence.get(token, 0) <= precedence.get(stack[-1], 0)):
                    output.append(stack.pop())
                stack.append(token)
            elif token == '(':
                stack.append(token)
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()  # Убираем открывающую скобку

        res = output[0]
        pos = 1
        while stack:
            res += stack.pop() + output[pos]
            pos = pos + 1
            #output.append(stack.pop())

        #return ' '.join(output)
        return res

    def parse_dicts(self, text: str):
        dict_pattern = r"\{(.*?)\}"  # Matches dictionary blocks
        dict_matches = re.findall(dict_pattern, text, re.DOTALL)

        for block in dict_matches:
            entries = re.findall(r"([a-z0-9]+) = (.*?);", block)
            for key, value in entries:
                if (value.isdigit() or (value.startswith('-') and value[1:].isdigit())):
                    self.variables[key] = int(value)
                elif re.match(r"^'.*?'$", value, flags=re.DOTALL):
                    self.variables[key] = value.strip("'")
                elif value in self.constants:
                    self.variables[key] = self.constants[value]
                else:
                    raise ValueError(f"Invalid value for key {key}: {value}")

    def evaluate_expressions(self, text: str):
        expr_pattern = r"([a-z0-9]+) = (.+?);"
        matches = re.findall(expr_pattern, text)
        for var_name, expression in matches:
            try:
                # Replace variables in the expression with their current values
                for key, value in self.variables.items():
                    expression = expression.replace(key, str(value))

                # print(f"var:{var_name} = {expression}")
                # postfix to infix
                # expression = self.infixToPostfix(expression)

                # Evaluate the expression safely
                self.variables[var_name] = eval(expression)
            except Exception as e:
                raise ValueError(f"Error evaluating expression for {var_name}: {expression} ({e})")

    def save_to_json(self, data: Dict[str, Any], output_file: str):
        output_data = {
            "variables": self.variables
        }
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=4)
        print(json.dumps(output_data, indent=4))

if __name__ == "__main__":
    try:
        with open("config.txt", "r") as config_file:
            lines = config_file.readlines()
            settings = {}
            for line in lines:
                if line.strip().startswith("outputFile"):
                    settings["outputFile"] = line.split("=")[1].strip()
                elif line.strip().startswith("inputFile"):
                    settings["inputFile"] = line.split("=")[1].strip()

        input_file = settings.get("inputFile")
        output_file = settings.get("outputFile")

        if not input_file or not output_file:
            raise ValueError("Both inputFile and outputFile must be specified in the settings section of config.txt")

        with open(input_file, "r") as infile:
            input_text = infile.read()

        parser = ConfigParser()
        parsed_data = parser.parse(input_text)
        parser.save_to_json(parsed_data, output_file)

        print(f"Parsing successful. Output saved to {output_file}")
    except Exception as e:
        print(f"Error: {e}")
