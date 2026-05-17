# Dora Assistant

Dora is a Python-based virtual assistant designed for hands-free control and integration with the TeamTalk 5 conferencing platform, system management, and time-based alerts.

## Features
- **Wake Word Activation:** Responds to the wake word "computer".
- **TeamTalk Integration:** Connect to multiple servers, monitor user activity, send messages, and manage channels via voice or slash commands.
- **System Utilities:** Shutdown/restart computer, set timers with looping alarms, and check the time.
- **Terminal & Voice Input:** Control the assistant via voice commands or type commands directly into the terminal.
- **Configurable:** Easy setup for multiple TeamTalk servers and notifications via Telegram.

## Setup & Configuration
1. **Install Dependencies:**
   Ensure Python 3.12+ is installed, then run:
   ```bash
   pip install -r assistant/requirements.txt
   ```

2. **Configuration:**
   Run the setup script:
   ```bash
   python assistant/configure.py
   ```
   This will create a hidden folder in your user profile (`~/.assistantconf/`) where your settings and server configurations are stored.

3. **Running the Assistant:**
   ```bash
   python assistant/main.py
   ```

## Command Reference
You can either say these commands or type them using the `/` prefix in the terminal:

- `/help` or `/commands`: List all available commands.
- `/start-server` / `/stop-server`: Manage TeamTalk monitoring.
- `/switch-server`: Switch between configured TeamTalk servers.
- `/pm` / `/write` / `/broadcast`: Send TeamTalk messages.
- `/kick`: Kick a user from the channel.
- `/timer [minutes]`: Set a timer.
- `/stop-timer`: Stop the timer or alarm.
- `/play` / `/next` / `/stop`: Local music control.
- `/time`: Get the current time.
- `/shutdown`: Shutdown the system.

*Note: For TeamTalk integration, ensure `TeamTalk5.dll` is present in the `assistant` directory.*
