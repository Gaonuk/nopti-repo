from typing import Optional
from elevenlabs.client import ElevenLabs
import os
from pathlib import Path


def text_to_speech(text: str) -> Optional[bytes]:
    # Initialize client with API key from environment variables
    client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

    try:
        # Generate audio using the client without streaming
        audio = client.generate(
            text=text, voice="Jessica", model="eleven_multilingual_v2", stream=False
        )

        if not audio:
            print("No audio generated")
            return None

        # Convert generator to bytes if needed
        if hasattr(audio, "__iter__"):
            return b"".join(audio)

        return audio

    except Exception as e:
        print(f"Error generating speech: {str(e)}")
        return None


# def text_to_speech_stream(text):
#     """Generator version of text_to_speech that yields chunks"""
#     client = ElevenLabs(
#         api_key=os.getenv("ELEVENLABS_API_KEY")
#     )

#     try:
#         # Generate audio stream
#         audio_stream = client.generate(
#             text=text,
#             voice="Josh",
#             model="eleven_multilingual_v2",
#             stream=True
#         )

#         if not audio_stream:
#             print("No audio stream generated")
#             return None

#         # Yield each chunk as it becomes available
#         for chunk in audio_stream:
#             if chunk:
#                 yield chunk


def load_sound_effect(filename: str) -> Optional[bytes]:
    """
    Load an MP3 file and return it as bytes.

    Args:
        filename: Name of the sound file (with or without .mp3 extension)

    Returns:
        Optional[bytes]: Audio data as bytes, or None if loading fails
    """
    try:
        # Ensure the filename has .mp3 extension
        if not filename.endswith(".mp3"):
            filename += ".mp3"

        # Construct path to sound effects directory
        sound_dir = Path(__file__).parent / "sound_effects"
        file_path = sound_dir / filename

        # Read the audio file
        with open(file_path, "rb") as f:
            return f.read()

    except Exception as e:
        print(f"Error loading sound effect: {str(e)}")
        return None
