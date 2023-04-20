from dotenv import load_dotenv
load_dotenv()

from langchain.text_splitter import PythonCodeTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
import tiktoken


def summarize(filepath: str) -> str:
    def count_tokens(text):
        enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
        encoded = enc.encode(text)
        return len(encoded)

    """Summarize a single file."""
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

    chain = load_summarize_chain(llm, chain_type="refine", verbose=True)

    summary = chain.run(docs)
    return summary

print(summarize('main.py'))