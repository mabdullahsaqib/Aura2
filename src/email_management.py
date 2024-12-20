# email_management.py
import base64
import os
from email.mime.text import MIMEText

import google.generativeai as genai
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import GEMINI_API_KEY, GMAIL_CREDENTIALS_PATH, GMAIL_TOKEN_PATH
from utility import tts, recognizer

# Initialize Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Define the Gmail API scope
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.modify']


def authenticate_gmail():
    creds = None
    if os.path.exists(GMAIL_TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(GMAIL_TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(GMAIL_CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(GMAIL_TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    return creds


def fetch_emails(service, max_results=5):
    try:
        results = service.users().messages().list(userId='me', maxResults=max_results).execute()
        messages = results.get('messages', [])

        if not messages:
            tts.speak("No messages found in your inbox.")
            return

        for msg in messages:
            message = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = {header['name']: header['value'] for header in message['payload']['headers']}
            sender = headers.get("From", "Unknown Sender")
            subject = headers.get("Subject", "No Subject")
            snippet = message['snippet']

            print(f"From: {sender}")
            print(f"Subject: {subject}")
            print(f"Snippet: {snippet}")
            tts.speak(f"Email from {sender}, subject: {subject}")

    except HttpError as error:
        print(f"An error occurred: {error}")
        tts.speak("Failed to fetch emails. Please try again later.")


def send_email(service, to_email, subject, message_text):
    try:
        message = MIMEText(message_text)
        message['To'] = to_email
        message['Subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        send_message = {'raw': raw_message}
        sent_message = service.users().messages().send(userId='me', body=send_message).execute()
        print(f"Message sent! Id: {sent_message['id']}")
        tts.speak("Your email has been sent successfully.")
    except HttpError as error:
        print(f"An error occurred: {error}")
        tts.speak("Failed to send the email. Please try again later.")


def summarize_email(service, email_id):
    try:
        message = service.users().messages().get(userId='me', id=email_id).execute()
        snippet = message['snippet']

        # Summarize the email content using Gemini
        summary = model.generate_content(f"Summarize this email: {snippet}")
        print("Summary:", summary.text)
        tts.speak(f"Summary of the email: {summary.text}")

    except HttpError as error:
        print(f"An error occurred: {error}")
        tts.speak("Failed to summarize the email. Please try again later.")


def send_email_with_generated_response(service, email_id):
    try:
        message = service.users().messages().get(userId='me', id=email_id).execute()
        snippet = message['snippet']

        # Generate response using Gemini
        response = model.generate_content("Reply to this email: " + snippet)
        print("Generated Response:", response.text)

        # Extract sender's email and relevant headers to reply
        headers = {header['name']: header['value'] for header in message['payload']['headers']}
        sender_email = headers.get("From")
        subject = headers.get("Subject", "No Subject")
        message_id = headers.get("Message-ID")

        # Create a MIME message with reply headers
        reply_message = MIMEText(response.text)
        reply_message['To'] = sender_email
        reply_message['Subject'] = "Re: " + subject
        if message_id:
            reply_message['In-Reply-To'] = message_id
            reply_message['References'] = message_id

        raw_message = base64.urlsafe_b64encode(reply_message.as_bytes()).decode()

        send_message = {'raw': raw_message}
        sent_message = service.users().messages().send(userId='me', body=send_message).execute()
        print(f"Reply sent! Id: {sent_message['id']}")
        tts.speak("Your reply has been sent successfully.")

    except HttpError as error:
        print(f"An error occurred: {error}")
        tts.speak("Failed to send the reply. Please try again later.")



# Voice Interaction
def email_voice_interaction(command):
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)

    if "fetch" in command or "emails" in command or "mails" in command or "inbox" in command:
        fetch_emails(service, 10)
    elif ("send" in command or "compose" in command or "write" in command) and (
            "email" in command or "mail" in command):
        tts.speak("Who is the recipient?")
        to_email = recognizer.listen()
        tts.speak("What is the subject?")
        subject = recognizer.listen()
        tts.speak("What should I say?")
        message_text = recognizer.listen()
        send_email(service, to_email, subject, message_text)
    elif "summarize" in command and ("email" in command or "mail" in command):
        tts.speak("What is the email ID?")
        email_id = recognizer.listen()
        summarize_email(service, email_id)
    elif "reply" in command and ("email" in command or "mail" in command):
        tts.speak("What is the email ID?")
        email_id = recognizer.listen()
        send_email_with_generated_response(service, email_id)

if __name__ == "__main__":
    email_voice_interaction("fetch emails")