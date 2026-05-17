import threading
import gui_player

def play_youtube_video(assistant, command):
    """Parses video link or triggers GUI dialog for URL."""
    
    video_url = None
    for part in command.split():
        if "http" in part:
            video_url = part
            break
            
    assistant.speak(f"Opening YouTube Player.")
    
    # Launch GUI in a separate thread.
    # If video_url is None, gui_player will show the input dialog.
    threading.Thread(target=gui_player.launch_player, args=(video_url,), daemon=True).start()
