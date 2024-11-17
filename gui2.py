# pip install windows-curses
import curses
import os
import tkinter as tk
from tkinter import messagebox
from shell_emulator import ShellEmulator


def show_popup(command):
    """Отображает всплывающее окно с введенной командой."""
    root = tk.Tk()
    root.withdraw()  # Скрыть основное окно
    messagebox.showinfo("Введенная команда", command)
    root.destroy()

def terminal(stdscr):
    # Настройка цветов
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Белый текст на черном фоне
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Зеленый текст на черном фоне

    stdscr.clear()
    stdscr.bkgd(' ', curses.color_pair(1))  # Установить фон и текст
    #stdscr.addstr("UNIX Terminal Emulator\n", curses.color_pair(2))
    #stdscr.refresh()

    while True:
        stdscr.addstr(f"{emulator.computer_name}:{emulator.current_dir}>", curses.color_pair(1))
        stdscr.refresh()

        # Получить ввод пользователя
        curses.echo()  # Включить отображение введенного текста
        stdscr.attron(curses.color_pair(1))
        command = stdscr.getstr().decode('utf-8')
        stdscr.attroff(curses.color_pair(1))
        curses.noecho()  # Выключить отображение введенного текста

        # Показать всплывающее окно с введенной командой
        # show_popup(command)
        result = emulator.execute_command(command)

        # Вывести "ok" и перенести строку
        stdscr.addstr(f"{result}\n", curses.color_pair(2))
        stdscr.refresh()
        if (emulator.running==False):
            exit(0)


if __name__ == "__main__":
    config_path = "config.txt"
    if not os.path.exists(config_path):
        print(f"Конфигурационный файл {config_path} не найден.")
    else:
        emulator = ShellEmulator(config_path)
    curses.wrapper(terminal)
