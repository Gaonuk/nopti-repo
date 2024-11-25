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
    if not isinstance(input_text, str):
        input_text = str(input_text)
    print(input_text)

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input_text},
        ],
        temperature=0.7,
        max_tokens=500,
    )
    return response.choices[0].message.content
