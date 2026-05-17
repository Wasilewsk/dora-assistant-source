# skills/audio.py
import os
import random
import pygame

# --- Constants for cleaner code ---
MUSIC_FOLDER_NAME = "music"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# SCRIPT_DIR's parent is the 'skills' folder, its parent is the project root
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
MUSIC_FOLDER = os.path.join(PROJECT_ROOT, MUSIC_FOLDER_NAME)

# --- Stop music function ---
def stop_music(assistant, command=None):
    """Calls the assistant's central media stop function."""
    if hasattr(assistant, 'stop_all_media'):
        assistant.stop_all_media(command)
    else:
        # Fallback if for some reason it doesn't exist in assistant
        print("Warning: The 'assistant' object does not have a 'stop_all_media' method.")
        pygame.mixer.music.stop()


# --- Existing functions ---
def play_music(assistant, command=None):
    # Call the assistant's central stop function
    assistant.stop_all_media(command) 
    
    if not os.path.exists(MUSIC_FOLDER):
        assistant.speak(assistant.get_response('music_folder_missing', folder=MUSIC_FOLDER_NAME))
        return

    songs = [f for f in os.listdir(MUSIC_FOLDER) if f.endswith(('.mp3', '.wav'))]
    if not songs:
        assistant.speak(assistant.get_response('music_file_not_found'))
        return

    assistant.current_playlist = songs
    random.shuffle(assistant.current_playlist)
    assistant.current_song_index = 0
    
    song_path = os.path.join(MUSIC_FOLDER, assistant.current_playlist[0])
    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()
    
    song_name = os.path.splitext(assistant.current_playlist[0])[0].replace('_', ' ')
    assistant.speak(assistant.get_response('music_starting', song_name=song_name))

def play_next_song(assistant, command=None):
    if not hasattr(assistant, 'current_playlist') or not assistant.current_playlist:
        assistant.speak(assistant.get_response('music_nothing_to_play'))
        return
    assistant.current_song_index = (assistant.current_song_index + 1) % len(assistant.current_playlist)
    
    song_path = os.path.join(MUSIC_FOLDER, assistant.current_playlist[assistant.current_song_index])
    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()
    song_name = os.path.splitext(assistant.current_playlist[assistant.current_song_index])[0].replace('_', ' ')
    assistant.speak(assistant.get_response('next_media', title=song_name))

def pause_resume_playback(assistant, command=None):
    if pygame.mixer.music.get_busy():
        if hasattr(assistant, 'is_pygame_paused') and assistant.is_pygame_paused:
            pygame.mixer.music.unpause()
            assistant.is_pygame_paused = False
            assistant.speak(assistant.get_response('playback_resumed'))
        else:
            pygame.mixer.music.pause()
            assistant.is_pygame_paused = True
            assistant.speak(assistant.get_response('playback_paused'))
