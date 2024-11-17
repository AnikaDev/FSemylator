import unittest
from unittest.mock import patch, MagicMock, mock_open
from graphviz import Digraph
import show_commits

class TestScript(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data="[Settings]\nrepository_path=repo\nsince_date=2023-01-01\ngraph_output_path=graph\n")
    def test_load_config(self, mock_file):
        config = show_commits.load_config("config.ini")
        self.assertEqual(config['Settings']['repository_path'], "repo")
        self.assertEqual(config['Settings']['since_date'], "2023-01-01")

    @patch("subprocess.run")
    def test_get_commits(self, mock_subprocess):
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="abc123 1672531200 Anika\nxyz789 1672617600 Anna\n"
        )
        repo_path = "repo"
        since_date = "2023-01-01"
        expected = [
            ("xyz789", "2023-01-02 03:00:00", "Anna"),
            ("abc123", "2023-01-01 03:00:00", "Anika")
        ]
        commits = show_commits.get_commits(repo_path, since_date)
        self.assertEqual(commits, expected)

    def test_build_dependency_graph(self):
        commits = [
            ("abc123", "2023-01-01 00:00:00", "Anika"),
            ("xyz789", "2023-01-02 00:00:00", "Anna")
        ]
        graph = show_commits.build_dependency_graph(commits)
        self.assertIn('abc123', graph.source)
        self.assertIn('xyz789', graph.source)
        self.assertIn("->", graph.source)  # Ensure edges are present

    @patch("graphviz.Digraph.render")
    def test_save_graph(self, mock_render):
        graph = Digraph()
        show_commits.save_graph(graph, "output")
        mock_render.assert_called_once_with("output", format="png")

if __name__ == "__main__":
    unittest.main()
