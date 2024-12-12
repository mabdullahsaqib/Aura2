import os

from dotenv import load_dotenv

load_dotenv()

# Firebase configuration
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")

# Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Google Custom Search API configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# Gmail API configuration
GMAIL_CREDENTIALS_PATH = os.getenv("GMAIL_CREDENTIALS_PATH")
GMAIL_TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH")

# News API key
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Weather API configuration
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_HOST = os.getenv("WEATHER_API_HOST")

# Spotify API configuration
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

# YouTube API key
YOUTUBE_API_KEY = "AIzaSyA36ThEAdtps37rX_0miWSc_OWDnPtS_Xo"
