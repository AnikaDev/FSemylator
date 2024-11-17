import os
import zipfile
import json
import configparser
import time
from datetime import datetime


class ShellEmulator:
    def __init__(self, config_path):
        self.config = configparser.ConfigParser()
        print("Config file:"+config_path)
        self.config.read(config_path)

        self.computer_name = self.config['Settings']['computer_name']
        self.vfs_path = self.config['Settings']['virtual_fs_path']
        self.log_path = self.config['Settings']['log_path']
        self.startup_script = self.config['Settings']['startup_script']

        self.vfs = {}
        self.current_dir = "/"
        self.running = True
        self.start_time = time.time()  # Время запуска программы

        self.load_virtual_fs()

    def load_virtual_fs(self):
        """Загрузка виртуальной файловой системы из ZIP-архива."""
        try:
            with zipfile.ZipFile(self.vfs_path, 'r') as zip_ref:
                self.vfs = {"": []}  # Корневая директория
                for name in zip_ref.namelist():
                    parts = name.strip("/").split("/")
                    current_level = self.vfs

                    for part in parts[:-1]:
                        if part not in current_level:
                            current_level[part] = {"": [], "permissions": "755"}  # Подкаталог
                        current_level = current_level[part]

                    # Добавляем файл или подкаталог
                    if name.endswith("/"):
                        current_level[parts[-1]] = {"": [], "permissions": "755"}  # Пустой каталог
                    else:
                        current_level[""].append({"name": parts[-1], "permissions": "644"})  # Файл

        except FileNotFoundError:
            print(f"Ошибка: архив {self.vfs_path} не найден.")
            self.running = False

    def log_action(self, action, result):
        """Логирует действие и результат выполнения."""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "command": action,
            "result": result
        }
        with open(self.log_path, "a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def run_startup_script(self):
        result = ""
        """Выполняет команды из стартового скрипта."""
        if os.path.exists(self.startup_script):
            with open(self.startup_script, 'r') as script:
                commands = script.readlines()
                for command in commands:
                    result += (f"Запуск команды из скрипта: {command}\n")
                    result += self.execute_command(command.strip())
                    result += "\n"
        else:
            result = f"Стартовый скрипт не найден: {self.startup_script}\n"
        return result

    def get_current_level(self):
        """Возвращает текущую директорию."""
        parts = self.current_dir.strip("/").split("/")
        current_level = self.vfs
        for part in parts:
            if part:
                current_level = current_level[part]
        return current_level

    def execute_command(self, command):
        """Обработка команд shell."""
        try:
            if command.startswith("ls"):
                result = self.ls()
            elif command.startswith("cd"):
                result = self.cd(command.split(" ", 1)[1])
            elif command.startswith("exit"):
                result = self.exit()
            elif command.startswith("chmod"):
                result = self.chmod(command.split(" ", 2))
            elif command.startswith("uptime"):
                result = self.uptime()
            elif command.startswith("rm"):
                result = self.rm(command.split(" ", 1)[1])
            else:
                result = f"Неизвестная команда: {command}"
            self.log_action(command, result)
        except Exception as e:
            result = f"Ошибка выполнения команды '{command}': {e}"
            print(result)
            self.log_action(command, result)
        return result

    def ls(self):
        """Выводит содержимое текущей директории с уровнями доступа."""
        current_level = self.get_current_level()
        result = []
        for directory, content in current_level.items():
            if directory and directory != "permissions":  # Это подкаталог
                result.append(f"[DIR] {directory} (permissions: {content['permissions']})")
        for file in current_level[""]:  # Файлы
            result.append(f"{file['name']} (permissions: {file['permissions']})")
        output = "\n".join(result)
        print(output)
        return output

    def cd(self, path):
        """Изменяет текущую директорию."""
        current_level = self.get_current_level()
        if path == "..":
            self.current_dir = "/".join(self.current_dir.rstrip('/').split('/')[:-1]) or "/"
            return f"Перешли в директорию {self.current_dir}"
        elif path in current_level and path:  # Переход в подкаталог
            self.current_dir = f"{self.current_dir.rstrip('/')}/{path}/"
            return f"Перешли в директорию {self.current_dir}"
        else:
            return f"Директория {path} не найдена."

    def exit(self):
        """Завершает работу shell."""
        self.running = False
        return "Выход из системы."

    def chmod(self, args):
        """Изменяет права доступа файла или каталога."""
        if len(args) < 3:
            return "Неправильный формат команды chmod. Используйте: chmod <права> <файл/каталог>"
        permissions, target = args[1], args[2]
        current_level = self.get_current_level()

        if target in current_level:  # Если это подкаталог
            current_level[target]["permissions"] = permissions
            return f"Установлены права '{permissions}' для каталога {target}."
        else:  # Если это файл
            for file in current_level[""]:
                if file["name"] == target:
                    file["permissions"] = permissions
                    return f"Установлены права '{permissions}' для файла {target}."
        return f"Файл или каталог {target} не найден в текущей директории."

    def uptime(self):
        """Выводит время работы shell с момента запуска."""
        uptime_seconds = time.time() - self.start_time
        uptime_str = f"Система работает {uptime_seconds:.2f} секунд."
        print(uptime_str)
        return uptime_str

    def rm(self, filename):
        """Удаляет файл."""
        current_level = self.get_current_level()
        for file in current_level[""]:
            if file["name"] == filename:
                current_level[""].remove(file)
                return f"Файл {filename} удалён."
        return f"Файл {filename} не найден в текущей директории."

    def start(self):
        """Запуск shell."""
        while self.running:
            command = input(f"{self.computer_name}:{self.current_dir}$ ")
            self.execute_command(command)


if __name__ == "__main__":
    config_path = "config.txt"
    if not os.path.exists(config_path):
        print(f"Конфигурационный файл {config_path} не найден.")
    else:
        emulator = ShellEmulator(config_path)
        emulator.start()
