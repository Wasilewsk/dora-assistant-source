# skills/information.py
import datetime

def tell_time(assistant, command=None):
    """Tells the current time to the user."""
    now = datetime.datetime.now()
    
    # English format (12-hour, AM/PM)
    hour_12_str = now.strftime("%I")
    # strftime returns '01' for 1 o'clock, .lstrip('0') removes the leading zero
    hour_12 = hour_12_str.lstrip('0') if hour_12_str.startswith('0') else hour_12_str
    minute = now.strftime("%M")
    ampm = now.strftime("%p")
    
    # Read the format from the language file
    assistant.speak(assistant.get_response('time_is', username=assistant.username, hour_12=hour_12, minute=minute, ampm=ampm))