import subprocess
from typing import Set, Dict

import fnmatch



def exclude_files(tracked_files: Set[str], path: str, exclude_patterns: Set[str]) -> Set[str]:
    for pattern in exclude_patterns:
        matched_files = {file for file in tracked_files if fnmatch.fnmatch(file, pattern)}
        tracked_files -= matched_files

    return tracked_files


def list_files(path: str, exclude_patterns: Set[str]) -> Dict[str, str]:
    """List all files tracked by git, excluding files matching the glob patterns in exclude_patterns, and return a
    dictionary with file paths and their hashes."""
    tracked_files_output = subprocess.check_output(["git", "ls-files"], cwd=path, universal_newlines=True)
    tracked_files = set(tracked_files_output.strip().splitlines())
    filtered_files = exclude_files(tracked_files, path, exclude_patterns)

    file_hashes_output = subprocess.check_output(["git", "hash-object", *filtered_files], cwd=path,
                                                 universal_newlines=True)
    file_hashes = file_hashes_output.strip().splitlines()

    return dict(zip(filtered_files, file_hashes))