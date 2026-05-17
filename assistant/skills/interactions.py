# skills/interactions.py
import config_manager

def confirm_user(assistant):
    """Identifies or registers the user upon startup."""
    username = assistant.username
    assistant.speak(assistant.get_response('confirm_user_prompt', USERNAME=username))
    while True:
        confirmation = assistant.listen()
        if not confirmation: continue
        if 'yes' in confirmation:
            assistant.speak(assistant.get_response('confirm_user_success', USERNAME=username))
            return username
        elif 'no' in confirmation:
            assistant.speak(assistant.get_response('confirm_user_new_prompt'))
            break
        else:
            assistant.speak(assistant.get_response('confirm_user_misunderstood'))
    while True:
        new_name = assistant.listen()
        if new_name:
            assistant.speak(assistant.get_response('confirm_user_new_confirm', new_name=new_name.title()))
            name_confirm = assistant.listen()
            if 'yes' in name_confirm:
                confirmed_name = new_name.title()
                assistant.speak(assistant.get_response('confirm_user_new_welcome', new_name=confirmed_name))
                return confirmed_name
            else:
                assistant.speak(assistant.get_response('confirm_user_retry_name'))
        else:
            assistant.speak(assistant.get_response('confirm_user_misunderstood'))

def switch_language(assistant, command=None):
    """Placeholder for language switching, now only supports English."""
    assistant.speak("I only speak English now.")