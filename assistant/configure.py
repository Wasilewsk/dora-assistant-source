import wx
import configparser
import json
import os
import config_manager

class ConfigGUI(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Dora Configurator - The Bluebird Project", size=(800, 700))
        self.config = configparser.ConfigParser()
        if os.path.exists(config_manager.CONFIG_FILE):
            self.config.read(config_manager.CONFIG_FILE, encoding='utf-8')
        self.settings = config_manager.load_settings()
        self.cmds = config_manager.load_custom_commands()

        main_panel = wx.Panel(self)
        self.notebook = wx.Notebook(main_panel)
        
        # Add Tabs
        self.tab_telegram = TelegramTab(self.notebook, self.config)
        self.tab_servers = ServersTab(self.notebook, self.config)
        self.tab_settings = SettingsTab(self.notebook, self.settings)
        self.tab_ai = AISettingsTab(self.notebook, self.settings)
        self.tab_cmds = CustomCmdsTab(self.notebook, self)
        
        self.notebook.AddPage(self.tab_telegram, "Telegram")
        self.notebook.AddPage(self.tab_servers, "Servers")
        self.notebook.AddPage(self.tab_settings, "Settings")
        self.notebook.AddPage(self.tab_ai, "AI Settings")
        self.notebook.AddPage(self.tab_cmds, "Custom Commands")
        
        # Bottom Buttons Panel - Standard for configuration windows
        btn_panel = wx.Panel(main_panel)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.btn_save = wx.Button(btn_panel, label="Save & Exit")
        self.btn_save.SetName("Save and Exit button")
        self.btn_save.SetToolTip("Save all changes and close the configurator.")
        self.btn_save.Bind(wx.EVT_BUTTON, self.on_save)
        
        self.btn_cancel = wx.Button(btn_panel, label="Cancel & Exit")
        self.btn_cancel.SetName("Cancel button")
        self.btn_cancel.SetToolTip("Close without saving.")
        self.btn_cancel.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        
        btn_sizer.Add(self.btn_save, 1, wx.ALL | wx.EXPAND, 10)
        btn_sizer.Add(self.btn_cancel, 1, wx.ALL | wx.EXPAND, 10)
        btn_panel.SetSizer(btn_sizer)
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(btn_panel, 0, wx.EXPAND)
        main_panel.SetSizer(main_sizer)
        
        self.Show()
        self.Layout()

    def on_save(self, event):
        """Saves all configurations to their respective files."""
        try:
            # Save config.ini
            with open(config_manager.CONFIG_FILE, 'w', encoding='utf-8') as f:
                self.config.write(f)
            
            # Save settings.json
            config_manager.save_settings(self.settings)
            
            # Save custom commands
            with open(config_manager.CUSTOM_CMDS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.cmds, f, indent=4)
                
            wx.MessageBox("All settings have been saved successfully.", "Success", wx.OK | wx.ICON_INFORMATION)
            self.Close()
        except Exception as e:
            wx.MessageBox(f"An error occurred while saving: {e}", "Error", wx.OK | wx.ICON_ERROR)

class AddServerDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Add Server Configuration", size=(450, 750))
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.fields = {}
        field_configs = [
            ('Name', 'Name (Display name for the server)'),
            ('Host', 'Host (e.g. tt.myserver.com)'),
            ('TCPPort', 'TCP Port'),
            ('UDPPort', 'UDP Port'),
            ('Nickname', 'Nickname'),
            ('Channel', 'Channel (e.g. / or /MyChannel)'),
            ('Username', 'Username (Optional)'),
            ('Password', 'Password (Optional)')
        ]
        
        for field, label_text in field_configs:
            label = wx.StaticText(self, label=label_text)
            vbox.Add(label, 0, wx.ALL, 5)
            if field == 'Password':
                ctrl = wx.TextCtrl(self, style=wx.TE_PASSWORD)
            else:
                ctrl = wx.TextCtrl(self)
            ctrl.SetName(field)
            vbox.Add(ctrl, 0, wx.EXPAND | wx.ALL, 5)
            self.fields[field] = ctrl
        
        # Speech Checkbox
        self.speech_check = wx.CheckBox(self, label="Enable Speech for this server")
        self.speech_check.SetValue(True)
        vbox.Add(self.speech_check, 0, wx.ALL, 5)
        
        # Soundpack Choice
        label_sp = wx.StaticText(self, label="Soundpack:")
        vbox.Add(label_sp, 0, wx.ALL, 5)
        sounds_dir = os.path.join(os.path.dirname(__file__), 'skills', 'teamtalk_manager', 'sounds')
        soundpacks = ['default']
        if os.path.exists(sounds_dir):
            try:
                soundpacks = [d for d in os.listdir(sounds_dir) if os.path.isdir(os.path.join(sounds_dir, d))]
            except Exception: pass
        if not soundpacks: soundpacks = ['default']
        
        self.soundpack_choice = wx.Choice(self, choices=soundpacks)
        if 'default' in soundpacks:
            self.soundpack_choice.SetSelection(soundpacks.index('default'))
        else:
            self.soundpack_choice.SetSelection(0)
        vbox.Add(self.soundpack_choice, 0, wx.EXPAND | wx.ALL, 5)
        
        btn_ok = wx.Button(self, wx.ID_OK, label="Add Server")
        btn_ok.SetName("Add button")
        vbox.Add(btn_ok, 0, wx.ALL | wx.ALIGN_CENTER, 15)
        self.SetSizer(vbox)

    def get_data(self):
        data = {f: self.fields[f].GetValue() for f in self.fields}
        data['speech'] = 'true' if self.speech_check.GetValue() else 'false'
        data['soundpack'] = self.soundpack_choice.GetStringSelection()
        return data

class TelegramTab(wx.Panel):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        label = wx.StaticText(self, label="Telegram Bot Token:")
        vbox.Add(label, 0, wx.ALL, 5)
        self.token = wx.TextCtrl(self, value=config.get('Telegram', 'token', fallback=''))
        self.token.SetName("Bot Token Input")
        vbox.Add(self.token, 0, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(vbox)
        self.token.Bind(wx.EVT_TEXT, self.on_change)

    def on_change(self, event):
        if 'Telegram' not in self.config:
            self.config.add_section('Telegram')
        self.config.set('Telegram', 'token', self.token.GetValue())

class AISettingsTab(wx.Panel):
    def __init__(self, parent, settings):
        super().__init__(parent)
        self.settings = settings
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Provider
        label_provider = wx.StaticText(self, label="AI Provider (e.g., ollama or openai):")
        vbox.Add(label_provider, 0, wx.ALL, 5)
        self.provider = wx.TextCtrl(self, value=settings.get('ai_provider', 'ollama'))
        vbox.Add(self.provider, 0, wx.EXPAND | wx.ALL, 5)
        
        # Endpoint
        label_endpoint = wx.StaticText(self, label="API Endpoint (Base URL):")
        vbox.Add(label_endpoint, 0, wx.ALL, 5)
        self.endpoint = wx.TextCtrl(self, value=settings.get('ai_endpoint', 'http://localhost:11434/v1'))
        vbox.Add(self.endpoint, 0, wx.EXPAND | wx.ALL, 5)
        
        # Model
        label_model = wx.StaticText(self, label="AI Model Name:")
        vbox.Add(label_model, 0, wx.ALL, 5)
        self.model = wx.TextCtrl(self, value=settings.get('ai_model', 'llama3'))
        vbox.Add(self.model, 0, wx.EXPAND | wx.ALL, 5)
        
        # API Key
        label_key = wx.StaticText(self, label="API Key (Leave empty if not required):")
        vbox.Add(label_key, 0, wx.ALL, 5)
        self.key = wx.TextCtrl(self, value=settings.get('ai_api_key', ''), style=wx.TE_PASSWORD)
        vbox.Add(self.key, 0, wx.EXPAND | wx.ALL, 5)
        
        # Enable by default
        self.ai_default = wx.CheckBox(self, label="Enable AI Chatting mode by default on startup")
        self.ai_default.SetValue(settings.get('ai_enabled_by_default', False))
        vbox.Add(self.ai_default, 0, wx.ALL, 5)
        
        self.SetSizer(vbox)
        
        # Bind events to update the settings object directly
        self.provider.Bind(wx.EVT_TEXT, self.sync)
        self.endpoint.Bind(wx.EVT_TEXT, self.sync)
        self.model.Bind(wx.EVT_TEXT, self.sync)
        self.key.Bind(wx.EVT_TEXT, self.sync)
        self.ai_default.Bind(wx.EVT_CHECKBOX, self.sync)

    def sync(self, event):
        self.settings['ai_provider'] = self.provider.GetValue()
        self.settings['ai_endpoint'] = self.endpoint.GetValue()
        self.settings['ai_model'] = self.model.GetValue()
        self.settings['ai_api_key'] = self.key.GetValue()
        self.settings['ai_enabled_by_default'] = self.ai_default.GetValue()

class ServersTab(wx.Panel):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        label = wx.StaticText(self, label="Configured TeamTalk Servers:")
        vbox.Add(label, 0, wx.ALL, 5)
        
        self.listbox = wx.ListBox(self, choices=[s for s in config.sections() if s.lower().startswith('server ')])
        vbox.Add(self.listbox, 1, wx.EXPAND | wx.ALL, 5)
        
        btn_add = wx.Button(self, label="Add New Server")
        btn_add.Bind(wx.EVT_BUTTON, self.on_add)
        vbox.Add(btn_add, 0, wx.EXPAND | wx.ALL, 5)
        
        btn_remove = wx.Button(self, label="Remove Selected Server")
        btn_remove.Bind(wx.EVT_BUTTON, self.on_remove)
        vbox.Add(btn_remove, 0, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(vbox)

    def on_add(self, event):
        dlg = AddServerDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.get_data()
            section = f"server {data['Name']}"
            if section in self.config:
                wx.MessageBox(f"A server named '{data['Name']}' is already configured.", "Error", wx.OK | wx.ICON_ERROR)
                return
            
            self.config.add_section(section)
            for k, v in data.items():
                if k != 'Name':
                    self.config.set(section, k.lower(), v)
            self.listbox.Append(section)
        dlg.Destroy()

    def on_remove(self, event):
        sel = self.listbox.GetSelection()
        if sel != wx.NOT_FOUND:
            name = self.listbox.GetString(sel)
            self.config.remove_section(name)
            self.listbox.Delete(sel)

class SettingsTab(wx.Panel):
    def __init__(self, parent, settings):
        super().__init__(parent)
        self.settings = settings
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        label_user = wx.StaticText(self, label="Default Username:")
        vbox.Add(label_user, 0, wx.ALL, 5)
        self.user = wx.TextCtrl(self, value=settings.get('username', 'User'))
        vbox.Add(self.user, 0, wx.EXPAND | wx.ALL, 5)
        
        label_pin = wx.StaticText(self, label="Notes Security PIN:")
        vbox.Add(label_pin, 0, wx.ALL, 5)
        self.pin = wx.TextCtrl(self, value=settings.get('notes_pin', ''), style=wx.TE_PASSWORD)
        vbox.Add(self.pin, 0, wx.EXPAND | wx.ALL, 5)
        
        # TTS Engine Selection
        vbox.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 10)
        label_engine = wx.StaticText(self, label="TTS Engine:")
        vbox.Add(label_engine, 0, wx.ALL, 5)
        self.engine_choice = wx.Choice(self, choices=["google", "star"])
        current_engine = settings.get('tts_engine', 'google')
        self.engine_choice.SetStringSelection(current_engine)
        vbox.Add(self.engine_choice, 0, wx.EXPAND | wx.ALL, 5)

        # Google TTS Options
        self.google_panel = wx.Panel(self)
        g_vbox = wx.BoxSizer(wx.VERTICAL)
        label_tts = wx.StaticText(self.google_panel, label="Google TTS Language:")
        g_vbox.Add(label_tts, 0, wx.ALL, 5)
        
        self.tts_langs = {"en": "English", "es": "Spanish", "fr": "French", "de": "German", "it": "Italian", "pt": "Portuguese", "ru": "Russian", "ja": "Japanese", "ko": "Korean", "zh-CN": "Chinese (Simplified)", "ar": "Arabic", "hi": "Hindi"}
        display_names = list(self.tts_langs.values())
        self.tts_codes = list(self.tts_langs.keys())
        self.tts_choice = wx.Choice(self.google_panel, choices=display_names)
        current_code = settings.get('tts_lang', 'en')
        if current_code in self.tts_codes:
            self.tts_choice.SetSelection(self.tts_codes.index(current_code))
        else:
            self.tts_choice.SetSelection(0)
        g_vbox.Add(self.tts_choice, 0, wx.EXPAND | wx.ALL, 5)
        self.google_panel.SetSizer(g_vbox)
        vbox.Add(self.google_panel, 0, wx.EXPAND)

        # STAR TTS Options
        self.star_panel = wx.Panel(self)
        s_vbox = wx.BoxSizer(wx.VERTICAL)
        
        label_server = wx.StaticText(self.star_panel, label="STAR Server URL:")
        s_vbox.Add(label_server, 0, wx.ALL, 5)
        self.star_server = wx.TextCtrl(self.star_panel, value=settings.get('star_server', 'http://localhost:5000'))
        s_vbox.Add(self.star_server, 0, wx.EXPAND | wx.ALL, 5)
        
        btn_fetch = wx.Button(self.star_panel, label="Fetch STAR Voices")
        s_vbox.Add(btn_fetch, 0, wx.ALL, 5)
        
        label_voice = wx.StaticText(self.star_panel, label="STAR Voice:")
        s_vbox.Add(label_voice, 0, wx.ALL, 5)
        self.star_voice_choice = wx.Choice(self.star_panel, choices=[])
        s_vbox.Add(self.star_voice_choice, 0, wx.EXPAND | wx.ALL, 5)
        
        self.star_panel.SetSizer(s_vbox)
        vbox.Add(self.star_panel, 0, wx.EXPAND)

        self.SetSizer(vbox)
        
        # Bindings
        self.user.Bind(wx.EVT_TEXT, lambda e: self.settings.update({'username': self.user.GetValue()}))
        self.pin.Bind(wx.EVT_TEXT, lambda e: self.settings.update({'notes_pin': self.pin.GetValue()}))
        self.engine_choice.Bind(wx.EVT_CHOICE, self.on_engine_change)
        self.tts_choice.Bind(wx.EVT_CHOICE, self.on_google_lang_change)
        self.star_server.Bind(wx.EVT_TEXT, lambda e: self.settings.update({'star_server': self.star_server.GetValue()}))
        btn_fetch.Bind(wx.EVT_BUTTON, self.on_fetch_voices)
        self.star_voice_choice.Bind(wx.EVT_CHOICE, self.on_star_voice_change)
        
        self.toggle_panels(current_engine)
        if current_engine == 'star':
            # Pre-populate voice if exists
            saved_voice = settings.get('star_voice', '')
            if saved_voice:
                self.star_voice_choice.Append(saved_voice)
                self.star_voice_choice.SetSelection(0)

    def toggle_panels(self, engine):
        if engine == 'google':
            self.google_panel.Show()
            self.star_panel.Hide()
        else:
            self.google_panel.Hide()
            self.star_panel.Show()
        self.Layout()

    def on_engine_change(self, event):
        engine = self.engine_choice.GetStringSelection()
        self.settings['tts_engine'] = engine
        self.toggle_panels(engine)

    def on_google_lang_change(self, event):
        self.settings['tts_lang'] = self.tts_codes[self.tts_choice.GetSelection()]

    def on_star_voice_change(self, event):
        self.settings['star_voice'] = self.star_voice_choice.GetStringSelection()

    def on_fetch_voices(self, event):
        server = self.star_server.GetValue().strip()
        if not server:
            wx.MessageBox("Please enter a STAR server URL.", "Error", wx.OK | wx.ICON_ERROR)
            return
        
        # STAR uses WebSockets (ws:// or wss://)
        if not server.startswith("ws"):
            wx.MessageBox("STAR server URL must start with ws:// or wss://", "Error", wx.OK | wx.ICON_ERROR)
            return

        import websockets.sync.client
        import json
        try:
            with websockets.sync.client.connect(server, timeout=5) as ws:
                # Send user hello to get voices
                ws.send(json.dumps({"user": 4})) # USER_REVISION = 4
                
                # Wait for voices message
                # We might need to receive a few messages if there's a backlog or status
                for _ in range(5):
                    msg = ws.recv(timeout=2)
                    data = json.loads(msg)
                    if "voices" in data:
                        voices = data["voices"]
                        # STAR voices can be list of strings or list of dicts with 'name'
                        voice_names = []
                        for v in voices:
                            if isinstance(v, dict):
                                voice_names.append(v.get('name', ''))
                            else:
                                voice_names.append(str(v))
                        
                        self.star_voice_choice.Clear()
                        for v in voice_names:
                            self.star_voice_choice.Append(v)
                        
                        if voice_names:
                            self.star_voice_choice.SetSelection(0)
                            self.settings['star_voice'] = voice_names[0]
                        
                        wx.MessageBox(f"Successfully fetched {len(voice_names)} voices.", "Success")
                        return
                
                wx.MessageBox("Could not find 'voices' in server response.", "Error", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            wx.MessageBox(f"Failed to fetch voices: {e}", "Error", wx.OK | wx.ICON_ERROR)

class CustomCmdsTab(wx.Panel):
    def __init__(self, parent, frame):
        super().__init__(parent)
        self.frame = frame
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        label = wx.StaticText(self, label="Custom Command Triggers:")
        vbox.Add(label, 0, wx.ALL, 5)
        
        self.list = wx.ListBox(self, choices=list(frame.cmds.keys()))
        vbox.Add(self.list, 1, wx.EXPAND | wx.ALL, 5)
        
        btn_add = wx.Button(self, label="Add New Trigger")
        btn_add.Bind(wx.EVT_BUTTON, self.on_add)
        vbox.Add(btn_add, 0, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(vbox)

    def on_add(self, event):
        dlg = wx.TextEntryDialog(self, "Trigger keyword:", "Add Custom Command")
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.GetValue().strip().lower()
            if not name: return
            if name in self.frame.cmds:
                wx.MessageBox("This trigger already exists.", "Error", wx.OK | wx.ICON_ERROR)
                return
            self.frame.cmds[name] = {'type': 'shell', 'command': 'echo hello'}
            self.list.Append(name)
        dlg.Destroy()

def run_gui_config():
    app = wx.App()
    ConfigGUI()
    app.MainLoop()

if __name__ == "__main__":
    run_gui_config()
