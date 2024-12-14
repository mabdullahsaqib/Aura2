import pyaudio
from openai import OpenAI
import dotenv
import os

dotenv.load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

p = pyaudio.PyAudio()
stream = p.open(format=8,
                channels=1,
                rate=24_000,
                output=True)

with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="shimmer",
        input="""I see skies of blue and clouds of white
             The bright blessed days, the dark sacred nights
             And I think to myself
             What a wonderful world""",
        response_format="pcm"
) as response:
    for chunk in response.iter_bytes(1024):
        stream.write(chunk)

