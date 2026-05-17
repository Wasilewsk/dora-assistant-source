# configure.py
import configparser
import os
import json

# Base directory in user profile
BASE_CONF_DIR = os.path.join(os.path.expanduser("~"), ".assistantconf")

# Ensure the directory exists
if not os.path.exists(BASE_CONF_DIR):
    os.makedirs(BASE_CONF_DIR)

CONFIG_FILE = os.path.join(BASE_CONF_DIR, 'config.ini')
SETTINGS_FILE = os.path.join(BASE_CONF_DIR, 'settings.json')

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def setup_telegram(config):
    print("\n--- Telegram Configuration ---")
    if 'Telegram' not in config:
        config['Telegram'] = {}
    
    token = input(f"Enter Telegram Bot Token [{config['Telegram'].get('token', 'YOUR_TOKEN')}]: ")
    if token: config['Telegram']['token'] = token
    
    chat_id = input(f"Enter Telegram Chat ID [{config['Telegram'].get('chat_id', 'YOUR_CHAT_ID')}]: ")
    if chat_id: config['Telegram']['chat_id'] = chat_id

def add_server(config):
    print("\n--- Add TeamTalk Server ---")
    name = input("Enter a friendly name for this server (e.g., MyServer): ")
    if not name: return
    
    section = f"server {name}"
    config[section] = {}
    config[section]['host'] = input("Host/IP: ")
    config[section]['tcpport'] = input("TCP Port [10333]: ") or "10333"
    config[section]['udpport'] = input("UDP Port [10333]: ") or "10333"
    config[section]['nickname'] = input("Nickname: ")
    config[section]['username'] = input("Username (optional): ")
    config[section]['password'] = input("Password (optional): ")
    config[section]['channel'] = input("Channel to join [/]: ") or "/"
    config[section]['soundpack'] = input("Soundpack (default/electron/firestar/etc.) [default]: ") or "default"
    config[section]['speech'] = input("Enable speech for this server? (true/false) [true]: ") or "true"
    config[section]['log'] = input("Enable logging for this server? (true/false) [true]: ") or "true"

def list_servers(config):
    print("\n--- Configured Servers ---")
    servers = [s for s in config.sections() if s.lower().startswith('server ')]
    if not servers:
        print("No servers configured.")
        return []
    for i, s in enumerate(servers):
        print(f"{i+1}. {s.replace('server ', '')}")
    return servers

def remove_server(config):
    servers = list_servers(config)
    if not servers: return
    try:
        choice = int(input("\nEnter the number of the server to remove (0 to cancel): "))
        if 0 < choice <= len(servers):
            config.remove_section(servers[choice-1])
            print("Server removed.")
    except ValueError:
        print("Invalid input.")

def setup_user_settings():
    print("\n--- User Settings ---")
    settings = {}
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings = json.load(f)
    
    username = input(f"Enter your name [{settings.get('username', 'User')}]: ")
    if username: settings['username'] = username
    
    settings['last_lang'] = 'en' # Force English
    
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)
    print("Settings saved to settings.json")

def main():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE, encoding='utf-8')
    
    while True:
        clear_screen()
        print("====================================")
        print("     Dora Assistant Configuration   ")
        print("====================================")
        print("1. Configure Telegram")
        print("2. Add TeamTalk Server")
        print("3. List/Remove TeamTalk Servers")
        print("4. Configure User Settings")
        print("5. Save and Exit")
        print("6. Exit without saving")
        
        choice = input("\nSelect an option: ")
        
        if choice == '1':
            setup_telegram(config)
        elif choice == '2':
            add_server(config)
        elif choice == '3':
            remove_server(config)
        elif choice == '4':
            setup_user_settings()
        elif choice == '5':
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                config.write(f)
            print(f"\nConfiguration saved to {CONFIG_FILE}")
            setup_user_settings() # Ensure settings.json is also updated/created
            break
        elif choice == '6':
            break
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
