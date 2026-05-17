import subprocess
import os
import sys

def check_for_updates():
    """Checks for GitHub updates and pulls them if available."""
    try:
        # Fetch remote updates
        subprocess.check_call(['git', 'fetch', 'origin', 'main'])
        
        # Check if local is behind remote
        local_rev = subprocess.check_output(['git', 'rev-parse', 'main']).strip()
        remote_rev = subprocess.check_output(['git', 'rev-parse', 'origin/main']).strip()
        
        if local_rev != remote_rev:
            print("Update available. Updating...")
            subprocess.check_call(['git', 'pull', 'origin', 'main'])
            print("Update complete. Restarting...")
            os.execv(sys.executable, ['python'] + sys.argv)
    except Exception as e:
        print(f"Update check failed: {e}")
