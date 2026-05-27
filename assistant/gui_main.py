import sys
import os
import wx
import datetime
import threading

# Add parent directory to sys.path to allow imports from assistant
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config_manager
from skills import timer

class EchoShowFrame(wx.Frame):
    def __init__(self, assistant=None):
        super().__init__(None, title="Dora Assistant - Echo Show Mode", size=(900, 550), style=wx.DEFAULT_FRAME_STYLE)
        self.assistant = assistant
        
        # Main Panel for proper tab traversal and accessibility
        self.panel = wx.Panel(self, style=wx.TAB_TRAVERSAL)
        self.panel.SetBackgroundColour(wx.Colour(0, 0, 0))
        
        # Load settings for username
        settings = config_manager.load_settings()
        username = settings.get('username', 'User')
        
        # Main Sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # --- Top Bar ---
        self.top_bar = wx.BoxSizer(wx.HORIZONTAL)
        
        self.greeting_label = wx.StaticText(self.panel, label=f"Hello, {username}", name="Greeting Message")
        self.greeting_label.SetForegroundColour(wx.Colour(200, 200, 200))
        self.greeting_label.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT))
        self.top_bar.Add(self.greeting_label, 0, wx.ALL, 20)
        
        self.top_bar.AddStretchSpacer(1)
        
        self.battery_label = wx.StaticText(self.panel, label="Battery: --%", name="Battery Level Status")
        self.battery_label.SetForegroundColour(wx.Colour(200, 200, 200))
        self.battery_label.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.top_bar.Add(self.battery_label, 0, wx.ALL, 20)
        
        self.main_sizer.Add(self.top_bar, 0, wx.EXPAND)
        
        # --- Center Content (Clock & Date) ---
        self.main_sizer.AddStretchSpacer(1)
        
        self.clock_label = wx.StaticText(self.panel, label="00:00:00", name="Clock")
        self.clock_label.SetForegroundColour(wx.Colour(255, 255, 255))
        clock_font = wx.Font(84, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.clock_label.SetFont(clock_font)
        self.main_sizer.Add(self.clock_label, 0, wx.ALIGN_CENTER)
        
        self.date_label = wx.StaticText(self.panel, label="Monday, January 1", name="Calendar Date")
        self.date_label.SetForegroundColour(wx.Colour(180, 180, 180))
        date_font = wx.Font(28, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT)
        self.date_label.SetFont(date_font)
        self.main_sizer.Add(self.date_label, 0, wx.ALIGN_CENTER | wx.TOP, 10)
        
        self.main_sizer.AddStretchSpacer(1)
        
        # --- Status Line ---
        self.status_label = wx.StaticText(self.panel, label="Ready", name="Assistant Current Status")
        self.status_label.SetForegroundColour(wx.Colour(0, 150, 255))
        status_font = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL)
        self.status_label.SetFont(status_font)
        self.main_sizer.Add(self.status_label, 0, wx.ALIGN_CENTER | wx.BOTTOM, 40)
        
        # --- Alarm Controls ---
        self.alarm_sizer = wx.StaticBoxSizer(wx.VERTICAL, self.panel, "Alarm Settings")
        self.alarm_sizer.GetStaticBox().SetForegroundColour(wx.Colour(200, 200, 200))
        
        # Horizontal layout for picker and choice
        self.alarm_controls = wx.BoxSizer(wx.HORIZONTAL)
        
        # Duration SpinCtrl
        self.duration_label = wx.StaticText(self.panel, label="Minutes:", name="Alarm Duration Label")
        self.duration_label.SetForegroundColour(wx.Colour(255, 255, 255))
        self.duration_ctrl = wx.SpinCtrl(self.panel, value="5", min=1, max=1440, size=(70, -1), name="Alarm Minutes Picker")
        
        # Sound Choice
        self.sound_label = wx.StaticText(self.panel, label="Sound:", name="Alarm Sound Label")
        self.sound_label.SetForegroundColour(wx.Colour(255, 255, 255))
        
        # Get list of sounds
        alarms_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'alarms')
        sound_files = ["Random"]
        if os.path.exists(alarms_dir):
            files = [f for f in os.listdir(alarms_dir) if f.endswith(('.ogg', '.wav', '.mp3'))]
            sound_files.extend(files)
            
        self.sound_choice = wx.Choice(self.panel, choices=sound_files, name="Alarm Sound Selector")
        self.sound_choice.SetSelection(0)
        
        # Set Alarm Button
        self.set_alarm_btn = wx.Button(self.panel, label="Set Alarm", size=(120, -1), name="Set Alarm Button")
        self.set_alarm_btn.SetBackgroundColour(wx.Colour(0, 100, 0))
        self.set_alarm_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.set_alarm_btn.Bind(wx.EVT_BUTTON, self.on_set_custom_alarm)
        
        self.alarm_controls.Add(self.duration_label, 0, wx.ALIGN_CENTER | wx.RIGHT, 5)
        self.alarm_controls.Add(self.duration_ctrl, 0, wx.ALIGN_CENTER | wx.RIGHT, 15)
        self.alarm_controls.Add(self.sound_label, 0, wx.ALIGN_CENTER | wx.RIGHT, 5)
        self.alarm_controls.Add(self.sound_choice, 1, wx.ALIGN_CENTER | wx.RIGHT, 15)
        self.alarm_controls.Add(self.set_alarm_btn, 0, wx.ALIGN_CENTER)
        
        self.alarm_sizer.Add(self.alarm_controls, 0, wx.EXPAND | wx.ALL, 10)
        self.main_sizer.Add(self.alarm_sizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        
        # --- Reminder Controls ---
        self.rem_sizer = wx.StaticBoxSizer(wx.VERTICAL, self.panel, "Reminder Settings")
        self.rem_sizer.GetStaticBox().SetForegroundColour(wx.Colour(200, 200, 200))
        
        self.rem_controls = wx.BoxSizer(wx.HORIZONTAL)
        
        self.rem_text = wx.TextCtrl(self.panel, value="Take a break", size=(200, -1), name="Reminder Text Input")
        self.rem_time = wx.TextCtrl(self.panel, value="12:00", size=(60, -1), name="Reminder Time Input")
        self.rem_ampm = wx.Choice(self.panel, choices=["AM", "PM"], name="Reminder AM/PM Selector")
        self.rem_ampm.SetSelection(1) # Default to PM
        
        self.set_rem_btn = wx.Button(self.panel, label="Set Reminder", size=(120, -1), name="Set Reminder Button")
        self.set_rem_btn.SetBackgroundColour(wx.Colour(0, 0, 100))
        self.set_rem_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.set_rem_btn.Bind(wx.EVT_BUTTON, self.on_set_reminder)
        
        self.rem_controls.Add(wx.StaticText(self.panel, label="Task:"), 0, wx.ALIGN_CENTER | wx.RIGHT, 5)
        self.rem_controls.Add(self.rem_text, 1, wx.ALIGN_CENTER | wx.RIGHT, 15)
        self.rem_controls.Add(wx.StaticText(self.panel, label="Time:"), 0, wx.ALIGN_CENTER | wx.RIGHT, 5)
        self.rem_controls.Add(self.rem_time, 0, wx.ALIGN_CENTER | wx.RIGHT, 5)
        self.rem_controls.Add(self.rem_ampm, 0, wx.ALIGN_CENTER | wx.RIGHT, 15)
        self.rem_controls.Add(self.set_rem_btn, 0, wx.ALIGN_CENTER)
        
        self.rem_sizer.Add(self.rem_controls, 0, wx.EXPAND | wx.ALL, 10)
        self.main_sizer.Add(self.rem_sizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 20)
        
        # --- Action Buttons ---
        self.btn_grid = wx.FlexGridSizer(rows=2, cols=4, hgap=15, vgap=15)
        
        actions = [
            ("Stop All", "stop", "Stops all media and alarms"),
            ("Play Music", "play music", "Plays random songs from your music folder"),
            ("Set Timer", "set timer 5 minutes", "Starts a 5 minute countdown"),
            ("List Reminders", "list reminders", "Announces all your scheduled reminders"),
            ("What Time", "what time is it", "Dora will tell you the current time"),
            ("Battery Status", "battery status", "Dora will announce the battery level"),
            ("Open Apps", "open", "Opens the application launcher"),
            ("Help Menu", "help", "Shows a list of all voice commands")
        ]
        
        for label, cmd, tooltip in actions:
            btn = wx.Button(self.panel, label=label, size=(160, 50), name=label)
            btn.SetBackgroundColour(wx.Colour(50, 50, 50))
            btn.SetForegroundColour(wx.Colour(255, 255, 255))
            btn.SetToolTip(tooltip)
            # Accessibility: The label is already set, but explicitly setting Name helps some screen readers
            btn.Bind(wx.EVT_BUTTON, lambda e, c=cmd: self.send_command(c))
            self.btn_grid.Add(btn, 0, wx.ALIGN_CENTER)
            
        self.main_sizer.Add(self.btn_grid, 0, wx.ALIGN_CENTER | wx.BOTTOM, 30)
        
        # --- Alarm Stop Alert (Hidden by default) ---
        self.stop_alarm_btn = wx.Button(self.panel, label="STOP ALARM", size=(400, 100), name="Emergency Stop Alarm")
        self.stop_alarm_btn.SetBackgroundColour(wx.Colour(200, 0, 0)) # Bright Red
        self.stop_alarm_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.stop_alarm_btn.SetFont(wx.Font(36, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.stop_alarm_btn.Bind(wx.EVT_BUTTON, lambda e: self.send_command("stop"))
        self.stop_alarm_btn.Hide()
        self.main_sizer.Add(self.stop_alarm_btn, 0, wx.ALIGN_CENTER | wx.ALL, 20)
        
        self.panel.SetSizer(self.main_sizer)
        self.main_sizer.Fit(self) # Ensure the frame fits the sizer content
        self.Layout()
        
        # Timers
        self.clock_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_update_clock, self.clock_timer)
        self.clock_timer.Start(1000)
        
        # Initial updates
        self.update_battery()
        self.on_update_clock(None)
        
        self.Show()

    def on_update_clock(self, event):
        now = datetime.datetime.now()
        self.clock_label.SetLabel(now.strftime("%H:%M:%S"))
        self.date_label.SetLabel(now.strftime("%A, %B %d"))
        
        # Check alarm state frequently using the new state checker
        if timer.is_alarm_active():
            if not self.stop_alarm_btn.IsShown():
                self.stop_alarm_btn.Show()
                self.btn_grid.Hide()
                self.alarm_sizer.Hide()
                self.Layout()
        else:
            if self.stop_alarm_btn.IsShown():
                self.stop_alarm_btn.Hide()
                self.btn_grid.Show()
                self.alarm_sizer.Show()
                self.Layout()

        if now.second == 0:
            self.update_battery()
            
        self.panel.Layout()

    def update_battery(self):
        try:
            import psutil
            battery = psutil.sensors_battery()
            if battery:
                percent = battery.percent
                plugged = " (Charging)" if battery.power_plugged else ""
                self.battery_label.SetLabel(f"Battery: {percent}%{plugged}")
                self.battery_label.SetName(f"Battery Level: {percent} percent{plugged}")
        except Exception:
            self.battery_label.SetLabel("Battery: N/A")

    def on_set_custom_alarm(self, event):
        minutes = self.duration_ctrl.GetValue()
        sound = self.sound_choice.GetStringSelection()
        
        # Command format: set timer X minutes sound:filename.ogg
        cmd = f"set timer {minutes} minutes"
        if sound != "Random":
            cmd += f" sound:{sound}"
            
        self.send_command(cmd)
        self.status_label.SetLabel(f"Alarm set: {minutes}m ({sound})")

    def on_set_reminder(self, event):
        text = self.rem_text.GetValue()
        time_str = self.rem_time.GetValue()
        ampm = self.rem_ampm.GetStringSelection()
        if not text or not time_str: return
        
        try:
            # Convert 12h time to 24h for the reminder skill
            time_obj = datetime.datetime.strptime(f"{time_str} {ampm}", "%I:%M %p")
            final_time = time_obj.strftime("%H:%M")
            
            # Command format: remind me to [text] at [HH:MM]
            cmd = f"remind me to {text} at {final_time}"
            self.send_command(cmd)
            self.status_label.SetLabel(f"Reminder set: {time_str} {ampm}")
        except ValueError:
            self.status_label.SetLabel("Error: Invalid time format (use HH:MM)")

    def send_command(self, cmd):
        ipc_file = os.path.join(config_manager.BASE_DATA_DIR, 'gui_cmd.txt')
        try:
            with open(ipc_file, 'w') as f:
                f.write(cmd)
            self.status_label.SetLabel(f"Command: {cmd}")
            self.status_label.SetName(f"Assistant Status: Command {cmd} sent")
        except Exception as e:
            print(f"GUI IPC Error: {e}")

def launch_ui(assistant=None):
    app = wx.App()
    EchoShowFrame(assistant)
    app.MainLoop()

if __name__ == "__main__":
    launch_ui()
