# utility.py

import pyaudio
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Load OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API key in environment variables.")

client = OpenAI(api_key=OPENAI_API_KEY)

# Centralized text-to-speech
class TextToSpeech:
    def __init__(self):
        self.stream = self._initialize_audio_stream()

    def _initialize_audio_stream(self):
        p = pyaudio.PyAudio()
        return p.open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)

    def speak(self, text):
        with client.audio.speech.with_streaming_response.create(
            model="tts-1", voice="shimmer", input=text, response_format="pcm"
        ) as response:
            for chunk in response.iter_bytes(1024):
                self.stream.write(chunk)

# Centralized speech recognition
class SpeechRecognizer:
    def __init__(self):
        import speech_recognition as sr
        self.recognizer = sr.Recognizer()

    def listen(self):
        import speech_recognition as sr

        with sr.Microphone() as source:
            print("Listening...")
            while True:
                try:
                    audio = self.recognizer.listen(source)
                    command = self.recognizer.recognize_google(audio)
                    print("Command:", command)
                    return command
                except sr.UnknownValueError:
                    print("Sorry, I didn't catch that. Please try again.")
                except sr.RequestError:
                    print("Voice service unavailable. Please try later.")
                    return ""

# Singleton instances
tts = TextToSpeech()
recognizer = SpeechRecognizer()
