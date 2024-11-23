import requests
import json

BASE_URL = "http://localhost:8000"

def test_root():
    response = requests.get(f"{BASE_URL}/")
    print("Root endpoint:", response.json())

def test_content():
    response = requests.get(f"{BASE_URL}/content")
    if response.headers.get('content-type') == 'audio/mpeg':
        # Save the audio response
        with open("content_audio.mp3", "wb") as f:
            f.write(response.content)
        print("Content endpoint: Audio saved as content_audio.mp3")
    else:
        print("Content endpoint:", response.json())

# def test_text_to_speech():
#     data = {"text": "Hello, this is a test message"}
#     response = requests.post(f"{BASE_URL}/text_to_speech", json=data)
#     print("Text-to-speech response:", response.headers)
#     print("Text-to-speech content:", response.content)
#     if response.headers.get('content-type') == 'audio/mpeg':
#         # Save the audio file
#         with open("output.mp3", "wb") as f:
#             f.write(response.content)
#         print("Text-to-speech: Audio file saved as output.mp3")
#     else:
#         print("Text-to-speech error:", response.json())

# def test_speech_to_text():
#     # Make sure you have a test audio file
#     try:
#         with open("output.mp3", "rb") as audio_file:
#             files = {"file": ("output.mp3", audio_file, "audio/mpeg")}
#             response = requests.post(f"{BASE_URL}/speech_to_text", files=files)
#             print("Speech-to-text:", response.json())
#     except FileNotFoundError:
#         print("Please provide a test_audio.mp3 file for speech-to-text testing")

def test_get_decision():
    # First get content to get valid content_id
    content_response = requests.get(f"{BASE_URL}/content")
    if not isinstance(content_response.json(), dict) or 'content' not in content_response.json():
        print("Error: Could not fetch content for testing decisions")
        return
        
    content_id = content_response.json()['content'][0]['id']  # Get first content's ID
    
    # Test different types of user inputs
    test_inputs = [
        "next please",
        "can you summarize this",
        "play this",
        "random gibberish"
    ]
    
    for user_input in test_inputs:
        print(f"\nTesting decision with input: '{user_input}'")
        response = requests.get(f"{BASE_URL}/get-decision/{user_input}/{content_id}")
        
        # Check if response is audio or decision
        if response.headers.get('content-type') == 'audio/mpeg':
            # Save the audio file with a unique name
            filename = f"decision_output_{user_input.replace(' ', '_')}.mp3"
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Get-decision: Audio file saved as {filename}")
        else:
            print("Get-decision response:", response.json())

if __name__ == "__main__":
    print("Testing API endpoints...")
    test_root()
    test_content()
    # test_text_to_speech()
    # test_speech_to_text()
    test_get_decision()