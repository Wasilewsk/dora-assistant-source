import sys
import os

# Add assistant dir to path
sys.path.append(os.path.join(os.getcwd(), 'assistant'))

try:
    import wx
    import config_manager
    from gui_main import launch_ui
    print("Imports successful.")
    
    # Simulate a partial assistant object for testing
    class DummyAssistant:
        def __init__(self):
            self._command_map = {'en': {'test': None}}
            
    print("Launching UI...")
    launch_ui(DummyAssistant())
except Exception as e:
    import traceback
    traceback.print_exc()
