from dotenv import load_dotenv

from repo_summarizer.output import format_as_tree
from repo_summarizer.repository import list_files

load_dotenv()

import json
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Set
from collections import OrderedDict
import click

from repo_summarizer.summarize import summarize
from repo_summarizer.tokens import count_tokens_in_file


@click.command()
@click.argument("path", type=click.Path(exists=True), default=".")
def main(path):
    if os.path.isdir(path):
        summary = summarize_repository(path)
        with open(os.path.join(path, "repo-summary.json"), "w") as f:
            json.dump(summary, f, indent=4)
        tree = format_as_tree(summary)
        click.echo(tree)


def summarize_repository(path: str) -> OrderedDict[str, str]:
    """Summarize all files in a repository."""
    if not os.path.isdir(path) or not os.path.exists(os.path.join(path, ".git")):
        raise ValueError("The path is not a git repository.")

    if os.path.exists(os.path.join(path, "repo-summarizer.json")):
        with open(os.path.join(path, "repo-summarizer.json"), "r") as f:
            config = json.load(f)
            exclude_patterns = set(config.get("exclude", []))

    tracked_files = list_files(path, exclude_patterns)
    calculate_cost_and_confirm(tracked_files, path)

    summarize_with_basepath = lambda file: summarize(file, path)

    with ThreadPoolExecutor(max_workers=20) as executor:
        file_summaries = list(executor.map(summarize_with_basepath, tracked_files))

    return OrderedDict(sorted(zip(tracked_files, file_summaries)))


def calculate_cost_and_confirm(tracked_files: Set[str], repo_path: str) -> None:
    """Ask for confirmation if the cost of summarizing the repository is above the limit."""
    tracked_files_full_path = [os.path.join(repo_path, file) for file in tracked_files]

    tokens = {file: count_tokens_in_file(file) for file in tracked_files_full_path}
    total_tokens = sum(tokens.values())
    price = 0.002  # price per 1k tokens for chatgpt-3.5-turbo
    cost = (total_tokens / 1000) * price
    limit = 0.0

    if cost > limit:
        click.echo(f"Total tokens: {total_tokens}", err=True)
        files_by_size_desc = OrderedDict(sorted(tokens.items(), key=lambda x: x[1], reverse=True))

        click.echo(f"Top 10 files by tokens:", err=True)
        for file, size in list(files_by_size_desc.items())[:10]:
            click.echo(f"  {file}: {size}", err=True)

        click.echo(err=True)
        if click.confirm(
                f"Warning: The cost of summarizing this repository is {cost} USD ({price} USD/1k tokens). Do you want to continue?",
                err=True) is False:
            raise click.Abort()


if __name__ == "__main__":
    main()
