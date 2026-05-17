# language_manager.py

import json
import os

# Set LANG_DIR relative to the location of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LANG_DIR = os.path.join(BASE_DIR, 'lang')
LANG_CONFIG = {}

def load_languages():
    """Loads all language JSON files from the lang directory."""
    if not os.path.exists(LANG_DIR):
        print(f"!!! CRITICAL ERROR: The '{LANG_DIR}' folder was not found!")
        exit()
    
    try:
        for filename in os.listdir(LANG_DIR):
            if filename.endswith('.json'):
                lang_code = filename.split('.')[0]
                filepath = os.path.join(LANG_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    LANG_CONFIG[lang_code] = json.load(f)
                    print(f"'{lang_code}' language successfully loaded.")
    except Exception as e:
        print(f"!!! CRITICAL ERROR while loading language files: {e}")
        exit()

load_languages()

def get_response(lang, key, **kwargs):
    """Returns a formatted response string for the given language and key."""
    template = LANG_CONFIG.get(lang, {}).get('RESPONSES', {}).get(key, "MISSING_TEXT_{}".format(key))
    return template.format(**kwargs)

def get_config_value(lang, key, default=None):
    """
    Retrieves other configuration values (e.g., WAKE_WORD).
    If the key is not found, it returns the specified 'default' value.
    """
    return LANG_CONFIG.get(lang, {}).get(key, default)