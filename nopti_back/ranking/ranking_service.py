from pathlib import Path
from typing import List
from openai import OpenAI
from pydantic import BaseModel

from contants import OPENAI_API_KEY


def classify_content(
    to_classify_content: list[dict[str, str | int]],
    classified_content: list[dict[str, str | bool]],
):
    """
    Classify content based on a list of content to classify and a list of classified content.

    Args:
    - to_classify_content (list[dict[str, str | int]]): List of content to classify.
    - classified_content (list[dict[str, str | bool]]): List of classified content.

    Returns:
    - list[dict[str, str | bool]]: List of classified content.
    """

    class ContentRanking(BaseModel):
        id: int
        ranking: int

    class ClassifiedContent(BaseModel):
        content_rankings: List[ContentRanking]

    openai_client = OpenAI(api_key=OPENAI_API_KEY)

    system_prompt = Path("ranking/system_prompt.md").read_text()

    def prompt_for_classification(to_classify_content, classified_content) -> str:
        return f"Please classify this content. The content to classify is {to_classify_content}. The classified content is: {classified_content}."

    response = openai_client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": prompt_for_classification(
                    to_classify_content, classified_content
                ),
            },
        ],
        response_format=ClassifiedContent,
    )
    classified_results = response.choices[0].message.parsed

    return classified_results
