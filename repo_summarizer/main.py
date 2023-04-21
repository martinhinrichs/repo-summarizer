from dotenv import load_dotenv

load_dotenv()

import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from typing import Dict
from collections import OrderedDict
import click

from repo_summarizer.summarize import summarize


@click.command()
@click.argument('path', type=click.Path(exists=True))
def main(path):
    if os.path.isdir(path):
        print(json.dumps(summarize_repository(path), indent=4))
    elif os.path.isfile(path):
        print(summarize(path))


def summarize_repository(path: str) -> Dict[str, str]:
    """Summarize all files in a repository."""
    if not os.path.exists(os.path.join(path, ".git")):
        raise ValueError("The path is not a git repository.")
    tracked_files_output = subprocess.check_output(["git", "ls-files"], cwd=path, universal_newlines=True)
    tracked_files = set(tracked_files_output.strip().splitlines())

    if os.path.exists(os.path.join(path, "repo-summarizer.json")):
        with open(os.path.join(path, "repo-summarizer.json"), "r") as f:
            config = json.load(f)
        for file in config.get("exclude", []):
            if file in tracked_files:
                tracked_files.remove(file)

    with ThreadPoolExecutor(max_workers=20) as executor:
        file_summaries = list(executor.map(summarize, tracked_files))

    return OrderedDict(sorted(zip(tracked_files, file_summaries)))


if __name__ == "__main__":
    main()
