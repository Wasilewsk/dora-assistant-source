# config_manager.py

import configparser
import json
import os

# Base directory in user profile
BASE_CONF_DIR = os.path.join(os.path.expanduser("~"), ".assistantconf")

# Ensure the directory exists
if not os.path.exists(BASE_CONF_DIR):
    os.makedirs(BASE_CONF_DIR)

# Constants pointing to user profile
CONFIG_FILE = os.path.join(BASE_CONF_DIR, 'config.ini')
SETTINGS_FILE = os.path.join(BASE_CONF_DIR, 'settings.json')
REMINDERS_FILE = os.path.join(BASE_CONF_DIR, 'reminders.json')
ALARMS_FILE = os.path.join(BASE_CONF_DIR, 'alarms.json')

def handle_critical_error(message):
    """Prints an error message and waits for enter before exiting."""
    print("\n" + "="*50)
    print("!!! CRITICAL ERROR !!!")
    print(message)
    print("="*50)
    input("\nThe program will exit. Press Enter to exit...")
    exit()

def load_ini_config():
    """Loads the config.ini file and returns the values read from it."""
    if not os.path.exists(CONFIG_FILE):
        # Create an empty template if not exists
        print(f"Configuration file '{CONFIG_FILE}' not found. Please run configure.py.")
        return None, None
    
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    
    try:
        token = config.get('Telegram', 'token')
        chat_id = config.get('Telegram', 'chat_id')
        return token, chat_id
    except configparser.NoSectionError:
        return None, None
    except configparser.NoOptionError:
        return None, None
    except Exception as e:
        print(f"Unknown error while reading '{CONFIG_FILE}': {e}")
        return None, None

def load_settings():
    """Loads user settings (language, chatbot model, username)."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Error while loading settings: {e}. Using default settings.")
    return {'last_lang': 'en', 'chatbot_model': 1, 'username': 'User'}

def save_settings(settings_data):
    """Saves user settings."""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error while saving settings: {e}")

def load_reminders():
    if os.path.exists(REMINDERS_FILE):
        try:
            with open(REMINDERS_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except Exception: return []
    return []

def save_reminders(reminders):
    try:
        with open(REMINDERS_FILE, 'w', encoding='utf-8') as f: json.dump(reminders, f, ensure_ascii=False, indent=4)
    except Exception as e: print(f"Error while saving reminders: {e}")