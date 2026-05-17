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