# main.py
from assistant import Assistant
import pygame
import updater

if __name__ == "__main__":
    updater.check_for_updates()
    dora = None
    try:
        print("Starting Dora Assistant...")
        dora = Assistant()
        dora.run()
    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
    except Exception as e:
        print(f"\n!!! CRITICAL ERROR in the main program: {e}")
    finally:
        print("Releasing resources and exiting...")
        if dora and hasattr(dora, 'asset_manager') and dora.asset_manager:
            dora.asset_manager.close()
        if pygame.get_init():
            pygame.quit()
        print("Goodbye!")