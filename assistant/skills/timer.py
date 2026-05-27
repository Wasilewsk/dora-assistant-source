import threading
import time
import pygame
import os
import msvcrt
import random
import sys

# Shared state dictionary to ensure all threads see the same values
# We use a dict because it's mutable and easy to share
state = {
    'timer_running': False,
    'alarm_active': False
}

def is_alarm_active():
    return state['alarm_active']

def start_timer(assistant, command):
    # Extract minutes from command
    words = command.split()
    minutes = 0
    requested_sound = None
    
    for i, word in enumerate(words):
        if word.isdigit():
            minutes = int(word)
        if "sound:" in word:
            requested_sound = word.split("sound:")[1]
            
    if minutes <= 0:
        assistant.speak("Please specify the number of minutes for the timer.")
        return

    if state['timer_running']:
        assistant.speak("A timer is already running.")
        return

    assistant.speak(f"Timer set for {minutes} minutes.")
    state['timer_running'] = True
    timer_thread = threading.Thread(target=_timer_logic, args=(assistant, minutes, requested_sound), daemon=True)
    timer_thread.start()

def _timer_logic(assistant, minutes, sound_file=None):
    time.sleep(minutes * 60)
    if state['timer_running']:
        state['alarm_active'] = True
        _play_alarm(assistant, sound_file)

def _play_alarm(assistant, sound_file=None):
    # Try to find an alarm sound in the alarms folder
    alarms_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'alarms')
    alarm_path = None
    
    if sound_file:
        potential_path = os.path.join(alarms_dir, sound_file)
        if os.path.exists(potential_path):
            alarm_path = potential_path

    if not alarm_path and os.path.exists(alarms_dir):
        files = [f for f in os.listdir(alarms_dir) if f.endswith(('.ogg', '.wav', '.mp3'))]
        if files:
            alarm_path = os.path.join(alarms_dir, random.choice(files))
    
    alarm_channel = None
    if alarm_path:
        try:
            alarm_sound = pygame.mixer.Sound(alarm_path)
            alarm_channel = alarm_sound.play(loops=-1)
        except Exception as e:
            print(f"Error playing alarm file: {e}")
            assistant.play_sfx('status.wav')
    else:
        assistant.play_sfx('status.wav')
    
    print("\n" + "="*60)
    print("!!! ALARM TRIGGERED !!!")
    print("TIME IS UP!")
    print("Press ANY KEY in this terminal to stop the alarm.")
    print("="*60 + "\n")
    sys.stdout.flush()
    
    # Critical loop: must react instantly to state change or keypress
    while state['alarm_active']:
        # Check for keyboard input in the terminal
        if msvcrt.kbhit():
            msvcrt.getch() # consume the key
            print("Keypress detected. Stopping alarm...")
            state['alarm_active'] = False
            break
        
        # Check if the channel stopped but should still be playing
        if alarm_channel and not alarm_channel.get_busy() and state['alarm_active']:
            alarm_channel.play(loops=-1)
            
        time.sleep(0.05)
    
    # Final cleanup
    if alarm_channel:
        alarm_channel.stop()
    pygame.mixer.stop()
    
    print("Alarm silenced.")
    sys.stdout.flush()
    assistant.speak("Alarm stopped.")
    state['timer_running'] = False
    state['alarm_active'] = False

def stop_timer(assistant, command=None):
    if state['alarm_active']:
        state['alarm_active'] = False
        print("Alarm stop requested via command.")
        return True
    elif state['timer_running']:
        state['timer_running'] = False
        assistant.speak("Timer cancelled.")
        return True
    else:
        return False
