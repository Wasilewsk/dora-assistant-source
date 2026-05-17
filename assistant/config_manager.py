# config_manager.py (updated with paths)
import configparser
import json
import os

BASE_CONF_DIR = os.path.join(os.path.expanduser("~"), ".assistantconf")
BASE_DATA_DIR = os.path.join(os.path.expanduser("~"), ".assistant-data")
CUSTOM_CMDS_FILE = os.path.join(os.path.expanduser("~"), ".assistant-custom-commands.json")

# Ensure directories exist
for d in [BASE_CONF_DIR, BASE_DATA_DIR]:
    if not os.path.exists(d): os.makedirs(d)

CONFIG_FILE = os.path.join(BASE_CONF_DIR, 'config.ini')
SETTINGS_FILE = os.path.join(BASE_CONF_DIR, 'settings.json')
NOTES_FILE = os.path.join(BASE_DATA_DIR, 'notes.json')

def load_settings():
    """Loads user settings (language, chatbot model, username)."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Error while loading settings: {e}. Using default settings.")
    return {'last_lang': 'en', 'chatbot_model': 1, 'username': 'User'}

def get_notes_pin():
    settings = load_settings()
    return settings.get('notes_pin', None)

def set_notes_pin(pin):
    settings = load_settings()
    settings['notes_pin'] = pin
    save_settings(settings)


def load_notes():
    if os.path.exists(NOTES_FILE):
        try:
            with open(NOTES_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except Exception: return []
    return []

def save_note(note):
    notes = load_notes()
    notes.append(note)
    with open(NOTES_FILE, 'w', encoding='utf-8') as f: json.dump(notes, f, indent=4)

def load_custom_commands():
    if os.path.exists(CUSTOM_CMDS_FILE):
        with open(CUSTOM_CMDS_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    return {}

def save_custom_command(name, cmd_info):
    cmds = load_custom_commands()
    cmds[name] = cmd_info
    with open(CUSTOM_CMDS_FILE, 'w', encoding='utf-8') as f: json.dump(cmds, f, indent=4)
