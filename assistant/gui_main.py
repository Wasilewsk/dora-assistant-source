import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import wx
import config_manager
import os

class MainUIFrame(wx.Frame):
    def __init__(self, assistant):
        super().__init__(None, title="Dora Assistant UI - The Bluebird Project", size=(600, 600))
        self.assistant = assistant
        self.notebook = wx.Notebook(self)
        
        # Tabs
        self.notebook.AddPage(MainTab(self.notebook, self.assistant), "Controls")
        self.notebook.AddPage(CommandsTab(self.notebook, self.assistant), "Commands")
        self.notebook.AddPage(TeamTalkTab(self.notebook, self.assistant), "TeamTalk")
        self.notebook.AddPage(NotesTab(self.notebook, self.assistant), "Notes")
        
        self.Show()

class MainTab(wx.Panel):
    def __init__(self, parent, assistant):
        super().__init__(parent)
        self.assistant = assistant
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.status = wx.StaticText(self, label="Status: Active", style=wx.ALIGN_CENTER)
        self.status.SetName("Assistant Status")
        vbox.Add(self.status, 0, wx.ALL | wx.EXPAND, 10)
        
        btn_stop = wx.Button(self, label="Stop All Media")
        btn_stop.SetName("Stop all media button")
        btn_stop.SetToolTip("Stops all music playback")
        btn_stop.Bind(wx.EVT_BUTTON, self.on_stop)
        vbox.Add(btn_stop, 0, wx.ALL | wx.EXPAND, 5)
        
        self.SetSizer(vbox)

    def on_stop(self, event):
        self.assistant.stop_all_media()
        wx.CallAfter(self.status.SetLabel, "Status: Media Stopped")

class CommandsTab(wx.Panel):
    def __init__(self, parent, assistant):
        super().__init__(parent)
        self.assistant = assistant
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        choices = list(self.assistant._command_map['en'].keys()) if self.assistant else []
        self.listbox = wx.ListBox(self, choices=choices)
        self.listbox.SetName("Commands List")
        self.listbox.SetToolTip("Select a command to run.")
        vbox.Add(self.listbox, 1, wx.ALL | wx.EXPAND, 10)
        
        btn_run = wx.Button(self, label="Run Selected")
        btn_run.SetName("Run Command Button")
        btn_run.SetToolTip("Executes the selected command.")
        btn_run.Bind(wx.EVT_BUTTON, self.on_run)
        vbox.Add(btn_run, 0, wx.ALL | wx.EXPAND, 5)
        
        self.SetSizer(vbox)

    def on_run(self, event):
        sel = self.listbox.GetStringSelection()
        if sel and self.assistant:
            self.assistant.process_command(sel)

class TeamTalkTab(wx.Panel):
    def __init__(self, parent, assistant):
        super().__init__(parent)
        self.assistant = assistant
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        btn_start = wx.Button(self, label="Start Monitors")
        btn_start.SetName("Start TeamTalk Monitors")
        btn_start.SetToolTip("Starts background monitoring for configured TeamTalk servers.")
        btn_start.Bind(wx.EVT_BUTTON, lambda e: self.assistant.process_command("start teamtalk monitor"))
        vbox.Add(btn_start, 0, wx.ALL | wx.EXPAND, 5)
        
        btn_stop = wx.Button(self, label="Stop Monitors")
        btn_stop.SetName("Stop TeamTalk Monitors")
        btn_stop.SetToolTip("Stops all background TeamTalk server monitoring.")
        btn_stop.Bind(wx.EVT_BUTTON, lambda e: self.assistant.process_command("stop teamtalk monitor"))
        vbox.Add(btn_stop, 0, wx.ALL | wx.EXPAND, 5)
        
        self.SetSizer(vbox)

class NotesTab(wx.Panel):
    def __init__(self, parent, assistant):
        super().__init__(parent)
        self.assistant = assistant
        self.pin = config_manager.get_notes_pin()
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.content = wx.Panel(self)
        self.content.Hide()
        
        label_pin = wx.StaticText(self, label="Enter PIN:")
        vbox.Add(label_pin, 0, wx.ALL, 5)
        
        self.pin_prompt = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        self.pin_prompt.SetName("Notes PIN Input")
        vbox.Add(self.pin_prompt, 0, wx.ALL | wx.EXPAND, 5)
        
        btn_login = wx.Button(self, label="Unlock Notes")
        btn_login.SetName("Unlock Button")
        btn_login.Bind(wx.EVT_BUTTON, self.on_unlock)
        vbox.Add(btn_login, 0, wx.ALL | wx.EXPAND, 5)
        
        if not self.pin:
            self.content.Show()

        self.listbox = wx.ListBox(self.content)
        self.listbox.SetName("Notes List")
        
        content_vbox = wx.BoxSizer(wx.VERTICAL)
        content_vbox.Add(self.listbox, 1, wx.ALL | wx.EXPAND, 10)
        self.content.SetSizer(content_vbox)
        
        vbox.Add(self.content, 1, wx.ALL | wx.EXPAND, 10)
        
        self.SetSizer(vbox)
        self.refresh_notes()

    def on_unlock(self, event):
        if self.pin_prompt.GetValue() == self.pin:
            self.content.Show()
            self.Layout()
        else:
            wx.MessageBox("Incorrect PIN", "Error", wx.OK | wx.ICON_ERROR)

    def refresh_notes(self):
        self.listbox.Set(config_manager.load_notes())

def launch_ui(assistant):
    app = wx.App()
    MainUIFrame(assistant)
    app.MainLoop()
