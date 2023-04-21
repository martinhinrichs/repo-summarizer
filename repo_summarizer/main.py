import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from typing import Dict
from collections import OrderedDict

from dotenv import load_dotenv
from langchain import PromptTemplate

load_dotenv()

import argparse
import os
from langchain.text_splitter import PythonCodeTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
import tiktoken


def summarize(filepath: str) -> str:
    """Summarize a single file."""

    def count_tokens(text):
        enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
        encoded = enc.encode(text)
        return len(encoded)

    with open(filepath, "r") as f:
        try:
            text = f.read()
        except UnicodeDecodeError:
            return ""

    if text.strip() == "":
        return ""

    splitter = PythonCodeTextSplitter(chunk_size=3500, chunk_overlap=0, length_function=count_tokens)

    docs = splitter.create_documents([text])

    llm = ChatOpenAI()

    prompt_template = f"""
You are the world's best code summarizer. Your summaries are extremely concise, clear and correct.
We are creating an overview of a repository, with a short description of each file. Summarize the following code (contained in {filepath}):
```
{'{text}'}
```
Use a single short sentence, unless the sentence would be very long (then you may split it up to make it more readable).
Only use more than one sentence if the code seems to play a central role in the overall application.

What the code in {filepath} will achieve is to"""

    refine_prompt_template = f"""
You are the world's best code summarizer. Your summaries are extremely concise, clear and correct.
We are creating an overview of a repository, with a short description of each file. You have already summarized 
the first part of the code in {filepath} as follows:

{{existing_answer}}

After the already summarized part, the code continues:
```
{{text}}
```
If necessary, adapt the summary to include the new code.
Use a single short sentence, unless the sentence would be very long (then you may split it up to make it more readable).
Only use more than one sentence if the code seems to play a central role in the overall application.

What the code in {filepath} will achieve is to"""

    prompt = PromptTemplate(template=prompt_template, input_variables=["text"])

    refine_prompt = PromptTemplate(template=refine_prompt_template, input_variables=["existing_answer", "text"])

    chain = load_summarize_chain(llm, chain_type="refine", verbose=True, question_prompt=prompt, refine_prompt=refine_prompt)

    summary = chain.run(docs)
    summary = summary[0].upper() + summary[1:]
    return summary


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
    parser = argparse.ArgumentParser(description="Summarize the content of a git repository")
    parser.add_argument("path", help="Path to the repository or file to summarize")
    args = parser.parse_args()

    path = args.path
    if os.path.exists(path):
        if os.path.isdir(path):
            print(json.dumps(summarize_repository(path), indent=4))
        elif os.path.isfile(path):
            print(summarize(path))
    else:
        print(f"Error: The path '{path}' does not exist.")
