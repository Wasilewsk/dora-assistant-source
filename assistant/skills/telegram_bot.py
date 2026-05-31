import threading
import time
import requests

_polling_active = False
_last_update_id = 0

def start_polling(assistant):
    global _polling_active
    if _polling_active:
        return
    _polling_active = True
    threading.Thread(target=_polling_loop, args=(assistant,), daemon=True).start()
    print("Telegram polling started.")

def stop_polling():
    global _polling_active
    _polling_active = False

def _polling_loop(assistant):
    global _last_update_id
    while _polling_active:
        try:
            if not assistant.telegram_token:
                time.sleep(5)
                continue
            url = f"https://api.telegram.org/bot{assistant.telegram_token}/getUpdates"
            params = {"offset": _last_update_id + 1, "timeout": 30}
            resp = requests.get(url, params=params, timeout=35)
            data = resp.json()
            if data.get("ok"):
                for update in data.get("result", []):
                    _last_update_id = update["update_id"]
                    msg = update.get("message", {})
                    chat_id = msg.get("chat", {}).get("id")
                    text = msg.get("text", "")
                    if chat_id and text:
                        _handle_message(assistant, str(chat_id), text)
        except requests.Timeout:
            pass
        except Exception as e:
            print(f"Telegram polling error: {e}")
            time.sleep(5)

def _handle_message(assistant, chat_id, text):
    from skills import communication, information
    import ai_manager

    text_lower = text.lower().strip()
    assistant._telegram_chat_id = chat_id

    try:
        if text_lower in ['/start', '/help', 'help', 'commands']:
            cmds = list(assistant._command_map.get('en', {}).keys())
            reply = "Dora Assistant\nCommands: " + ", ".join(sorted(cmds))
            communication._send_raw_telegram(assistant.telegram_token, chat_id, reply)
        elif text_lower in ['/time', 'time', 'what time is it']:
            information.tell_time(assistant)
        else:
            if assistant.ai_mode:
                response = ai_manager.get_ai_response(text, assistant)
                communication._send_raw_telegram(assistant.telegram_token, chat_id, response)
            else:
                assistant.process_command(text)
    finally:
        assistant._telegram_chat_id = None
