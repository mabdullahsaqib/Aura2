# note_taking.py
from datetime import datetime

import google.generativeai as genai
from firebase_admin import firestore

from config import GEMINI_API_KEY
from utility import tts, recognizer

# Initialize Firestore
db = firestore.client()

# Initialize Gemini model
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-exp")


def get_next_note_id():
    """
    Retrieve and increment the note ID from a dedicated counter document in Firestore.
    """
    counter_ref = db.collection("metadata").document("note_counter")
    counter_doc = counter_ref.get()
    current_id = counter_doc.to_dict().get("count", 0) if counter_doc.exists else 0
    next_id = current_id + 1
    counter_ref.set({"count": next_id})  # Update the counter in Firestore
    return next_id  # Use plain numeric ID


def add_note(title, content, tags=None):
    """
    Adds a note to Firestore with a title, optional tags, and a timestamp.

    Parameters:
        title (str): The title of the note.
        content (str): The content of the note.
        tags (list of str): Optional tags for the note.
    """
    note_id = get_next_note_id()
    note_ref = db.collection("notes").document(str(note_id))
    note_data = {
        "note_id": note_ref.id,
        "title": title,
        "content": content,
        "timestamp": datetime.now(),
        "tags": tags if tags else []
    }
    note_ref.set(note_data)
    print("Note added successfully!")
    tts.speak("Note added successfully.")


def retrieve_notes(note_id=None, keyword=None, tag=None, date_range=None):
    """
    Retrieves notes based on a keyword, tag, or date range.

    Parameters:
        keyword (str): Keyword to search within note content.
        tag (str): Tag to filter notes.
        date_range (tuple of datetime): Start and end date for filtering notes.

    Returns:
        list: List of notes matching the criteria.
    """
    query = db.collection("notes")

    if note_id:
        query = query.where("note_id", "==", note_id)
        return [note.to_dict() for note in query.stream()]

    if tag:
        query = query.where("tags", "array_contains", tag)
    if date_range:
        start_date, end_date = date_range
        query = query.where("timestamp", ">=", start_date).where("timestamp", "<=", end_date)

    notes = [note.to_dict() for note in query.stream()]

    if keyword:
        notes = [note for note in notes if keyword.lower() in note["content"].lower()]

    return notes


def retrieve_all_notes():
    """
    Retrieves and displays all notes by their IDs and titles.

    Returns:
        list: A list of dictionaries containing note IDs and titles.
    """
    notes = db.collection("notes").stream()
    all_notes = [note.to_dict() for note in notes]

    print("\nAll Notes:")
    for note in all_notes:
        print(f"Note ID: {note['note_id']}, Title: {note['title']}, Tags: {note['tags']}, Content: {note['content']}")

    return all_notes


def summarize_note(note_content):
    """
    Summarizes a single note's content using Gemini.

    Parameters:
        note_content (str): The content of the note to summarize.

    Returns:
        str: Summary of the note.
    """
    response = model.generate_content("Summarize the following text: " + note_content)
    return response.text


def delete_note(note_id):
    """
    Deletes a note by note_id.

    Parameters:
        note_id (str): ID of the note to delete.
    """
    db.collection("notes").document(note_id).delete()
    print("Note deleted successfully!")
    tts.speak("Note deleted successfully.")


def edit_note(note_id, new_title=None, new_content=None, new_tags=None):
    """
    Edits a note's title, content, or tags.

    Parameters:
        note_id (str): ID of the note to edit.
        new_title (str): New title to replace the old title.
        new_content (str): New content to replace the old content.
        new_tags (list of str): New tags to replace the old tags.
    """
    note_ref = db.collection("notes").document(note_id)
    update_data = {}
    if new_title:
        update_data["title"] = new_title
    if new_content:
        update_data["content"] = new_content
    if new_tags is not None:
        update_data["tags"] = new_tags

    note_ref.update(update_data)
    print("Note updated successfully!")
    tts.speak("Note updated successfully.")


# Voice Interaction
def note_voice_interaction(choice):
    if "add" in choice or "create" in choice or "new" in choice or "make" in choice or "write" in choice or "record" in choice or "take" in choice:
        tts.speak("Please say the note title.")
        title = recognizer.listen()
        tts.speak("Please say the note content.")
        content = recognizer.listen()
        tts.speak("Would you like to add tags? Say yes or no.")
        if "yes" in recognizer.listen().lower():
            tts.speak("Please say the tags, separated by commas.")
            tags = recognizer.listen().split(",")
        else:
            tags = None
        add_note(title, content, tags)

    elif ("retrieve" in choice or "get" in choice) and "all" not in choice:
        tts.speak("Please say the note ID to retrieve or leave blank.")
        note_id = recognizer.listen() or None
        if "blank" in note_id.lower():
            note_id = None
        tts.speak("Please say a keyword or leave blank.")
        keyword = recognizer.listen() or None
        if "blank" in keyword.lower():
            keyword = None
        tts.speak("Please say a tag to filter by, or leave blank.")
        tag = recognizer.listen() or None
        if "blank" in tag.lower():
            tag = None
        notes = retrieve_notes(note_id=note_id, keyword=keyword, tag=tag)
        tts.speak("Notes retrieved. Check the console for details.")
        for note in notes:
            print(f"Note ID: {note['note_id']}, Title: {note['title']}, Content: {note['content']}")

    elif "retrieve all" in choice or "all notes" in choice or "all" in choice or "get" in choice:
        notes = retrieve_all_notes()
        tts.speak("All notes retrieved. Check the console for details.")
        for note in notes:
            print(f"Note ID: {note['note_id']}, Title: {note['title']}")

    elif "summarize" in choice or "summary" in choice:
        tts.speak("Please say the note ID to summarize.")
        note_id = recognizer.listen()
        note = db.collection("notes").document(note_id).get()
        if note.exists:
            summary = summarize_note(note.to_dict()["content"])
            tts.speak("Note summarized. Check the console for details.")
            print(f"Summary: {summary}")
        else:
            tts.speak("Note not found.")

    elif "delete" in choice or "remove" in choice or "erase" in choice or "clear" in choice:
        tts.speak("Please say the note ID to delete.")
        note_id = recognizer.listen()
        delete_note(note_id)

    elif "edit" in choice or "update" in choice or "change" in choice or "modify" in choice:
        tts.speak("Please say the note ID to edit.")
        note_id = recognizer.listen()
        tts.speak("Please say the new title or say 'skip' to leave unchanged.")
        new_title = recognizer.listen()
        if "skip" in new_title.lower():
            new_title = None
        tts.speak("Please say the new content or say 'skip' to leave unchanged.")
        new_content = recognizer.listen()
        if "skip" in new_content.lower():
            new_content = None
        tts.speak("Would you like to update tags? Say yes or no.")
        if "yes" in recognizer.listen().lower():
            tts.speak("Please say the new tags, separated by commas.")
            new_tags = recognizer.listen().split(",")
        else:
            new_tags = None
        edit_note(note_id, new_title, new_content, new_tags)

    else:
        tts.speak("Option not recognized, please try again.")
