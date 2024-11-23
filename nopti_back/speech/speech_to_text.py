from openai import OpenAI
import os

def speech_to_text(audio_data):
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    try:
        # Create a temporary file to store the audio data
        with open("temp_audio.mp3", "wb") as audio_file:
            audio_file.write(audio_data)
        
        # Open the audio file and transcribe it
        with open("temp_audio.mp3", "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        # Clean up the temporary file
        os.remove("temp_audio.mp3")
        
        return transcript.text
    except Exception as e:
        print(f"Error transcribing speech: {str(e)}")
        if os.path.exists("temp_audio.mp3"):
            os.remove("temp_audio.mp3")
        return None
