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

def create_command_ai(assistant, command):
    import ai_manager
    import json

    prompt = (
        f"The user wants to create a custom voice command.\n"
        f"User request: {command}\n\n"
        "Extract these fields from the request:\n"
        "1. command_name: the trigger word(s) the user will say (lowercase, underscores for spaces)\n"
        "2. type: \"exe\" for running a program, \"shell\" for a shell command, \"port\" for opening a network port\n"
        "3. For type \"exe\" -> field \"path\": full path to the executable\n"
        "4. For type \"shell\" -> field \"command\": the shell command to run\n"
        "5. For type \"port\" -> field \"port\": port number\n\n"
        "Reply ONLY with valid JSON. Examples:\n"
        '{"command_name": "run_chrome", "type": "exe", "path": "C:\\\\Program Files\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe"}\n'
        '{"command_name": "ipconfig", "type": "shell", "command": "ipconfig /all"}\n'
        '{"command_name": "open_port_8080", "type": "port", "port": "8080"}\n\n'
        'If you cannot determine the details, reply with {"error": "what is missing"}'
    )

    response = ai_manager.get_ai_response(prompt, assistant)
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        if start == -1 or end <= start:
            assistant.speak("Sorry, I had trouble understanding the request.")
            return
        data = json.loads(response[start:end])
        if 'error' in data:
            assistant.speak(f"I need more information: {data['error']}")
            return
        cmd_name = data.get('command_name', '').lower().strip()
        cmd_type = data.get('type', 'shell')
        if not cmd_name:
            assistant.speak("I couldn't figure out the command name.")
            return
        if cmd_type == 'exe':
            path = data.get('path', '')
            if not path:
                assistant.speak("I need the path to the executable.")
                return
            config_manager.save_custom_command(cmd_name, {'type': 'exe', 'path': path})
            assistant.speak(f"Created command '{cmd_name}' to run {path}")
            subprocess.Popen(path)
        elif cmd_type == 'shell':
            shell_cmd = data.get('command', '')
            if not shell_cmd:
                assistant.speak("I need a shell command to run.")
                return
            config_manager.save_custom_command(cmd_name, {'type': 'shell', 'command': shell_cmd})
            assistant.speak(f"Created command '{cmd_name}' to run {shell_cmd}")
            os.system(shell_cmd)
        elif cmd_type == 'port':
            port = data.get('port', '')
            if not port:
                assistant.speak("I need a port number.")
                return
            config_manager.save_custom_command(cmd_name, {'type': 'port', 'port': port})
            assistant.speak(f"Created command '{cmd_name}' to open port {port}")
    except Exception as e:
        assistant.speak(f"Sorry, I couldn't create that command: {e}")

def _open_port(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', int(port)))
    s.listen(1)
    print(f"Port {port} opened.")
    s.accept()
