import json
import os
import datetime
import threading
import time
import config_manager

REMINDERS_FILE = os.path.join(config_manager.BASE_DATA_DIR, 'reminders.json')

def load_reminders():
    if os.path.exists(REMINDERS_FILE):
        try:
            with open(REMINDERS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_reminders(reminders):
    with open(REMINDERS_FILE, 'w') as f:
        json.dump(reminders, f, indent=4)

def add_reminder(assistant, command):
    """
    Command format: remind me to [text] at [HH:MM]
    """
    try:
        # Simple parsing for "remind me to [text] at [HH:MM]"
        if 'at' not in command:
            assistant.speak("Please specify a time using 'at HH:MM'.")
            return

        parts = command.split('at')
        time_str = parts[-1].strip()
        text_part = parts[0].replace('remind me to', '').strip()

        # Validate time format
        datetime.datetime.strptime(time_str, "%H:%M")
        
        reminders = load_reminders()
        reminders.append({
            "text": text_part,
            "time": time_str,
            "triggered": False,
            "date": str(datetime.date.today())
        })
        save_reminders(reminders)
        assistant.speak(f"Ok, I'll remind you to {text_part} at {time_str}.")
    except Exception as e:
        print(f"Error adding reminder: {e}")
        assistant.speak("I couldn't set the reminder. Please use the format: remind me to [task] at [hour:minute].")

def check_reminders(assistant):
    """
    Background check for reminders.
    """
    while assistant.is_running:
        now = datetime.datetime.now().strftime("%H:%M")
        today = str(datetime.date.today())
        reminders = load_reminders()
        updated = False

        for r in reminders:
            if r['time'] == now and not r['triggered'] and (r.get('date') == today or 'date' not in r):
                # Trigger reminder
                assistant.play_sfx('status.wav') # Small sound
                assistant.speak(f"Reminder: {r['text']}")
                r['triggered'] = True
                updated = True
        
        if updated:
            save_reminders(reminders)
            
        # Wait until next minute
        time.sleep(30)

def list_reminders(assistant, command=None):
    reminders = load_reminders()
    if not reminders:
        assistant.speak("You have no reminders.")
        return
    
    msg = "Your reminders are: "
    for r in reminders:
        status = " (done)" if r['triggered'] else ""
        msg += f"{r['text']} at {r['time']}{status}. "
    assistant.speak(msg)

def clear_reminders(assistant, command=None):
    save_reminders([])
    assistant.speak("All reminders cleared.")
