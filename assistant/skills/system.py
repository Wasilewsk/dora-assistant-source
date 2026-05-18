# skills/system.py

import os

def shutdown_computer(assistant, command):
    """Shuts down the computer after confirmation."""
    assistant.speak(assistant.get_response('shutdown_confirm'))
    
    confirmation = assistant.listen()
    
    if 'yes' in confirmation:
        assistant.speak(assistant.get_response('shutdown_initiated'))
        os.system("shutdown /s /t 10")
    else:
        assistant.speak(assistant.get_response('action_cancelled'))

def restart_computer(assistant, command):
    """Restarts the computer after confirmation."""
    assistant.speak(assistant.get_response('restart_confirm'))

    confirmation = assistant.listen()
    
    if 'yes' in confirmation:
        assistant.speak(assistant.get_response('restart_initiated'))
        os.system("shutdown /r /t 10")
    else:
        assistant.speak(assistant.get_response('action_cancelled'))

def cancel_shutdown(assistant, command):
    """Cancels the shutdown or restart."""
    assistant.speak(assistant.get_response('shutdown_cancelled'))
    os.system("shutdown /a")

def get_battery_status(assistant, command=None):
    """Reports the battery percentage and charging status."""
    try:
        import psutil
        battery = psutil.sensors_battery()
        if battery is None:
            assistant.speak("I couldn't find a battery on this system.")
            return

        percent = battery.percent
        is_charging = battery.power_plugged

        status = "charging" if is_charging else "not charging"
        if percent == 100 and is_charging:
            status = "fully charged"

        message = f"Your battery is at {percent} percent and is currently {status}."
        assistant.speak(message)
    except Exception as e:
        print(f"Error getting battery status: {e}")
        assistant.speak("Sorry, I encountered an error while checking the battery status.")

def open_application(assistant, command):
    """Opens a specified application (e.g., Google Chrome)."""
    app_map = {
        'google chrome': 'chrome.exe',
        'chrome': 'chrome.exe',
        'firefox': 'firefox.exe',
        'notepad': 'notepad.exe',
        'calculator': 'calc.exe',
        'edge': 'msedge.exe',
        'vlc': 'vlc.exe',
        'discord': 'discord.exe'
    }
    
    # Extract app name from command
    # Examples: "open google chrome", "start chrome", "launch notepad"
    clean_command = command.lower().replace('open', '').replace('start', '').replace('launch', '').strip()
    
    if clean_command in app_map:
        app_to_run = app_map[clean_command]
        assistant.speak(f"Opening {clean_command}.")
        os.system(f"start {app_to_run}")
    else:
        # Try to run it directly if it's not in the map
        assistant.speak(f"Attempting to open {clean_command}.")
        # Use 'start' to run it in the background/not block
        os.system(f'start "" "{clean_command}"')
