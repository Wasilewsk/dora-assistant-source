import subprocess
import os
import sys

def check_for_updates():
    """Checks for GitHub updates and pulls them if available."""
    try:
        # Fetch remote updates
        subprocess.check_call(['git', 'fetch', 'origin', 'main'])
        
        # Check if local is behind remote
        # rev-list --count HEAD..origin/main counts commits that are in origin/main but not in HEAD
        behind_count = int(subprocess.check_output(['git', 'rev-list', '--count', 'HEAD..origin/main']).strip())
        
        if behind_count > 0:
            print(f"{behind_count} update(s) available. Updating...")
            
            # Play a notification tone
            try:
                import winsound
                sound_path = os.path.join(os.path.dirname(__file__), 'skills', 'teamtalk_manager', 'sounds', 'default', 'status.wav')
                if os.path.exists(sound_path):
                    winsound.PlaySound(sound_path, winsound.SND_FILENAME)
            except Exception as sound_e:
                print(f"Could not play notification sound: {sound_e}")

            subprocess.check_call(['git', 'pull', 'origin', 'main'])
            print("Update complete. Restarting...")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            print("Already up to date.")
    except Exception as e:
        print(f"Update check failed: {e}")
