import wx
import configparser
import json
import os
import config_manager

class ConfigGUI(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Dora Configurator - The Bluebird Project", size=(600, 500))
        self.config = configparser.ConfigParser()
        if os.path.exists(config_manager.CONFIG_FILE):
            self.config.read(config_manager.CONFIG_FILE, encoding='utf-8')
        self.settings = config_manager.load_settings()
        self.cmds = config_manager.load_custom_commands()

        self.notebook = wx.Notebook(self)
        self.notebook.AddPage(TelegramTab(self.notebook, self.config), "Telegram")
        self.notebook.AddPage(ServersTab(self.notebook, self.config), "Servers")
        self.notebook.AddPage(SettingsTab(self.notebook, self.settings), "Settings")
        self.notebook.AddPage(CustomCmdsTab(self.notebook, self), "Custom Commands")
        
        btn_save = wx.Button(self, label="Save & Exit")
        btn_save.SetName("Save button")
        btn_save.SetToolTip("Save all settings and exit.")
        btn_save.Bind(wx.EVT_BUTTON, self.on_save)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.EXPAND)
        sizer.Add(btn_save, 0, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer)
        self.Show()

    def on_save(self, event):
        with open(config_manager.CONFIG_FILE, 'w', encoding='utf-8') as f: self.config.write(f)
        config_manager.save_settings(self.settings)
        with open(config_manager.CUSTOM_CMDS_FILE, 'w', encoding='utf-8') as f: json.dump(self.cmds, f, indent=4)
        self.Close()

class AddServerDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Add Server Configuration", size=(400, 500))
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.fields = {}
        for field in ['Name', 'Host', 'TCPPort', 'UDPPort', 'Nickname', 'Channel']:
            label = wx.StaticText(self, label=f"{field}:")
            vbox.Add(label, 0, wx.ALL, 5)
            ctrl = wx.TextCtrl(self)
            ctrl.SetName(f"{field}")
            label.SetLabel(f"{field}")
            # Ensure label is associated
            vbox.Add(ctrl, 0, wx.EXPAND | wx.ALL, 5)
            self.fields[field] = ctrl
        
        btn_ok = wx.Button(self, wx.ID_OK, label="Add")
        btn_ok.SetName("Add button")
        vbox.Add(btn_ok, 0, wx.ALL, 10)
        self.SetSizer(vbox)

    def get_data(self):
        return {f: self.fields[f].GetValue() for f in self.fields}

class ServersTab(wx.Panel):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.listbox = wx.ListBox(self, choices=[s for s in config.sections() if s.lower().startswith('server ')])
        self.listbox.SetName("Servers List")
        vbox.Add(self.listbox, 1, wx.EXPAND | wx.ALL, 5)
        
        btn_add = wx.Button(self, label="Add Server")
        btn_add.SetName("Add Server Button")
        btn_add.SetToolTip("Open a detailed dialog to add a new TeamTalk server.")
        btn_add.Bind(wx.EVT_BUTTON, self.on_add)
        vbox.Add(btn_add, 0, wx.EXPAND | wx.ALL, 5)
        
        btn_remove = wx.Button(self, label="Remove Server")
        btn_remove.SetName("Remove Server Button")
        btn_remove.SetToolTip("Remove the selected server.")
        btn_remove.Bind(wx.EVT_BUTTON, self.on_remove)
        vbox.Add(btn_remove, 0, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(vbox)

    def on_add(self, event):
        dlg = AddServerDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.get_data()
            section = f"server {data['Name']}"
            self.config[section] = {k.lower(): v for k, v in data.items() if k != 'Name'}
            self.listbox.Append(section)
        dlg.Destroy()

    def on_remove(self, event):
        sel = self.listbox.GetSelection()
        if sel != wx.NOT_FOUND:
            name = self.listbox.GetString(sel)
            self.config.remove_section(name)
            self.listbox.Delete(sel)

class TelegramTab(wx.Panel):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        label = wx.StaticText(self, label="Bot Token:")
        vbox.Add(label, 0, wx.ALL, 5)
        self.token = wx.TextCtrl(self, value=config.get('Telegram', 'token', fallback=''))
        self.token.SetName("Bot Token Input")
        label.SetLabel("Bot Token")
        vbox.Add(self.token, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(vbox)
        self.token.Bind(wx.EVT_TEXT, self.on_change)

    def on_change(self, event):
        if 'Telegram' not in self.config: self.config['Telegram'] = {}
        self.config['Telegram']['token'] = self.token.GetValue()

class SettingsTab(wx.Panel):
    def __init__(self, parent, settings):
        super().__init__(parent)
        self.settings = settings
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        label_user = wx.StaticText(self, label="Username:")
        vbox.Add(label_user, 0, wx.ALL, 5)
        self.user = wx.TextCtrl(self, value=settings.get('username', 'User'))
        self.user.SetName("Username Input")
        label_user.SetLabel("Username")
        vbox.Add(self.user, 0, wx.EXPAND | wx.ALL, 5)
        
        label_pin = wx.StaticText(self, label="Notes PIN:")
        vbox.Add(label_pin, 0, wx.ALL, 5)
        self.pin = wx.TextCtrl(self, value=settings.get('notes_pin', ''), style=wx.TE_PASSWORD)
        self.pin.SetName("Notes PIN Input")
        label_pin.SetLabel("Notes PIN")
        vbox.Add(self.pin, 0, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(vbox)
        self.user.Bind(wx.EVT_TEXT, lambda e: settings.update({'username': self.user.GetValue()}))
        self.pin.Bind(wx.EVT_TEXT, lambda e: settings.update({'notes_pin': self.pin.GetValue()}))

class CustomCmdsTab(wx.Panel):
    def __init__(self, parent, frame):
        super().__init__(parent)
        self.frame = frame
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.list = wx.ListBox(self, choices=list(frame.cmds.keys()))
        self.list.SetName("Custom Commands List")
        vbox.Add(self.list, 1, wx.EXPAND | wx.ALL, 5)
        btn_add = wx.Button(self, label="Add Custom Command")
        btn_add.SetName("Add Custom Command Button")
        btn_add.SetToolTip("Opens a dialog to add a new command trigger.")
        btn_add.Bind(wx.EVT_BUTTON, self.on_add)
        vbox.Add(btn_add, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(vbox)

    def on_add(self, event):
        dlg = wx.TextEntryDialog(self, "Trigger Name:", "Add Cmd")
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.GetValue()
            # Simplified for brevity, add type selection later if needed
            self.frame.cmds[name] = {'type': 'shell', 'command': 'echo hello'}
            self.list.Append(name)
        dlg.Destroy()

def run_gui_config():
    app = wx.App()
    ConfigGUI()
    app.MainLoop()

if __name__ == "__main__":
    run_gui_config()
