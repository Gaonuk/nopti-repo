from fastapi import FastAPI, Response, UploadFile, File
import uvicorn
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from scraper.get_updated_news import get_update_news
from scraper.youtubeToSummary import chat_with_youtube_video
from speech.text_to_speech import text_to_speech, text_to_speech_stream
from speech.speech_to_text import speech_to_text

app = FastAPI()


class QueryInput(BaseModel):
    text: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/content")
def get_content():
    return get_update_news()


@app.get("/youtube-summary/{video_id}")
def get_youtube_summary(video_id: str):
    return chat_with_youtube_video(video_id)


@app.post("/text_to_speech")
async def generate_speech(query: QueryInput):
    audio_data = text_to_speech(query.text)
    if audio_data:
        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"},
        )
    return {"error": "Failed to generate speech"}


@app.post("/text_to_speech_stream")
async def generate_speech_stream(query: QueryInput):
    def audio_generator():
        for chunk in text_to_speech_stream(query.text):
            yield chunk

    return StreamingResponse(
        audio_generator(),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "attachment; filename=speech.mp3"},
    )


@app.post("/speech_to_text")
async def transcribe_speech(file: UploadFile = File(...)):
    try:
        # Read the audio file
        audio_data = await file.read()

        # Process the audio data
        text = speech_to_text(audio_data)

        if text:
            return {"text": text}
        return {"error": "Failed to transcribe speech"}
    except Exception as e:
        return {"error": f"Error processing audio: {str(e)}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
