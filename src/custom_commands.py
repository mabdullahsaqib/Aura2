# custom_commands.py
import subprocess

import google.generativeai as genai
from firebase_admin import firestore

from config import GEMINI_API_KEY
from utility import tts, recognizer

# Initialize Firestore
db = firestore.client()

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


def check_and_execute_command(command_name):
    """
    Checks if a command exists. If not, prompts user to create it,
    generates code suggestions with Gemini, and stores the command.
    """
    command_ref = db.collection("custom_commands").document(command_name)
    command_doc = command_ref.get()

    # Step 1: Check if the command exists
    if command_doc.exists:
        # Execute existing command
        command_action = command_doc.to_dict()["action"]
        subprocess.run(command_action, shell=True)
        tts.speak(f"Executed existing command '{command_name}'.")
    else:
        # Step 2: Prompt user to define new command
        tts.speak(f"The command '{command_name}' does not exist. Would you like to create it?")
        user_confirm = recognizer.listen()

        if user_confirm and "yes" in user_confirm:
            # Step 3: Get command description from the user
            tts.speak(f"Please assign a command name.")
            command_name = recognizer.listen()
            tts.speak(f"Please describe what '{command_name}' should do.")
            command_description = recognizer.listen()

            if command_description:
                try:
                    # Step 4: Pass command description to Gemini
                    gemini_response = model.generate_content(
                        "Suggest a command that can be executed in shell and perform this action: " + command_description + "\nOnly write the command and nothing else.")
                    suggested_command = gemini_response.text.strip()
                except Exception as e:
                    tts.speak(f"Error generating command suggestion: {e}")
                    return None

                # Confirm the suggested command with the user
                tts.speak(f"Suggested command: {suggested_command}")
                tts.speak("Would you like to save this command?")
                final_confirm = recognizer.listen()

                if final_confirm and "yes" in final_confirm:
                    # Step 5: Store the new command in Firestore
                    command_ref.set({
                        "action": suggested_command
                    })
                    tts.speak(f"Custom command '{command_name}' added successfully and ready for use.")
                else:
                    tts.speak("Command creation canceled.")
        else:
            tts.speak("Command creation canceled.")
