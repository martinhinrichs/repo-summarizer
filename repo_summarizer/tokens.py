import tiktoken


def count_tokens(text):
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    encoded = enc.encode(text)
    return len(encoded)


def count_tokens_in_file(path: str) -> int:
    """Count the number of tokens in a file."""
    with open(path, "r") as f:
        try:
            text = f.read()
        except UnicodeDecodeError:
            return 0

    if text.strip() == "":
        return 0

    return count_tokens(text)
