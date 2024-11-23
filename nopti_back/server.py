from typing import List, Optional
from fastapi import FastAPI, Response
from openai import OpenAI
import uvicorn
from pydantic import BaseModel
from datetime import datetime
from fastapi.responses import FileResponse
import tempfile
import os

from llm_agent.agent import decisionHandler
from models.content_entity import ContentEntity
from scraper.get_updated_news import get_update_news
from speech.text_to_speech import text_to_speech

app = FastAPI()

# Store content rankings in memory
content_rankings: List[ContentEntity] = []
content_number = 0
class QueryInput(BaseModel):
    text: str

@app.get("/")
def read_root():
    return {"status": "running", "timestamp": datetime.now().isoformat()}

@app.get("/hello")
def hello():
    text = "Hi I am Nopty, here to help you make the most of your day ! Fetching News..."
    audio_data = text_to_speech(text)
    if audio_data:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name
        
        # Return FileResponse and cleanup after
        return FileResponse(
            temp_path,
            media_type="audio/mpeg",
            background=lambda: os.unlink(temp_path)  # Cleanup temp file after sending
        )
    return {"error": "Failed to generate speech"}

@app.get("/content")
async def get_content():
    """Fetch and return all available content"""
    global content_rankings
    global content_number
    
    # Get fresh content if none exists
    if not content_rankings:
        news_data = get_update_news()
        for item in news_data["news_list"]:
            content_rankings.append(
                ContentEntity(
                    id=len(content_rankings),
                    title=item["title"],
                    link=item["link"],
                    summary=item["summary"],
                    source=item["source"],
                    date=item["date"],
                    type="article",
                    passed=False,
                    shown=False
                )
            )
    
    # Return audio response in same format as /hello endpoint
    current_content = content_rankings[content_number]
    speech_data = text_to_speech("Here is the first content of the day I recommend you to read : " + current_content.summary)
    
    if speech_data:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_file.write(speech_data)
            temp_path = temp_file.name
        
        # Return FileResponse and cleanup after
        return FileResponse(
            temp_path,
            media_type="audio/mpeg",
            background=lambda: os.unlink(temp_path)  # Cleanup temp file after sending
        )
    return {"error": "Failed to generate speech", "content": [content.dict() for content in content_rankings]}

@app.get("/get-decision")
async def get_decision(user_input: str): 
    global content_number
    client = OpenAI()
    handler = decisionHandler(client)
    # for content in content_rankings:
    #     if content.id == content_id:
    #         next_content = content
    #         break
    next_content = content_rankings[content_number] # le back ce souvient de l'état du client c'est pas ouf
    next_content = ContentEntity(
        id=len(content_rankings),
        title=next_content.title,
        summary=next_content.summary,
        link=next_content.link,
        date=next_content.date,
        type="article",  # Default to article type
        passed=False,
        shown=False
    )
    decision_output = handler.handle_decision(user_input, next_content)
    content_number += 1
    if decision_output.sound:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_file.write(decision_output.sound)
            temp_path = temp_file.name
            
        return FileResponse(
            temp_path,
            media_type="audio/mpeg",
            background=lambda: os.unlink(temp_path)
        )
    
    return {
        "error": "No audio generated",
        "action": decision_output.decision.action
    }

@app.get("/current-track-id")
async def get_current_track_id() -> dict:
    """Get Spotify track ID from current content if it's a track"""
    # current_content = get_current_played_content()
    return {"track_id": "4xu0gZ96zx1G7UdajUGDqD"}
    # try:
    #     if current_content.type == "track" and current_content.link:
    #         track_id = get_spotify_track_id(current_content.link)
    #         return {"track_id": "4xu0gZ96zx1G7UdajUGDqD"}
    #     return {"error": "Current content is not a Spotify track"}
    # except ValueError as e:
    #     return {"error": str(e)}

def get_spotify_track_id(url: str) -> str:
    """
    Extract the track ID from a Spotify URL.
    
    Args:
        url (str): Spotify track URL in any of these formats:
            - https://open.spotify.com/track/1301WleyT98MSxVHPZCA6M
            - https://open.spotify.com/track/1301WleyT98MSxVHPZCA6M?si=12345
            - spotify:track:1301WleyT98MSxVHPZCA6M
    
    Returns:
        str: The track ID if found, otherwise raises ValueError
    """
    # if url.startswith('spotify:track:'):
    #     return url.split(':')[-1]
    
    # if 'spotify.com/track/' in url:
    #     track_part = url.split('track/')[-1]
    #     track_id = track_part.split('?')[0]
    #     track_id = track_id.rstrip('/')
    #     return track_id
    
    # raise ValueError("Invalid Spotify URL format. Must be either a Spotify URI or web URL.")

def get_current_played_content()->str:
    global content_number
    return content_rankings[content_number]



# @app.get("/youtube-summary/{video_id}")
# async def get_youtube_summary(video_id: str):
#     """Get summary of a YouTube video"""
#     return await chat_with_youtube_video(video_id)

# @app.post("/text_to_speech")
# async def generate_speech(query: QueryInput):
#     """Convert text to speech"""
#     audio_data = text_to_speech(query.text)
#     if audio_data:
#         return Response(
#             content=audio_data,
#             media_type="audio/mpeg",
#             headers={"Content-Disposition": "attachment; filename=speech.mp3"},
#         )
#     return {"error": "Failed to generate speech"}

# @app.post("/text_to_speech_stream")
# async def generate_speech_stream(query: QueryInput):
#     """Stream text to speech conversion"""
#     def audio_generator():
#         for chunk in text_to_speech_stream(query.text):
#             yield chunk

#     return StreamingResponse(
#         audio_generator(),
#         media_type="audio/mpeg",
#         headers={"Content-Disposition": "attachment; filename=speech.mp3"},
#     )

# @app.post("/speech_to_text")
# async def transcribe_speech(file: UploadFile = File(...)):
#     """Convert speech to text"""
#     try:
#         audio_data = await file.read()
#         text = speech_to_text(audio_data)
        
#         if text:
#             return {"text": text}
#         return {"error": "Failed to transcribe speech"}
#     except Exception as e:
#         return {"error": f"Error processing audio: {str(e)}"}
    
# @app.post("/workflow")
# async def handle_workflow(user_input: InputUser):
#     """Handle the AI workflow based on user input"""
#     global content_rankings
    
#     if not content_rankings:
#         await get_content()
    
#     try:
#         result = ai_workflow(content_rankings, user_input.input)
#         return {"status": "success", "result": result}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/reset")
# async def reset_content():
#     """Reset all content rankings"""
#     global content_rankings
#     content_rankings = []
#     return {"status": "success", "message": "Content rankings reset"}

# @app.post("/speech_to_text_stream")
# async def transcribe_speech_stream(file: UploadFile = File(...)):
#     try:
#         # Read the audio file
#         audio_data = await file.read()
        
#         # Return streaming response
#         return StreamingResponse(
#             speech_to_text_stream(audio_data),
#             media_type="application/json"
#         )
#     except Exception as e:
#         return {"error": f"Error processing audio: {str(e)}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)