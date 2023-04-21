import json
import os
import subprocess
from typing import Set


def list_files(path: str) -> Set[str]:
    """List all files tracked by git, excluding files specified in repo-summarizer.json."""
    def exclude_files(tracked_files: Set[str], path: str) -> Set[str]:
        if os.path.exists(os.path.join(path, "repo-summarizer.json")):
            with open(os.path.join(path, "repo-summarizer.json"), "r") as f:
                config = json.load(f)
            for file in config.get("exclude", []):
                if file in tracked_files:
                    tracked_files.remove(file)

        return tracked_files

    tracked_files_output = subprocess.check_output(["git", "ls-files"], cwd=path, universal_newlines=True)
    tracked_files = set(tracked_files_output.strip().splitlines())
    return exclude_files(tracked_files, path)
