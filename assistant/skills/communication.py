# skills/communication.py

import asyncio
import telegram
import os
import time
from pydub import AudioSegment
import requests
import base64

def send_telegram_message(assistant, message_text):
    """Sends a text message to the configured Telegram chat."""
    async def _send():
        try:
            if assistant.telegram_token == "YOUR_NEW_BOT_TOKEN_HERE" or assistant.telegram_chat_id == "YOUR_CHAT_ID_HERE":
                assistant.speak("Telegram settings are missing in config.ini.")
                return
            bot = telegram.Bot(token=assistant.telegram_token)
            await bot.send_message(chat_id=assistant.telegram_chat_id, text=message_text)
            assistant.speak(assistant.get_response('notification_sent'))
        except Exception as e:
            print(f"Telegram error: {e}")
            assistant.speak(assistant.get_response('notification_error'))
    asyncio.run(_send())

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
        response.raise_for_status() # Throw error if status code is not 2xx
        data = response.json()
        
        # Different APIs may return the answer on different keys
        return data.get("answer") or data.get("text", "Did not receive a valid response.")
        
    except requests.RequestException as e:
        raise RuntimeError(f"Network error: {e}")
    except (KeyError, ValueError, IndexError) as e:
        raise RuntimeError(f"Invalid response from AI provider: {e}")

# Note: Monitoring Telegram messages (check_telegram_updates) is a more complex,
# background process. It's best handled in `assistant.py` or a dedicated 
# `background_tasks.py` module. The `send_telegram_message` above focuses 
# on manual message sending.