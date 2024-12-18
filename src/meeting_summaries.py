# meeting_summaries.py
import os
from pathlib import Path
from firebase_admin import firestore
import google.generativeai as genai
import whisper
from utility import tts, recognizer
from config import GEMINI_API_KEY

# Initialize Firestore
db = firestore.client()

# Initialize GEMINI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize Whisper Model
def load_model():
    whisper_model = whisper.load_model("base")
    return whisper_model

# Transcribe Audio Function
def transcribe_audio(whisper_model, file_path):
    result = whisper_model.transcribe(file_path)
    transcript = result['text']
    print("Transcript :", transcript)
    return transcript

# Summarize Transcript with GEMINI
def summarize_text(text):
    response = model.generate_content("Summarize the following meeting transcript, briefly: " + text)
    print("Summary :", response.text)
    return response.text

# Store Meeting Summary in Firestore
def store_summary(meeting_title, transcript, summary):
    doc_ref = db.collection("meeting_summaries").document(meeting_title)
    doc_ref.set({
        "title": meeting_title,
        "transcript": transcript,
        "summary": summary
    })
    print(f"Meeting '{meeting_title}' summary saved successfully.")
    tts.speak(f"Meeting summary for '{meeting_title}' has been saved successfully.")

# Main Function to Transcribe, Summarize, and Store
def process_meeting_summary(file_path, meeting_title):
    whisper_model = load_model()
    print("Transcribing audio...")
    transcript = transcribe_audio(whisper_model, file_path)
    print("Transcription complete. Summarizing text...")
    try:
        summary = summarize_text(transcript)
        print("Summary complete. Storing in Firestore...")
        store_summary(meeting_title, transcript, summary)
        with open(f"{meeting_title}_summary.txt", "w") as file:
            file.write("Summary : " + summary)
        print(f"Meeting summary for '{meeting_title}' processed and stored.")
        tts.speak("The meeting summary has been processed and stored successfully.")
    except Exception as e:
        print(f"Error occurred: {e}")
        tts.speak("An error occurred while processing the meeting summary. Please try again.")

# Search for File by Name
def findfile(name, path):
    """Searches for a file by name in a specified base directory."""
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            if Path(filename).stem.lower() == name:
                return Path(dirpath) / filename

    print(f"File '{name}' not found in '{path}'.")
    return None

# Retrieve Meeting Summaries
def getmeetings():
    meetings = db.collection("meeting_summaries").stream()
    for meeting in meetings:
        print(meeting.to_dict())
    tts.speak("All meeting summaries have been retrieved. Check the console for details.")

# Retrieve Specific Meeting Summary
def retrieve_a_meeting(title):
    doc_ref = db.collection("meeting_summaries").document(title)
    doc = doc_ref.get()
    if doc.exists:
        print(doc.to_dict())
        tts.speak(f"Meeting summary for '{title}' has been retrieved. Check the console for details.")
    else:
        print(f"Meeting '{title}' not found in Firestore.")
        tts.speak(f"Meeting '{title}' was not found.")

# Voice Interaction
def meeting_summary_voice_interaction(command):
    """
    Handles the meeting summary command.
    Asks user for the audio file and processes the meeting summary.
    """
    if "list" in command or "all" in command:
        tts.speak("Retrieving all meeting summaries from Firestore.")
        getmeetings()
        return
    elif "retrieve" in command or "get" in command:
        tts.speak("Please provide the title of the meeting summary you would like to retrieve.")
        title = recognizer.listen()
        retrieve_a_meeting(title)
        return
    else:
        tts.speak("What's the name of the audio file?")
        audio_file = recognizer.listen()
        audio_file_path = findfile(audio_file, "C:/Meetings")
        if audio_file_path:
            tts.speak(f"Processing the meeting summary from the file located at {audio_file_path}.")
            title = Path(audio_file_path).stem
            process_meeting_summary(str(audio_file_path), title)
        else:
            tts.speak("Sorry, I couldn't find the specified audio file. Please try again.")