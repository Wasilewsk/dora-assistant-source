# skills/time_signal.py
import threading
import time
import datetime

signal_thread = None
is_signal_running = False

def _signal_loop(assistant, interval_minutes):
    """
    Intelligent time signal loop. Calculates the next due time and
    adjusts the first wait to it.
    """
    global is_signal_running
    
    # --- Intelligent part: calculating the first wait ---
    now = datetime.datetime.now()
    
    # How many minutes have passed in the hour since the last interval?
    minutes_past_interval = now.minute % interval_minutes
    
    # How many minutes to wait until the next round time?
    wait_minutes = interval_minutes - minutes_past_interval
    
    # How many seconds to wait (subtracting the current seconds)?
    first_wait_seconds = (wait_minutes * 60) - now.second
    
    print(f"\nTime Signal: The next signal is due in {first_wait_seconds:.0f} seconds.")
    time.sleep(first_wait_seconds)
    
    if not is_signal_running: return # If it was stopped in the meantime

    # --- First signal ---
    now = datetime.datetime.now()
    hour_12_str = now.strftime("%I")
    hour_12 = hour_12_str.lstrip('0') if hour_12_str.startswith('0') else hour_12_str
    minute = now.strftime("%M")
    ampm = now.strftime("%p")
    assistant.speak(assistant.get_response('time_signal_announce', username=assistant.username, hour_12=hour_12, minute=minute, ampm=ampm))

    # --- Normal loop from here on, with fixed interval ---
    interval_seconds = interval_minutes * 60
    while is_signal_running:
        time.sleep(interval_seconds)
        if not is_signal_running:
            break
        
        now = datetime.datetime.now()
        hour_12_str = now.strftime("%I")
        hour_12 = hour_12_str.lstrip('0') if hour_12_str.startswith('0') else hour_12_str
        minute = now.strftime("%M")
        ampm = now.strftime("%p")
        assistant.speak(assistant.get_response('time_signal_announce', username=assistant.username, hour_12=hour_12, minute=minute, ampm=ampm))

def start_time_signal(assistant, command=None):
    global signal_thread, is_signal_running
    if is_signal_running:
        assistant.speak(assistant.get_response('time_signal_already_running'))
        return

    assistant.speak(assistant.get_response('time_signal_prompt'))
    response = assistant.listen().lower()

    interval_minutes = 0
    if '1' in response or 'one' in response or 'quarter' in response:
        interval_minutes = 15
    elif '2' in response or 'two' in response or 'half' in response:
        interval_minutes = 30
    elif '3' in response or 'three' in response or 'free' in response or 'full' in response or 'hour' in response:
        interval_minutes = 60
    
    if interval_minutes > 0:
        is_signal_running = True
        signal_thread = threading.Thread(target=_signal_loop, args=(assistant, interval_minutes), daemon=True)
        signal_thread.start()
        assistant.speak(assistant.get_response('time_signal_started', interval=interval_minutes))
    else:
        assistant.speak(assistant.get_response('unknown_command'))

def stop_time_signal(assistant, command=None):
    global is_signal_running
    if is_signal_running:
        is_signal_running = False
        assistant.speak(assistant.get_response('time_signal_stopped'))
    else:
        assistant.speak(assistant.get_response('time_signal_not_running'))