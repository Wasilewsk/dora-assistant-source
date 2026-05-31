import os
import time
import requests
import threading

def _send_raw_telegram(token, chat_id, text):
    if not token or not chat_id or not text:
        return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception as e:
        print(f"Telegram send error: {e}")

def send_telegram_message(assistant, command):
    if not assistant.telegram_token or not assistant.telegram_chat_id:
        assistant.speak(assistant.get_response('notification_error'))
        return
    message_text = command.lower().replace("send notification that", "").replace("send notification", "").strip()
    if not message_text:
        assistant.speak("What message should I send?")
        message_text = assistant.listen()
        if not message_text: return
    _send_raw_telegram(assistant.telegram_token, assistant.telegram_chat_id, message_text)
    assistant.speak(assistant.get_response('notification_sent'))

def send_telegram_notification(assistant, text):
    _send_raw_telegram(assistant.telegram_token, assistant.telegram_chat_id, text)

def start_chatbot_mode(assistant):
    """Starts the chatbot mode."""
    assistant.speak(assistant.get_response('chatbot_start'))

    while True:
        user_input = assistant.listen()
        if not user_input:
            continue

        exit_words_en = ['exit', 'that\'s enough', 'finish']
        should_exit = False

        if any(word in user_input for word in exit_words_en):
            assistant.speak(assistant.get_response('chatbot_exit'))
            break

        try:
            ai_response = query_ai(user_input, assistant.chatbot_model)
            assistant.speak(ai_response)
        except Exception as e:
            print(f"Chatbot error: {e}")
            assistant.speak(assistant.get_response('chatbot_error'))

def query_ai(prompt: str, model_id: int):
    """Queries an AI model with the given prompt."""
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("No text provided for query.")

    endpoints = [
        "https://bj-copilot-microsoft.vercel.app/",
        "https://gemini-1-5-flash.bjcoderx.workers.dev/",
    ]

    if model_id < 0 or model_id >= len(endpoints):
        raise ValueError("Invalid model ID.")

    try:
        model_name = "Copilot" if model_id == 0 else "Gemini"
        print(f"AI query with {model_name} model...")

        response = requests.get(endpoints[model_id], params={"text": prompt}, timeout=30)
        response.raise_for_status()
        data = response.json()

        return data.get("answer") or data.get("text", "Did not receive a valid response.")

    except requests.RequestException as e:
        raise RuntimeError(f"Network error: {e}")
    except (KeyError, ValueError, IndexError) as e:
        raise RuntimeError(f"Invalid response from AI provider: {e}")
