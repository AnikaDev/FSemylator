import unittest
import os
import json
import zipfile  # Импортируем модуль zipfile
from shell_emulator import ShellEmulator


class TestShellEmulator(unittest.TestCase):
    def setUp(self):
        # Создание тестовой конфигурации
        self.test_config_path = "test_config.txt"
        with open(self.test_config_path, "w") as f:
            f.write("[Settings]\n")
            f.write("computer_name = TestMachine\n")
            f.write("virtual_fs_path = test_fs.zip\n")
            f.write("log_path = test_log.json\n")
            f.write("startup_script = test_startup.txt\n")

        # Создание виртуальной файловой системы
        self.test_vfs_path = "test_fs.zip"
        with zipfile.ZipFile(self.test_vfs_path, 'w') as zip_ref:
            zip_ref.writestr("dir1/", "")  # Папка
            zip_ref.writestr("test_file.txt", "Hello, World!")  # Файл

        # Создание стартового скрипта
        self.test_startup_script = "test_startup.txt"
        with open(self.test_startup_script, "w") as f:
            f.write("ls\n")

        self.emulator = ShellEmulator(config_path=self.test_config_path)

    def tearDown(self):
        # Удаление тестовых файлов
        os.remove(self.test_config_path)
        os.remove(self.test_vfs_path)
        os.remove(self.test_startup_script)
        if os.path.exists("test_log.json"):
            os.remove("test_log.json")

    def test_ls(self):
        # Тест команды ls
        output = self.emulator.ls()
        self.assertIn("[DIR] dir1 (permissions: 755)", output)
        self.assertIn("test_file.txt (permissions: 644)", output)

    def test_cd(self):
        # Тест команды cd
        self.emulator.cd("dir1")
        self.assertEqual(self.emulator.current_dir, "/dir1/")

    def test_chmod(self):
        # Тест команды chmod
        result = self.emulator.execute_command("chmod 600 test_file.txt")
        self.assertEqual(result, "Установлены права '600' для файла test_file.txt.")

        result = self.emulator.execute_command("chmod 600 test_file1.txt")
        self.assertEqual(result, "Файл или каталог test_file1.txt не найден в текущей директории.")

    def test_rm(self):
        # Тест команды rm
        result = self.emulator.rm("test_file.txt")
        self.assertEqual(result, "Файл test_file.txt удалён.")
        self.assertNotIn("test_file.txt", self.emulator.vfs)

    def test_uptime(self):
        # Тест команды uptime
        output = self.emulator.uptime()
        self.assertTrue("Система работает" in output)

    def test_exit(self):
        # Тест команды exit
        result = self.emulator.exit()
        self.assertEqual(result, "Выход из системы.")
        self.assertFalse(self.emulator.running)

    def test_logging(self):
        # Тест логирования
        self.emulator.execute_command("ls")
        self.emulator.execute_command("uptime")
        with open("test_log.json", "r") as f:
            logs = [json.loads(line) for line in f]
        self.assertTrue(any("uptime" in log["command"] for log in logs))
        self.assertTrue(any("ls" in log["command"] for log in logs))

    def test_startup_script(self):
        # Тест выполнения стартового скрипта
        with open("test_log.json", "r") as f:
            logs = [json.loads(line) for line in f]
        self.assertTrue(any("ls" in log["command"] for log in logs))


if __name__ == "__main__":
    unittest.main()
