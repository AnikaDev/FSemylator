import os
from tkinter import Tk, Text, END, Frame, Label
from tkinter.scrolledtext import ScrolledText
from shell_emulator import ShellEmulator

class ShellGUI:
    def __init__(self, emulator):
        self.emulator = emulator
        self.root = Tk()
        self.root.title("Unix Shell Emulator")
        self.setup_gui()

    def setup_gui(self):
        # Создаем основной фрейм
        self.frame = Frame(self.root, bg="black")
        self.frame.pack(fill="both", expand=True)

        # Метка с текущим состоянием консоли
        self.label = Label(
            self.frame,
            text=f"{self.emulator.computer_name}@shell:~$",
            fg="green",
            bg="black",
            font=("Courier", 12, "bold")
        )
        self.label.pack(anchor="w", padx=5, pady=5)

        # Поле вывода (история выполнения команд)
        self.text = ScrolledText(
            self.frame,
            height=20,
            width=80,
            bg="black",
            fg="green",
            insertbackground="green",
            font=("Courier", 12),
            state="normal"
        )
        self.text.pack(padx=5, pady=5, fill="both", expand=True)
        self.text.tag_configure("command", foreground="green", font=("Courier", 12, "bold"))

        # Поле ввода (однострочное)
        self.entry = Text(
            self.frame,
            height=1,
            width=80,
            bg="black",
            fg="green",
            insertbackground="green",
            font=("Courier", 12)
        )
        self.entry.pack(padx=5, pady=5)

        # Привязка клавиши Enter для выполнения команды
        self.entry.bind("<Return>", self.execute_command)

    def execute_command(self, event=None):
        # Получаем введенную команду
        command = self.entry.get("1.0", END).strip()
        if not command:
            return

        # Выполняем команду через эмулятор
        result = self.emulator.execute_command(command)

        # Выводим команду и результат в поле вывода
        self.text.insert(END, f"{self.emulator.computer_name}@{self.emulator.current_dir}:~$ {command}\n", "command")
        self.text.insert(END, f"{result}\n\n")

        # Прокручиваем текст до конца
        self.text.see(END)

        # Очищаем поле ввода
        self.entry.delete("1.0", END)

        if (emulator.running == False):
            exit(0)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    config_path = "config.txt"
    if not os.path.exists(config_path):
        print(f"Конфигурационный файл {config_path} не найден.")
    else:
        emulator = ShellEmulator(config_path)
        gui = ShellGUI(emulator)
        gui.run()
