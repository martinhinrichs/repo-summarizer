import unittest
from unittest import mock
import os
from repo_summarizer.repository import list_files

class TestListFiles(unittest.TestCase):
    @mock.patch("subprocess.check_output")
    def test_glob_patterns(self, mock_check_output):
        mock_check_output.return_value = "README.md\n.env\napp/package-lock.json\napp/src/main.py\napp/src/utils.py\napp/poetry.lock\n"
        repo_path = os.path.dirname(os.path.abspath(__file__))
        exclude_patterns = {"**/*.lock", "**/package-lock.json", ".env"}

        expected_files = {
            "README.md",
            "app/src/main.py",
            "app/src/utils.py"
        }

        self.assertEqual(list_files(repo_path, exclude_patterns), expected_files)

if __name__ == "__main__":
    unittest.main()
