# skills/teamtalk_manager/manager.py
import threading
import configparser
import os
import re
import TeamTalk5
from .server_handler import ServerHandler

bot_instances = {}

def load_server_configs():
    filepath = 'config.ini'
    if not os.path.exists(filepath): return []
    config = configparser.ConfigParser()
    config.read(filepath, encoding='utf-8')
    servers_list = []
    for section in config.sections():
        if section.lower().startswith('server '):
            server_name = section.split(' ', 1)[1]
            server_data = dict(config[section])
            server_data['server_name'] = server_name
            servers_list.append(server_data)
    return servers_list

def start_manager(assistant, command=None):
    global bot_instances
    if bot_instances:
        assistant.speak(assistant.get_response('tt_manager_already_running'))
        return
    server_configs = load_server_configs()
    if not server_configs:
        assistant.speak(assistant.get_response('tt_no_servers_configured'))
        return
    count = 0
    for config in server_configs:
        server_name = config['server_name']
        bot = ServerHandler(assistant, config)
        bot_instances[server_name.lower()] = bot
        thread = threading.Thread(target=bot.start, daemon=True)
        thread.start()
        count += 1
    if server_configs:
        assistant.active_tt_server = server_configs[0]['server_name'].lower()
        print(f"Default active server: {assistant.active_tt_server}")
    if count > 0:
        assistant.speak(assistant.get_response('tt_monitoring_started', count=count))

def stop_manager(assistant, command=None):
    global bot_instances
    if not bot_instances:
        assistant.speak(assistant.get_response('tt_manager_not_running'))
        return
    for bot in bot_instances.values():
        bot.stop()
    bot_instances.clear()
    assistant.active_tt_server = None
    assistant.speak(assistant.get_response('tt_monitoring_stopped'))

def switch_active_server(assistant, command=None):
    if not bot_instances:
        assistant.speak(assistant.get_response('tt_manager_not_running'))
        return
    server_list = list(bot_instances.keys())
    servers_str = " ".join([f"{i + 1}: {name}." for i, name in enumerate(server_list)])
    assistant.speak(assistant.get_response('tt_switch_server_prompt', servers_list=servers_str))
    response = assistant.listen()
    if not response: return
    try:
        choice_str = utils.text_to_number(response)
        choice_index = int(choice_str) - 1
        if 0 <= choice_index < len(server_list):
            assistant.active_tt_server = server_list[choice_index]
            assistant.speak(assistant.get_response('tt_active_server_switched', server=assistant.active_tt_server))
        else:
            assistant.speak(assistant.get_response('tt_invalid_number'))
    except (ValueError, IndexError):
        assistant.speak(assistant.get_response('unknown_command'))

def _get_active_bot(assistant):
    if not assistant.active_tt_server:
        assistant.speak(assistant.get_response('tt_active_server_none'))
        return None
    bot = bot_instances.get(assistant.active_tt_server)
    if not bot:
        assistant.speak(assistant.get_response('tt_active_server_error', server=assistant.active_tt_server))
        return None
    return bot

def send_private_message_on_active(assistant, command=None):
    bot = _get_active_bot(assistant)
    if not bot: return
    users = bot.get_users_in_channel()
    if not users:
        assistant.speak(assistant.get_response('tt_no_users_in_channel'))
        return
    user_map = {i + 1: TeamTalk5.ttstr(user.szNickname) for i, user in enumerate(users)}
    users_str = " ".join([f"{i}: {name}." for i, name in user_map.items()])
    assistant.speak(assistant.get_response('tt_send_pm_prompt', users_list=users_str))
    response_num = assistant.listen()
    if not response_num: return
    try:
        choice_str = utils.text_to_number(response_num)
        recipient_nickname = user_map[int(choice_str)]
        assistant.speak(assistant.get_response('tt_send_pm_prompt_message', recipient=recipient_nickname))
        message_text = assistant.listen()
        if message_text and bot.send_pm(recipient_nickname, message_text):
            assistant.speak(assistant.get_response('tt_message_sent'))
        else:
            assistant.speak(assistant.get_response('tt_message_failed'))
    except (ValueError, IndexError, KeyError):
        assistant.speak(assistant.get_response('unknown_command'))

def send_channel_message_on_active(assistant, command):
    bot = _get_active_bot(assistant)
    if not bot: return
    message = command.lower().replace("write to the channel that", "").strip()
    if message:
        bot.send_cm(message)
        assistant.speak(assistant.get_response('tt_channel_message_sent'))
    else:
        assistant.speak(assistant.get_response('tt_channel_message_prompt'))
        message_text = assistant.listen()
        if message_text:
            bot.send_cm(message_text)
            assistant.speak(assistant.get_response('tt_channel_message_sent'))

def kick_user_from_active(assistant, command):
    bot = _get_active_bot(assistant)
    if not bot: return
    name_to_kick = command.lower().replace("kick user", "").strip()
    if bot.execute_kick(name_to_kick):
        assistant.speak(assistant.get_response('tt_user_kicked', user=name_to_kick))
    else:
        assistant.speak(assistant.get_response('tt_user_not_found_on_active', user=name_to_kick))

def list_users_on_active(assistant, command=None):
    bot = _get_active_bot(assistant)
    if not bot: return
    user_list = bot.get_users_in_channel_text()
    if user_list:
        assistant.speak(assistant.get_response('tt_users_in_channel', users_list=user_list))
    else:
        assistant.speak(assistant.get_response('tt_channel_is_empty'))

def send_broadcast_message_on_active(assistant, command):
    bot = _get_active_bot(assistant)
    if not bot: return
    message = command.lower().replace("send broadcast message that", "").strip()
    if message:
        bot.send_bm(message)
        assistant.speak(assistant.get_response('tt_broadcast_sent'))

def disconnect_from_active(assistant, command=None):
    bot = _get_active_bot(assistant)
    if not bot: return
    server_name_to_disconnect = assistant.active_tt_server
    bot.stop()
    del bot_instances[server_name_to_disconnect]
    if bot_instances:
        assistant.active_tt_server = list(bot_instances.keys())[0]
        assistant.speak(assistant.get_response('tt_disconnected_new_active', server=assistant.active_tt_server))
    else:
        assistant.active_tt_server = None
        assistant.speak(assistant.get_response('tt_disconnected_last_one'))