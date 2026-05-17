import threading
import time
import pygame
import os

timer_running = False
timer_thread = None
alarm_active = False

def start_timer(assistant, command):
    global timer_running, timer_thread, alarm_active
    
    # Extract minutes from command
    words = command.split()
    minutes = 0
    for word in words:
        if word.isdigit():
            minutes = int(word)
            break
            
    if minutes <= 0:
        assistant.speak("Please specify the number of minutes for the timer.")
        return

    if timer_running:
        assistant.speak("A timer is already running.")
        return

    assistant.speak(f"Timer set for {minutes} minutes.")
    timer_running = True
    timer_thread = threading.Thread(target=_timer_logic, args=(assistant, minutes), daemon=True)
    timer_thread.start()

def _timer_logic(assistant, minutes):
    global timer_running, alarm_active
    time.sleep(minutes * 60)
    if timer_running:
        alarm_active = True
        assistant.speak("Time's up!")
        _play_alarm(assistant)

def _play_alarm(assistant):
    global alarm_active, timer_running
    while alarm_active:
        assistant.play_sfx('status.wav') # Using an existing sound from the pack
        time.sleep(2)
    timer_running = False

def stop_timer(assistant, command=None):
    global timer_running, alarm_active
    if alarm_active:
        alarm_active = False
        assistant.speak("Timer stopped.")
        return True
    elif timer_running:
        timer_running = False
        assistant.speak("Timer cancelled.")
        return True
    else:
        assistant.speak("No timer is currently running.")
        return False
