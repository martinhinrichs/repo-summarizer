from langchain import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import PythonCodeTextSplitter

from repo_summarizer.tokens import count_tokens


def summarize(filepath: str) -> str:
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
