# Dora Assistant

Dora is a Python-based virtual assistant designed for hands-free control and integration with the TeamTalk 5 conferencing platform, system management, and time-based alerts.

## Features
- **Wake Word Activation:** Responds to the wake word "computer".
- **TeamTalk Integration:** Connect to multiple servers, monitor user activity, send messages, and manage channels via voice or slash commands.
- **System Utilities:** Shutdown/restart computer, set timers with looping alarms, and check the time.
- **Terminal & Voice Input:** Control the assistant via voice commands or type commands directly into the terminal.
- **Configurable:** Easy setup for multiple TeamTalk servers and notifications via Telegram.

## Setup & Configuration
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/wasilewsk/dora-assistant-source.git
   cd dora-assistant-source
   ```

2. **Install Dependencies:**
   Ensure Python 3.12+ is installed, then run:
   ```bash
   pip install -r assistant/requirements.txt
   ```

2. **Configuration:**
   Run the GUI setup tool:
   ```bash
   python assistant/configure.py
   ```
   This will open a graphical window where you can configure your settings, server configurations, and custom commands, which will be stored in your user profile (`~/.assistantconf/`).

## Running the Assistant and GUI
The assistant now consists of two components: the core **Assistant** and the **User Interface (GUI)**. Because they operate in separate processes for stability, they are started independently.

1. **Start the Assistant:**
   Open a terminal and run the main assistant process:
   ```bash
   python assistant/main.py
   ```
   This will start the listening loop and wait for voice/text commands.

2. **Open the GUI (Optional):**
   When you want to access the Translation, Media Controls, or TeamTalk monitors, open a **new** terminal window and run:
   ```bash
   python assistant/gui_main.py
   ```
   The GUI will now connect automatically to the running assistant. Use the tabs in the GUI to control music, send commands, or translate text.

## Command Reference
You can say these commands or type them using the `/` prefix in the terminal. The GUI tabs can also trigger these commands for you.

- `/help` or `/commands`: List all available commands.
- `/start-server` / `/stop-server`: Manage TeamTalk monitoring.
- `/switch-server`: Switch between configured TeamTalk servers.
- `/pm` / `/write` / `/broadcast`: Send TeamTalk messages.
- `/kick`: Kick a user from the channel.
- `/timer [minutes]`: Set a timer.
- `/stop-timer`: Stop the timer or alarm.
- `/play` / `/next` / `/stop`: Local music control (Music is stored in `~/.assistant-music`).
- `/add-note [note]`: Save a note to your user data folder.
- `/list-notes`: Read your saved notes.
- `/delete-notes`: Delete all saved notes.
- `/time`: Get the current time.
- `/shutdown`: Shutdown the system.
- `battery status` / `/battery`: Check your system battery status.
- `ai-on` / `ai-off`: Toggle AI Chatting mode (using configured Ollama/OpenAI provider).
- `open [appname]` / `start [appname]`: Launch applications like Chrome, Notepad, etc.


## Custom Commands
You can define your own custom commands using the configuration utility:
1. Run `python assistant/configure.py`.
2. Select "Add Custom Command".
3. Define the trigger name, command type (exe/shell/port), and the associated path/command.
4. Trigger them by typing or saying the command name.

*Note: For TeamTalk integration, ensure `TeamTalk5.dll` is present in the `assistant` directory.*
