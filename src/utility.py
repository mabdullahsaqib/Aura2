# utility.py

import pyaudio
import speech_recognition as sr
from openai import OpenAI

from config import OPENAI_API_KEY

# Load OpenAI API key
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
    recognizer = None

    def __init__(self):
        self.recognizer = sr.Recognizer()

    def listen(self):

        with sr.Microphone() as source:
            while True:
                print("Listening...")
                try:
                    audio = self.recognizer.listen(source)
                    command = self.recognizer.recognize_google(audio)
                    print(f"Command: {command}")
                    return command
                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    print(f"Error: {e}")
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    print(f"Error: {e}")


# Singleton instances
tts = TextToSpeech()
recognizer = SpeechRecognizer()
