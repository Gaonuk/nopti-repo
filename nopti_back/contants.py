from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get OPENAI_API_KEY from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
