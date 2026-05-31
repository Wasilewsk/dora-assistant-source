import pyautogui
import os
import base64
import io

def take_screenshot(assistant, filename="screenshot.png"):
    """Takes a screenshot and saves it."""
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    assistant.play_sfx('Screenshot.mp3')
    return filename

def get_screenshot_base64(assistant):
    """Takes a screenshot and returns it as a base64 string."""
    screenshot = pyautogui.screenshot()
    assistant.play_sfx('Screenshot.mp3')
    buffered = io.BytesIO()
    screenshot.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def click_on_screen(x, y):
    """Clicks on the specified coordinates."""
    pyautogui.click(x, y)
    return f"Clicked at {x}, {y}"

def type_text(text):
    """Types the specified text."""
    pyautogui.typewrite(text)
    return f"Typed: {text}"

def move_mouse(x, y):
    """Moves the mouse to the specified coordinates."""
    pyautogui.moveTo(x, y)
    return f"Moved mouse to {x}, {y}"

def describe_screen(assistant):
    """Sends a screenshot to the AI and asks it to describe what it sees."""
    assistant.speak(assistant.get_response('gui_describing'))
    img_b64 = get_screenshot_base64(assistant)
    
    # We need to update ai_manager to handle this
    import ai_manager
    prompt = "Look at this screenshot of my screen. What do you see? Please describe the main windows and content."
    response = ai_manager.get_ai_response(prompt, assistant, image_b64=img_b64)
    assistant.speak(response)

def interact_with_gui(assistant, command):
    """Parses a command for GUI interaction and executes it."""
    # This is a bit complex, might need AI to help parse the action
    # For now, let's let the AI handle it if we send it the command and screen context
    assistant.speak(assistant.get_response('gui_analyzing'))
    img_b64 = get_screenshot_base64(assistant)
    
    import ai_manager
    prompt = f"User wants to: {command}. Look at the screenshot and tell me the coordinates (x, y) to click or what to type. Format your response as a JSON: {{\"action\": \"click\", \"x\": 100, \"y\": 200}} or {{\"action\": \"type\", \"text\": \"hello\"}}."
    response_text = ai_manager.get_ai_response(prompt, assistant, image_b64=img_b64)
    
    try:
        import json
        # Extract JSON from response if AI added text
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start != -1 and end != -1:
            action_data = json.loads(response_text[start:end])
            action = action_data.get('action')
            if action == 'click':
                click_on_screen(action_data['x'], action_data['y'])
                assistant.speak(assistant.get_response('gui_action_success'))
            elif action == 'type':
                type_text(action_data['text'])
                assistant.speak(assistant.get_response('gui_action_success'))
            else:
                assistant.speak(assistant.get_response('gui_action_failed'))
        else:
            assistant.speak(assistant.get_response('gui_action_failed'))
    except Exception as e:
        print(f"Error interacting with GUI: {e}")
        assistant.speak(assistant.get_response('gui_action_failed'))
