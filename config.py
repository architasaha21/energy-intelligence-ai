import os

from dotenv import load_dotenv


# Load variables from the .env file
load_dotenv()


# Base URL of Member 1's ML forecasting API
ML_API_URL = os.getenv(
    "ML_API_URL",
    "http://127.0.0.1:8000"
)


# Groq API key used by our AI agents
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# Groq model used for analysis and recommendations
GROQ_MODEL = "openai/gpt-oss-120b"