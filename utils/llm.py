import requests
import json
import dotenv
import os

dotenv.load_dotenv()

def prompt(message):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": "ibm-granite/granite-4.0-h-micro",
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ]
        })
    )

    result = response.json()

    # Manejo de errores de la API
    if "error" in result:
        raise ValueError(f"OpenRouter API Error: {result['error']}")

    if "choices" not in result or len(result["choices"]) == 0:
        raise ValueError(f"Unexpected API response: {result}")

    return result['choices'][0]['message']['content']


if __name__ == "__main__":
    print(prompt("Hola, ¿cómo estás?"))


