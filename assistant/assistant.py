# assistant.py
import pygame
import speech_recognition as sr
import time
import inspect
import tempfile
import os
import threading
import queue
from gtts import gTTS

from asset_manager import AssetManager
import config_manager
import language_manager as lang

from skills import information, audio, system, communication, interactions, time_signal, timer, youtube_gui, custom_manager
from skills.teamtalk_manager import manager as teamtalk_manager

class Assistant:
    def __init__(self):
        print("Initializing Dora Assistant - The Bluebird Project...")
        pygame.init()
        pygame.mixer.init()
        self.settings = config_manager.load_settings()
        self.current_lang = 'en'
        self.username = self.settings.get('username', 'User')
        self.asset_manager = AssetManager('sounds.dat')
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_running = True
        self.is_pygame_paused = False
        self.current_playlist = []
        self.current_song_index = -1
        self.active_tt_server = None
        self._command_map = self._register_commands()
        self.input_queue = queue.Queue()
        print("Assistant initialized.")

    def _register_commands(self):
        return {
            'en': {
                'shut down': system.shutdown_computer,
                'turn off': system.shutdown_computer,
                '/shutdown': system.shutdown_computer,
                'commands': self.list_commands,
                'help': self.list_commands,
                '/help': self.list_commands,
                'switch language': interactions.switch_language,
                'what time is it': information.tell_time,
                '/time': information.tell_time,
                'time signal': time_signal.start_time_signal,
                'stop the time signal': time_signal.stop_time_signal,
                'play music': audio.play_music,
                '/play': audio.play_music,
                'next': audio.play_next_song,
                '/next': audio.play_next_song,
                'stop': audio.stop_music,
                '/stop': audio.stop_music,
                'start teamtalk monitor': teamtalk_manager.start_manager,
                '/start-server': teamtalk_manager.start_manager,
                'stop teamtalk monitor': teamtalk_manager.stop_manager,
                '/stop-server': teamtalk_manager.stop_manager,
                'switch server': teamtalk_manager.switch_active_server,
                '/switch-server': teamtalk_manager.switch_active_server,
                'kick user': teamtalk_manager.kick_user_from_active,
                '/kick': teamtalk_manager.kick_user_from_active,
                'who is online': teamtalk_manager.list_users_on_active,
                '/online': teamtalk_manager.list_users_on_active,
                'send private message': teamtalk_manager.send_private_message_on_active,
                '/pm': teamtalk_manager.send_private_message_on_active,
                'write to the channel': teamtalk_manager.send_channel_message_on_active,
                '/write': teamtalk_manager.send_channel_message_on_active,
                'send broadcast message': teamtalk_manager.send_broadcast_message_on_active,
                '/broadcast': teamtalk_manager.send_broadcast_message_on_active,
                'disconnect': teamtalk_manager.disconnect_from_active,
                '/disconnect': teamtalk_manager.disconnect_from_active,
                'set timer': timer.start_timer,
                '/timer': timer.start_timer,
                'stop the timer': timer.stop_timer,
                'stop the alarm': timer.stop_timer,
                '/stop-timer': timer.stop_timer,
                'play youtube': youtube_gui.play_youtube_video,
                '/play-youtube': youtube_gui.play_youtube_video,
                'add note': custom_manager.add_note,
                '/add-note': custom_manager.add_note,
                'list notes': custom_manager.list_notes,
                '/list-notes': custom_manager.list_notes,
                'delete notes': custom_manager.delete_notes,
                '/delete-notes': custom_manager.delete_notes,
                'open the userinterface': self.open_ui,
                '/open-ui': self.open_ui,
            }
        }

    def open_ui(self, command=None):
        import gui_main
        threading.Thread(target=gui_main.launch_ui, args=(self,), daemon=True).start()
        self.speak("Opening the user interface.")


    def list_commands(self, command=None):
        print("Listing available commands...")
        active_commands = self._command_map.get(self.current_lang, {})
        command_list = list(active_commands.keys())
        commands_str = ", ".join(command_list)
        self.speak(self.get_response('available_commands', commands=commands_str))

    def play_sfx(self, filename):
        try:
            sfx_file_obj = self.asset_manager.get_asset_as_file_like_object(filename)
            if sfx_file_obj: pygame.mixer.Sound(sfx_file_obj).play()
        except Exception as e: print(f"Error playing SFX: {e}")

    def speak(self, text, lang_code=None):
        target_lang = lang_code or self.current_lang
        print(f"Dora ({target_lang}): {text}")
        
        pygame_was_playing = pygame.mixer.music.get_busy()

        if pygame_was_playing:
            pygame.mixer.music.pause()
        
        temp_file_path = None
        sound = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_f: temp_file_path = temp_f.name
            tts = gTTS(text=text, lang=target_lang); tts.save(temp_file_path)
            sound = pygame.mixer.Sound(temp_file_path); sound.play()
            while pygame.mixer.get_busy(): pygame.time.wait(50)
        except Exception as e: print(f"Error during gTTS/Pygame speech: {e}")
        finally:
            if sound: del sound
            if temp_file_path and os.path.exists(temp_file_path):
                time.sleep(0.1)
                try: os.remove(temp_file_path)
                except PermissionError: pass
            
            if pygame_was_playing:
                pygame.mixer.music.unpause()

    def listen(self, timeout=7):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5); print("Listening...")
            self.play_sfx('activate.wav')
            try:
                audio = self.recognizer.listen(source, timeout=timeout); self.play_sfx('deactivate.wav')
                lang_code = lang.get_config_value(self.current_lang, 'LANG_CODE', 'en-US')
                command = self.recognizer.recognize_google(audio, language=lang_code)
                print(f"Recognized: {command}"); return command.lower()
            except Exception: self.play_sfx('deactivate.wav'); return ""

    def get_response(self, key, **kwargs):
        return lang.get_response(self.current_lang, key, **kwargs)

    def stop_all_media(self, command=None):
        print("Stopping all playback...")
        stopped_something = False
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            self.current_playlist = []
            self.current_song_index = -1
            stopped_something = True
        if stopped_something:
            self.speak(self.get_response('playback_stopped'))
            
    def process_command(self, command):
        if not command: return
        
        # Check custom commands first
        cmds = config_manager.load_custom_commands()
        if command.strip() in cmds:
            custom_manager.run_custom_command(self, command)
            return
            
        processed_command = command.replace(" ", "")
        active_commands = self._command_map.get(self.current_lang, {})
        for keyword, func in active_commands.items():
            processed_keyword = keyword.replace(" ", "")
            if processed_keyword in processed_command:
                is_bound_method = inspect.ismethod(func)
                func_params = inspect.signature(func).parameters
                param_count_threshold = 1 if is_bound_method else 1 
                expects_command = 'command' in func_params or len(func_params) > param_count_threshold
                if is_bound_method:
                    if expects_command: func(command)
                    else: func()
                else:
                    if expects_command: func(self, command)
                    else: func(self)
                return
        self.speak(self.get_response('unknown_command'))

    def _terminal_input_loop(self):
        """Threaded function to read user input from the terminal."""
        while self.is_running:
            try:
                user_input = input("User (type command): ").strip()
                if user_input:
                    self.input_queue.put(user_input)
            except EOFError:
                break
            except Exception as e:
                print(f"Terminal input error: {e}")

    def run(self):
        confirmed_username = interactions.confirm_user(self)
        if confirmed_username != self.username:
            self.username = confirmed_username; self.settings['username'] = self.username
            config_manager.save_settings(self.settings)

        # Start the terminal input thread
        threading.Thread(target=self._terminal_input_loop, daemon=True).start()

        r_wake = sr.Recognizer()
        
        while self.is_running:
            # Check for terminal input first
            try:
                while not self.input_queue.empty():
                    typed_command = self.input_queue.get_nowait()
                    print(f"Processing terminal command: {typed_command}")
                    self.process_command(typed_command)
            except queue.Empty:
                pass

            wake_word = lang.get_config_value(self.current_lang, 'WAKE_WORD', 'computer')
            lang_code = lang.get_config_value(self.current_lang, 'LANG_CODE', 'en-US')
            prompt_text = self.get_response('waiting_for_wake_word')
            
            # Using a short timeout for voice listening to allow checking terminal input frequently
            try:
                with self.microphone as source:
                    r_wake.adjust_for_ambient_noise(source, duration=0.5)
                    # Use a shorter listen time to keep the terminal input responsive
                    audio = r_wake.listen(source, phrase_time_limit=3, timeout=1)
                
                query = r_wake.recognize_google(audio, language=lang_code).lower().strip()
                if wake_word in query:
                    print()
                    self.speak(self.get_response('wake_word_ack'))
                    command = self.listen()
                    self.process_command(command)
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                # Normal behavior when quiet
                continue
            except Exception as e: 
                print(f"\nError in main loop: {e}")
                time.sleep(1)
