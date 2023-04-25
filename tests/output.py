import unittest
from collections import OrderedDict

from repo_summarizer.output import format_as_tree


class TestSummariesToTree(unittest.TestCase):

    def test_summaries_to_tree(self):
        file_summaries = OrderedDict({
            'a.txt': 'File A',
            'b.txt': 'File B',
            'folder1/c.txt': 'File C',
            'folder1/d.txt': 'File D',
            'folder2/e.txt': 'File E',
        })

        expected = (
            ".\n"
            "├── a.txt - File A\n"
            "├── b.txt - File B\n"
            "├── folder1\n"
            "│   ├── c.txt - File C\n"
            "│   └── d.txt - File D\n"
            "└── folder2\n"
            "    └── e.txt - File E"
        )

        result = format_as_tree(file_summaries)

        self.assertEqual(expected, result)

    def test_no_summary_separator(self):
        file_summaries = OrderedDict({
            'a.txt': 'File A',
            'b.txt': '',
            'folder1/c.txt': 'File C',
            'folder1/d.txt': '',
            'folder2/e.txt': 'File E',
        })

        expected = (
            ".\n"
            "├── a.txt - File A\n"
            "├── b.txt\n"
            "├── folder1\n"
            "│   ├── c.txt - File C\n"
            "│   └── d.txt\n"
            "└── folder2\n"
            "    └── e.txt - File E"
        )

        result = format_as_tree(file_summaries)

        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
