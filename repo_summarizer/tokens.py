import tiktoken


def count_tokens(text):
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    encoded = enc.encode(text)
    return len(encoded)