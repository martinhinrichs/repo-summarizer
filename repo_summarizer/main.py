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
from repo_summarizer.tokens import count_tokens_in_file


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

    # Exclude files listed in repo-summarizer.json
    if os.path.exists(os.path.join(path, "repo-summarizer.json")):
        with open(os.path.join(path, "repo-summarizer.json"), "r") as f:
            config = json.load(f)
        for file in config.get("exclude", []):
            if file in tracked_files:
                tracked_files.remove(file)

    # Ask for confirmation if summarization price is > 0.1 USD
    tokens = {file: count_tokens_in_file(os.path.join(path, file)) for file in tracked_files}
    tokens = OrderedDict(sorted(tokens.items()))

    total_tokens = sum(tokens.values())
    price = 0.002 # price per 1k tokens for chatgpt-3.5-turbo
    cost = (total_tokens / 1000) * price
    limit = 0.0

    if (cost > limit):
        click.echo(f"Total tokens: {total_tokens}")
        files_by_size_desc = OrderedDict(sorted(tokens.items(), key=lambda x: x[1], reverse=True))

        click.echo(f"Top 10 files by tokens:")
        for file, size in list(files_by_size_desc.items())[:10]:
            click.echo(f"  {file}: {size}")

        click.echo()
        if click.confirm(f"Warning: The cost of summarizing this repository is {cost} USD ({price} USD/1k tokens). Do you want to continue?") is False:
            raise click.Abort()

    with ThreadPoolExecutor(max_workers=20) as executor:
        file_summaries = list(executor.map(summarize, tracked_files))

    return OrderedDict(sorted(zip(tracked_files, file_summaries)))


if __name__ == "__main__":
    main()
