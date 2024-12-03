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
        text, expression = self.extract_first_block_and_remainder(text)
        clean_text = re.sub(r'\s+', ' ', text).strip()
        self.parse_dicts2(clean_text,'')
        self.evaluate_expressions(expression)
        return self.variables

    def extract_first_block_and_remainder(self, text: str):
        stack = []
        start = None

        for i, char in enumerate(text):
            if char == '{':
                if not stack:
                    start = i  # Сохраняем индекс начала первого блока
                stack.append(char)
            elif char == '}':
                if stack:
                    stack.pop()
                    if not stack:  # Блок завершён
                        first_block = text[start:i + 1]
                        remainder = text[i + 1:].strip()
                        return first_block, remainder

        # Если не найден корректный блок
        return None, text.strip()
    def remove_comments(self, text: str) -> str:
        text = re.sub(r'/\+.*?\+/', '', text, flags=re.DOTALL)  # Remove multiline comments
        return text

    def remove_dicts_block(self, text: str) -> str:
        text = re.sub(r"\{(.*?)\}", '', text, flags=re.DOTALL)  # Remove multiline comments
        return text

    def evaluate_postfix(self, expression):
        # Определяем операции
        operations = {
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x / y,
            'abs': lambda x: abs(x),
            'mod': lambda x, y: x % y
        }

        stack = []
        tokens = expression.split()

        for token in tokens:
            if token.lstrip('-').isdigit():  # Если токен — число
                stack.append(int(token))
            elif token in operations:  # Если токен — операция
                if token == 'abs':  # Унарная операция
                    if len(stack) < 1:
                        raise ValueError("Недостаточно операндов для 'abs'")
                    x = stack.pop()
                    stack.append(operations[token](x))
                else:  # Бинарная операция
                    if len(stack) < 2:
                        raise ValueError(f"Недостаточно операндов для '{token}'")
                    y = stack.pop()
                    x = stack.pop()
                    stack.append(operations[token](x, y))
            else:
                raise ValueError(f"Неизвестный токен: {token}")

        if len(stack) != 1:
            raise ValueError("Неверное выражение: стек содержит лишние элементы")

        return stack[0]

    def parse_dicts2(self, block: str, prefix_var: str):
        """
        Рекурсивно парсит строку с выражением в виде вложенных ключей и значений.
        """
        result = {}
        key_value_pattern = re.compile(r'(\w+)\s*=\s*(\{.*?\}|[^;]+)')
        nested_block_pattern = re.compile(r'^\{(.*)\}$')

        while block:
            match = key_value_pattern.search(block)
            if match:
                key, value = match.groups()
                block = block[match.end():].lstrip(";")

                # Если значение - вложенный блок, разбираем его рекурсивно
                if nested_block_pattern.match(value):
                    inner_block = nested_block_pattern.match(value).group(1)
                    value = self.parse_dicts2(inner_block, key+".")
                else:
                    result[prefix_var + key] = value
                    self.variables[prefix_var + key] = value
            else:
                break
        return result

    def evaluate_expressions(self, text: str):
        expr_pattern = r"([a-z0-9]+) = (.+?);"
        matches = re.findall(expr_pattern, text)
        for var_name, expression in matches:
            try:
                # Replace variables in the expression with their current values
                # Simple 'for' does not work, need to sort...
                # for key, value in self.variables.items():
                for key, value in sorted(self.variables.items(), key=lambda item: item[0], reverse=False):
                    expression = expression.replace(key, str(value))

                # Expression, need to calculate :(
                if (len(expression) > 1 and expression[0] == '$' and expression[-1] == '$'):
                    expression_in = expression[1:-1]
                    expression = self.evaluate_postfix(expression_in)
                    print(f"calculate expression: '{expression_in}'={expression}")

                # Evaluate the expression safely
                self.variables[var_name] = expression
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
