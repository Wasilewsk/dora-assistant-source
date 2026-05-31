"""
Dora Assistant Skill API

Third-party skills are Python files placed in ~/.assistant-skills/.
Each skill file must define:

    metadata = {
        'name': 'My Skill',
        'version': '1.0',
        'author': 'Your Name',
        'description': 'What the skill does'
    }

    def register(assistant):
        assistant.register_command('trigger phrase', handler_function)

Handler functions receive (assistant, command_text) just like built-in skills.
Use assistant.speak(), assistant.listen(), assistant.get_response(), etc.

Example skill (~/.assistant-skills/hello.py):
------------------------------------------------
metadata = {
    'name': 'Hello Skill',
    'version': '1.0',
    'author': 'Developer',
    'description': 'Says hello'
}

def register(assistant):
    assistant.register_command('say hello', say_hello)
    assistant.register_command('say goodbye', say_goodbye)

def say_hello(assistant, command):
    assistant.speak("Hello! This is my custom skill.")

def say_goodbye(assistant, command):
    assistant.speak("Goodbye from my custom skill!")
------------------------------------------------
"""

import os

SKILLS_DIR = os.path.join(os.path.expanduser("~"), ".assistant-skills")
