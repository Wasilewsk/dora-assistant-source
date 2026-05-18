import requests
import json
import config_manager

def get_ai_response(prompt, assistant=None):
    """Fetches a response from the configured AI provider."""
    settings = config_manager.load_settings()
    provider = settings.get('ai_provider', 'ollama').lower()
    endpoint = settings.get('ai_endpoint', 'http://localhost:11434/v1')
    model = settings.get('ai_model', 'llama3')
    api_key = settings.get('ai_api_key', '')

    try:
        if provider == 'ollama' or provider == 'openai':
            # Both Ollama (with /v1) and OpenAI use the same chat completion format
            headers = {
                "Content-Type": "application/json",
            }
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are Dora, a helpful and friendly virtual assistant. Keep your responses concise and suitable for text-to-speech."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            }
            
            endpoint_url = f"{endpoint.rstrip('/')}/chat/completions"
            # Ensure we don't double up /v1 if already present, but Ollama usually needs it
            if provider == 'ollama' and '/v1' not in endpoint_url:
                # If the user provided just http://localhost:11434, add /v1
                endpoint_url = f"{endpoint.rstrip('/')}/v1/chat/completions"
            
            response = requests.post(endpoint_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content'].strip()
        else:
            return f"Error: Unknown AI provider '{provider}'"
    except Exception as e:
        return f"AI error: {str(e)}"
