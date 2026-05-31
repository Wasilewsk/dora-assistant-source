# Dora Assistant — Skill Development Guide

Third-party skills let you add custom voice commands to Dora without modifying
the core code. Skills are Python files placed in `~/.assistant-skills/` and are
auto-loaded when the assistant starts.

---

## Quick Start

Create a file `~/.assistant-skills/hello.py`:

```python
metadata = {
    'name': 'Hello Skill',
    'version': '1.0',
    'author': 'Your Name',
    'description': 'A simple greeting skill'
}

def register(assistant):
    assistant.register_command('say hello', cmd_hello)
    assistant.register_command('say goodbye', cmd_goodbye)

def cmd_hello(assistant, command):
    assistant.speak("Hello! This is my custom skill.")

def cmd_goodbye(assistant, command):
    assistant.speak("Goodbye from my custom skill!")
```

Restart Dora. Say **"say hello"** — the assistant will respond using your skill.

---

## Skill Structure

Every skill **must** define:

### `metadata` dict

```python
metadata = {
    'name': 'Skill Name',          # Required — display name
    'version': '1.0',              # Optional — version string
    'author': 'Your Name',         # Optional — who made it
    'description': 'What it does'  # Optional — short explanation
}
```

### `register(assistant)` function

Called once when the skill is loaded. Use it to register your commands:

```python
def register(assistant):
    assistant.register_command('trigger phrase', handler_function)
```

### Handler functions

Each handler receives two arguments:

| Argument | Type | Description |
|----------|------|-------------|
| `assistant` | object | The main Assistant instance — use its methods to speak, listen, etc. |
| `command` | str | The full text the user said after the wake word |

```python
def my_handler(assistant, command):
    """command is the full utterance, e.g. 'open notepad'"""
    assistant.speak("Doing something...")
```

---

## Assistant API — Available Methods

### Speaking & Listening

| Method | Description |
|--------|-------------|
| `assistant.speak(text)` | Speak text aloud (TTS) and print to console |
| `assistant.listen(timeout=7)` | Listen for voice input, returns recognized text or `""` |

### Responses & Language

| Method | Description |
|--------|-------------|
| `assistant.get_response(key, **kwargs)` | Get a formatted string from the current language file |
| `assistant.current_lang` | Current language code (e.g. `'en'`) |

### Settings & State

| Attribute | Description |
|-----------|-------------|
| `assistant.username` | The user's name |
| `assistant.settings` | Dict of all settings from `settings.json` |
| `assistant.ai_mode` | Whether AI chat mode is enabled (`True`/`False`) |
| `assistant.is_running` | Whether the main loop is active |

### Sound Effects

| Method | Description |
|--------|-------------|
| `assistant.play_sfx(filename)` | Play a sound effect from the soundpack (e.g. `'ok.mp3'`) |

### Command Registration

| Method | Description |
|--------|-------------|
| `assistant.register_command(trigger, handler, lang='en')` | Register a voice command |
| `assistant.unregister_command(trigger, lang='en')` | Remove a previously registered command |

### Notification

| Method | Description |
|--------|-------------|
| `assistant.notify_telegram(text)` | Send a notification via Telegram (if configured) |

---

## Examples

### 1. System Info Skill

`~/.assistant-skills/system_info.py`:

```python
import psutil
import datetime

metadata = {
    'name': 'System Info',
    'version': '1.0',
    'author': 'Developer',
    'description': 'Reports system uptime and CPU usage'
}

def register(assistant):
    assistant.register_command('system status', cmd_status)
    assistant.register_command('uptime', cmd_uptime)

def cmd_status(assistant, command):
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    assistant.speak(f"CPU is at {cpu} percent. Memory is at {mem.percent} percent.")

def cmd_uptime(assistant, command):
    boot = datetime.datetime.fromtimestamp(psutil.boot_time())
    delta = datetime.datetime.now() - boot
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, _ = divmod(remainder, 60)
    assistant.speak(f"System has been up for {hours} hours and {minutes} minutes.")
```

### 2. Weather Skill (using an API)

`~/.assistant-skills/weather.py`:

```python
import requests

metadata = {
    'name': 'Weather',
    'version': '1.0',
    'author': 'Developer',
    'description': 'Gets current weather for a city'
}

def register(assistant):
    assistant.register_command('get weather', cmd_weather)

def cmd_weather(assistant, command):
    city = command.replace('get weather', '').strip()
    if not city:
        assistant.speak("Which city should I check the weather for?")
        city = assistant.listen()
        if not city:
            return
    try:
        resp = requests.get(
            f"https://wttr.in/{city}?format=%C+%t",
            timeout=10
        )
        assistant.speak(f"Weather in {city}: {resp.text}")
    except Exception as e:
        assistant.speak(f"Could not get weather: {e}")
```

### 3. Timer Skill (using built-in features)

`~/.assistant-skills/pomodoro.py`:

```python
import threading
import time

metadata = {
    'name': 'Pomodoro Timer',
    'version': '1.0',
    'author': 'Developer',
    'description': 'A 25-minute focus timer'
}

_timer_active = False

def register(assistant):
    assistant.register_command('start pomodoro', cmd_pomodoro)

def cmd_pomodoro(assistant, command):
    global _timer_active
    if _timer_active:
        assistant.speak("A pomodoro is already running.")
        return
    _timer_active = True
    assistant.speak("Starting 25 minute focus session.")
    threading.Thread(target=_pomodoro_loop, args=(assistant,), daemon=True).start()

def _pomodoro_loop(assistant):
    global _timer_active
    time.sleep(1500)  # 25 minutes
    if _timer_active:
        assistant.speak("Pomodoro complete! Time for a break.")
    _timer_active = False
```

---

## Tips

- Keep handler functions **fast** — use `threading.Thread` for long-running tasks
- Use `assistant.speak()` for all voice output; it also logs to the terminal
- Commands are matched by **substring** — shorter triggers may be shadowed by longer ones
- Avoid `input()` or `print()` directly; use the assistant's methods instead
- Test your skill by restarting Dora; there is no hot-reload yet

## Troubleshooting

| Problem | Likely Cause |
|---------|-------------|
| Skill not loaded | File is not in `~/.assistant-skills/` or has `register()` missing |
| Command not recognized | Trigger phrase might be shadowed by a longer built-in command |
| Import error | Your skill uses a library not installed — add it with `pip install` |
| Syntax error | Check the file with `python -m py_compile ~/.assistant-skills/your_skill.py` |
