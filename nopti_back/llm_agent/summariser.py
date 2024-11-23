import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

system_prompt = """
                You are a chatbot making summaries from input text. Here is the response template you use :
                Title :
                One sentence describing what the content is about.
                Summary :
                A numbered list of the 2 most relevant things in the content, each with one sentence.
                """

api_key = os.getenv("OPENAI_API_KEY")


def summarize_text(input_text: str) -> str:
    client = OpenAI(
    base_url="http://127.0.0.1:8111/v1",  # Assuming LLM Studio uses the /v1 endpoint
    api_key="not-needed",  # LLM studio often doesn't need a key. You can use any placeholder string if needed.
)
    response = client.chat.completions.create(
        model="noneed",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input_text},
        ],
        temperature=0.7,
        max_tokens=500,
    )
    return response.choices[0].message.content
