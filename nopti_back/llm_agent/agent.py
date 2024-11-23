import re
from openai import OpenAI
from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime

import sys
import os

# Get the absolute path to the repository root
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import Boolean

from llm_agent.summariser import summarize_text
from speech.text_to_speech import load_sound_effect, text_to_speech
from models.content_entity import ContentEntity
import instructor

# Add new response model
class DecisionResponse(BaseModel):
    action: Literal["next", "summarize", "play", "unknown"]


class DecisionOutput(BaseModel):
    sound: Optional[bytes]
    decision: DecisionResponse

class decisionHandler:
    openai_client: OpenAI
    def __init__(self, openai_client: OpenAI):
        self.openai_client = openai_client


    def handle_decision(self,user_input: str, next_content: ContentEntity):
        # Patch the OpenAI client with instructor
#         client = instructor.from_openai( OpenAI(
#     base_url="http://127.0.0.1:8111/v1",  # Assuming LLM Studio uses the /v1 endpoint
#     api_key="not-needed",  # LLM studio often doesn't need a key. You can use any placeholder string if needed.
# ))
        #user_input = "Lionel messi est le meilleur joueur de football au monde. Mais pas Chritiano ronaldo"
        # Get structured response using instructor
        # decision = client.chat.completions.create(
        #     model="gpt-4o-mini",
        #     response_model=DecisionResponse,
        #     messages=[
        #         {"role": "system", "content": "You are a helpful assistant."}
        #         ,{"role": "user", "content": f"Classify the following user input into one of the following categories: next, summarize, play, or unknown. User input: {user_input}"}]
        # )
        _next = Boolean(re.search(r"\b(next)\b", user_input, re.IGNORECASE))
        _summarize = Boolean(re.search(r"\b(summarize)\b", user_input, re.IGNORECASE))
        _play = Boolean(re.search(r"\b(play)\b", user_input, re.IGNORECASE))
        
        if _next:
            sound = load_sound_effect("/Users/theomichel/Coding/Hackaton/nopti_back/SON META.mp3")
            return DecisionOutput(sound=sound, decision=DecisionResponse(action="next"))
            
        if _summarize:
            text = summarize_text(next_content.id)
            sound = text_to_speech(text)
            return DecisionOutput(sound=sound, decision=DecisionResponse(action="summarize"))
            
        if _play:
            sound = text_to_speech("Playing music: " + next_content.title)
            return DecisionOutput(sound=sound, decision=DecisionResponse(action="play"))
            
        sound = text_to_speech("I'm not sure what you want me to do.")
        return DecisionOutput(sound=sound, decision=DecisionResponse(action="unknown"))
        
        



def ai_workflow(rankings: list[ContentEntity], input: str = None):
    def update_passed_content(ranking: ContentEntity):
        ranking.passed = True
        ranking.shown = True

        ai_workflow(rankings, "")

    def play_music():
        # TODO 
        pass

    # Filter rankings to only show unshown content
    rankings = [r for r in rankings if not r.shown]
    ranking = rankings[0]
    ranking_id = ranking.id

    _next = Boolean(re.search(r"text|next", input, re.IGNORECASE))
    summarize = Boolean(re.search(r"summar", input, re.IGNORECASE))
    play = Boolean(re.search(r"play", input, re.IGNORECASE))
    user_input = Boolean(re.search(r"user_input", input, re.IGNORECASE))

    if _next:
        text_to_speech(ranking.title)
        update_passed_content(ranking)

    elif summarize:
        text_to_speech(summarize_text(ranking_id))
        ai_workflow(rankings, "user_input")

    elif play:
        play_music(ranking_id)
        ranking.passed = False
        ranking.shown = True

        ai_workflow(rankings, user_input)

    elif user_input:
        user_input = input(
            "Waiting for your response: "
        )  # TODO: deal with waiting for user answer
        ai_workflow(rankings, user_input)

    else:
        text_to_speech("Are you interested in this content?" + ranking.title)
        user_input = input(
            "Waiting for your response: "
        )  # TODO: deal with waiting for user answer
        ai_workflow(rankings, user_input)
