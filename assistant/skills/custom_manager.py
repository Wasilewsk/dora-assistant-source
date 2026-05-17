import config_manager
import subprocess
import socket
import threading
import os

def add_note(assistant, command):
    note = command.replace("add note", "").strip()
    config_manager.save_note(note)
    assistant.speak(f"Note saved: {note}")

def list_notes(assistant, command=None):
    notes = config_manager.load_notes()
    if not notes:
        assistant.speak("You have no notes.")
    else:
        assistant.speak("Your notes are: " + ". ".join(notes))

def delete_notes(assistant, command=None):
    if os.path.exists(config_manager.NOTES_FILE):
        os.remove(config_manager.NOTES_FILE)
        assistant.speak("All notes have been deleted.")
    else:
        assistant.speak("You have no notes to delete.")

def run_custom_command(assistant, command):
    cmds = config_manager.load_custom_commands()
    cmd_name = command.strip()
    if cmd_name in cmds:
        info = cmds[cmd_name]
        if info['type'] == 'exe':
            subprocess.Popen(info['path'])
        elif info['type'] == 'shell':
            os.system(info['command'])
        elif info['type'] == 'port':
            threading.Thread(target=_open_port, args=(info['port'],), daemon=True).start()
        assistant.speak(f"Running custom command {cmd_name}")
    else:
        assistant.speak("Custom command not found.")

def _open_port(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', int(port)))
    s.listen(1)
    print(f"Port {port} opened.")
    s.accept()
