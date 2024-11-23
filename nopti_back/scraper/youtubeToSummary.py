from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.schema import SystemMessage
from langchain_openai.chat_models import ChatOpenAI


from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv

import os

system_prompt = """
                You are a chatbot making summaries from input text. Here is the response template you use :
                Title :
                Two sentences describing what the content is about.
                Summary :
                A numbered list of the 5 most relevant things in the content, each with two sentences.
                """


async def chat_with_youtube_video(video_id):
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    model = "gpt-3.5-turbo"

    """# Extract the transcript"""

    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "fr"])

    formatted_transcript = ""
    for i in range(len(transcript)):
        formatted_transcript += transcript[i]["text"] + " "

    """# Prepare the agent"""

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                content=system_prompt,
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{human_input}"),
        ]
    )

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    llm = ChatOpenAI(model_name=model, openai_api_key=api_key)

    chat_llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        memory=memory,
        verbose=True,
    )

    """# Talk with the agent"""

    answer = chat_llm_chain.predict(human_input=formatted_transcript)

    return answer
