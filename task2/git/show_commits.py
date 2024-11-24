import os
import subprocess
from datetime import datetime
from typing import List, Tuple
import configparser
from graphviz import Digraph
import pydot


def load_config(config_file: str) -> dict:
    """
    @brief Загружает конфигурацию из файла.
    @param config_file Путь к файлу конфигурации.
    @return Словарь с параметрами конфигурации.
    """
    config = configparser.ConfigParser()
    print("Config file:" + config_file)
    config.read(config_file)
    return config


def get_commits(repo_path: str, since_date: str) -> List[Tuple[str, str, str]]:
    """
    @brief Получает список коммитов из репозитория с указанной даты.
    @param repo_path Путь к репозиторию Git.
    @param since_date Дата в формате, принимаемом командой 'git log --since', например, '2023-01-01'.
    @return Список кортежей (хэш коммита, дата, автор).
    @throws Exception Если команда Git завершилась с ошибкой.
    """
    git_command = [
        "git",
        "-C",
        repo_path,
        "log",
        "--pretty=format:%H %ct %an",
        "--since",
        since_date,
    ]
    result = subprocess.run(git_command, stdout=subprocess.PIPE, text=True)

    if result.returncode != 0:
        raise Exception(f"Error running git command: {result.stderr}")

    commits = result.stdout.splitlines()
    commit_data = [
        (
            c.split()[0],
            datetime.fromtimestamp(int(c.split()[1]), tz=None).strftime("%Y-%m-%d %H:%M:%S"),
            c.split()[2]
        )
        for c in commits
    ]
    return commit_data[::-1]  # Reverse to have chronological order


def build_dependency_graph(commits: List[Tuple[str, str, str]]) -> Digraph:
    """
    @brief Создаёт граф зависимостей коммитов с использованием Graphviz.
    @param commits Список кортежей (хэш коммита, дата, автор) в хронологическом порядке.
    @return Объект Digraph с построенным графом зависимостей.
    """
    dot = Digraph(comment="Git Commit Dependencies")

    for i, (commit, date, author) in enumerate(commits):
        dot.node(str(i), f"Commit: {commit}\nAuthor: {author}\nDate: {date}")
        if i > 0:
            dot.edge(str(i - 1), str(i))  # Connect commits in chronological order

    return dot


def save_graph(graph: Digraph, output_file: str) -> None:
    """
    @brief Сохраняет граф в файл PNG.
    @param graph Объект Digraph для сохранения.
    @param output_file Путь к файлу без расширения.
    """
    graph.render(output_file, format="png")
    print(f"Success! The graph has been saved to {output_file}.png")


def main(config_file: str) -> None:
    """
    @brief Основная функция. Загружает настройки, получает коммиты и строит граф.
    @param config_file Путь к файлу конфигурации.
    """
    config = load_config(config_file)
    repo_path = config['Settings']['repository_path']
    graph_output_path = config['Settings']['graph_output_path']
    since_date = config['Settings']['since_date']
    mode = config['Settings']['mode']
    os.environ["PATH"] = config['Settings']['graphviz'] + os.pathsep + os.environ["PATH"]

    if mode != "git_ignore":
        if not os.path.exists(repo_path):
            print(f"Error: Repository path '{repo_path}' does not exist.")
            return
        commits = get_commits(repo_path, since_date)
        if not commits:
            print(f"No commits found since {since_date}")
            return
        graph = build_dependency_graph(commits)
    else:
        graph = Digraph.from_file(graph_output_path)

    save_graph(graph, graph_output_path)


if __name__ == "__main__":
    config_file = "config.ini"
    main(config_file)
