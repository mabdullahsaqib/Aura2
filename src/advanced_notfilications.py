# advanced_notifications.py
from datetime import datetime, timedelta

from firebase_admin import firestore
from plyer import notification

from utility import tts

# Firebase initialization
db = firestore.client()


def send_desktop_notification(title, message):
    """
    Sends a desktop notification to the user.
    """
    notification.notify(
        title=title,
        message=message,
        app_name="Aura",
        timeout=10  # Notification duration in seconds
    )
    print("Desktop notification sent.")
    tts.speak(f"Notification sent: {title}")


def check_and_notify_tasks():
    """
    Checks for upcoming or overdue tasks and sends notifications.
    """
    current_time = datetime.now()
    upcoming_tasks = db.collection("tasks").where("deadline", "<=", current_time + timedelta(hours=1)).stream()

    for task in upcoming_tasks:
        task_data = task.to_dict()
        title = f"Upcoming Task: {task_data['title']}"
        message = f"Deadline: {task_data['deadline']}"
        send_desktop_notification(title, message)
        tts.speak(f"You have an upcoming task: {task_data['title']} due by {task_data['deadline']}.")
