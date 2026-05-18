import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import wx
import config_manager
import os

class MainUIFrame(wx.Frame):
    def __init__(self, assistant=None):
        super().__init__(None, title="Dora Assistant UI - The Bluebird Project", size=(600, 600))
        self.assistant = assistant
        self.notebook = wx.Notebook(self)
        
        # Tabs
        self.notebook.AddPage(MainTab(self.notebook), "Controls")
        self.notebook.AddPage(CommandsTab(self.notebook), "Commands")
        self.notebook.AddPage(TeamTalkTab(self.notebook), "TeamTalk")
        self.notebook.AddPage(TranslationTab(self.notebook), "Translation")
        
        self.Show()

    def send_command(self, cmd):
        ipc_file = os.path.join(config_manager.BASE_DATA_DIR, 'gui_cmd.txt')
        with open(ipc_file, 'w') as f:
            f.write(cmd)

class TeamTalkTab(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        btn_start = wx.Button(self, label="Start Monitors")
        btn_start.SetToolTip("Starts background monitoring for configured TeamTalk servers.")
        btn_start.Bind(wx.EVT_BUTTON, lambda e: self.GetParent().GetParent().send_command("start teamtalk monitor"))
        vbox.Add(btn_start, 0, wx.ALL | wx.EXPAND, 5)
        
        btn_stop = wx.Button(self, label="Stop Monitors")
        btn_stop.SetToolTip("Stops all background TeamTalk server monitoring.")
        btn_stop.Bind(wx.EVT_BUTTON, lambda e: self.GetParent().GetParent().send_command("stop teamtalk monitor"))
        vbox.Add(btn_stop, 0, wx.ALL | wx.EXPAND, 5)
        
        self.SetSizer(vbox)

class TranslationTab(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        label_in = wx.StaticText(self, label="Text to Translate:")
        vbox.Add(label_in, 0, wx.ALL, 5)
        self.text_in = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(-1, 100))
        vbox.Add(self.text_in, 0, wx.EXPAND | wx.ALL, 5)
        
        label_lang = wx.StaticText(self, label="Target Language:")
        vbox.Add(label_lang, 0, wx.ALL, 5)
        self.lang_choice = wx.Choice(self, choices=["en", "fr", "de", "es", "it", "pt", "ru", "ja", "ko", "zh-CN"])
        self.lang_choice.SetSelection(0)
        vbox.Add(self.lang_choice, 0, wx.EXPAND | wx.ALL, 5)
        
        btn_translate = wx.Button(self, label="Translate")
        btn_translate.Bind(wx.EVT_BUTTON, self.on_translate)
        vbox.Add(btn_translate, 0, wx.ALL | wx.EXPAND, 5)
        
        label_out = wx.StaticText(self, label="Result:")
        vbox.Add(label_out, 0, wx.ALL, 5)
        self.text_out = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1, 100))
        vbox.Add(self.text_out, 0, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(vbox)

    def on_translate(self, event):
        text = self.text_in.GetValue()
        target = self.lang_choice.GetStringSelection()
        if not text: return
        
        try:
            from deep_translator import GoogleTranslator
            translated = GoogleTranslator(source='auto', target=target).translate(text)
            self.text_out.SetValue(translated)
        except Exception as e:
            wx.MessageBox(f"Translation error: {e}", "Error", wx.OK | wx.ICON_ERROR)

class MainTab(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        btn_stop = wx.Button(self, label="Stop All Media")
        btn_stop.Bind(wx.EVT_BUTTON, lambda e: self.GetParent().GetParent().send_command("stop"))
        vbox.Add(btn_stop, 0, wx.ALL | wx.EXPAND, 5)
        
        self.SetSizer(vbox)

class CommandsTab(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.listbox = wx.ListBox(self, choices=["stop", "play music", "battery status", "ai-on", "ai-off"])
        vbox.Add(self.listbox, 1, wx.ALL | wx.EXPAND, 10)
        
        btn_run = wx.Button(self, label="Run Selected")
        btn_run.Bind(wx.EVT_BUTTON, self.on_run)
        vbox.Add(btn_run, 0, wx.ALL | wx.EXPAND, 5)
        
        self.SetSizer(vbox)

    def on_run(self, event):
        sel = self.listbox.GetStringSelection()
        if sel:
            self.GetParent().GetParent().send_command(sel)

if __name__ == "__main__":
    app = wx.App()
    MainUIFrame(None)
    app.MainLoop()
