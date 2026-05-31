# skills/interactions.py

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

def toggle_ai_mode(assistant, command):
    """Toggles the AI chatting mode."""
    if 'ai-on' in command or 'enable' in command or 'on' in command:
        assistant.ai_mode = True
        assistant.speak("AI mode is now enabled. You can now chat with me normally.")
    elif 'ai-off' in command or 'disable' in command or 'off' in command:
        assistant.ai_mode = False
        assistant.speak("AI mode is now disabled.")
    else:
        # Toggle if no specific instruction
        assistant.ai_mode = not assistant.ai_mode
        state = "enabled" if assistant.ai_mode else "disabled"
        assistant.speak(f"AI mode is now {state}.")