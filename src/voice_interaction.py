import random
import time

import firebase_admin
from firebase_admin import credentials

from config import FIREBASE_CREDENTIALS_PATH
from utility import tts, recognizer

# Firebase initialization
cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)

# Import all the modules as needed
from interaction_history import interaction_history, handle_user_command
from task_management import task_voice_interaction
from web_browsing import web_browsing_voice_interaction
from note_taking import note_voice_interaction
from custom_commands import check_and_execute_command
from realtime_translation import translation_voice_interaction
from email_management import email_voice_interaction
from weather_and_news import weather_and_news_voice_interaction
from personalized_recommendations import recommendations_voice_interaction
from entertainment_controls import entertainment_control_voice_interaction
from meeting_summaries import meeting_summary_voice_interaction
from advanced_notfilications import check_and_notify_tasks

# Initialize chat history
session_id, chat = interaction_history()

# Constants
INACTIVITY_THRESHOLD = 1800  # 30 minutes in seconds
Entertainment_Commands = ["play", "pause", "stop", "resume", "skip", "next", "previous", "shuffle", "repeat", "look",
                          "volume up",
                          "volume down", "increase", "decrease", "seek", "jump"]


def activate_module(command):
    """
    Activate the appropriate module based on the user's command.
    """

    if "task" in command or "reminder" in command or "schedule" in command or "to-do" in command or "tasks" in command:
        task_voice_interaction(command)
    elif "web" in command or "search" in command or "browse" in command and "youtube" not in command:
        web_browsing_voice_interaction(command)
    elif ("note" in command or "notes" in command or "record" in command or "write" in command) and "notepad" not in command and "email" not in command and "mail" not in command:
        note_voice_interaction(command)
    elif "translation" in command or "translate" in command or "interpret" in command:
        translation_voice_interaction()
    elif "email" in command or "mail" in command or "inbox" in command:
        email_voice_interaction(command)
    elif "weather" in command or "news" in command or "headline" in command or "article" in command:
        weather_and_news_voice_interaction(command)
    elif "recommendation" in command or "suggestion" in command or "advice" in command or "recommendations" in command or "recommend" in command:
        recommendations_voice_interaction(command)
    elif "entertainment" in command or "music" in command or "video" in command or "movie" in command or "spotify" in command or "youtube" in command or any(
            cmd in command for cmd in Entertainment_Commands):
        entertainment_control_voice_interaction(command)
    elif "meeting" in command or "summary" in command or "transcript" in command or "transcribe" in command:
        meeting_summary_voice_interaction(command)
    elif "custom" in command or "execute" in command or "run" in command or "perform" in command or "open" in command or "launch" in command or "start" in command:
        check_and_execute_command(command)
    else:
        response = handle_user_command(session_id, command, chat)
        print(response)
        tts.speak(response)


def main():
    """
    Main function to handle voice commands and activate modules.
    """
    greetings = ["Hello, how can I assist you today?", "Hi, what can I do for you?", "Hey, how can I help you?",
                 "Greetings, what can I do for you?", "Hello, how can I help you today?"]
    goodbyes = ["See you later!", "Goodbye, have a great day!", "Goodbye, take care!", "Goodbye, see you soon!",
                "Goodbye, have a nice day!"]
    tts.speak(random.choice(greetings))

    # Track last command time
    last_command_time = time.time()

    while True:
        # Check inactivity
        if time.time() - last_command_time >= INACTIVITY_THRESHOLD:
            check_and_notify_tasks()
            # Reset timer after notification
            last_command_time = time.time()

        command = recognizer.listen()
        if "exit" in command.lower():
            tts.speak(random.choice(goodbyes))
            break
        activate_module(command.lower())


if __name__ == "__main__":
    main()


