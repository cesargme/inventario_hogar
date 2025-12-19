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
    return response.json()['choices'][0]['message']['content']


if __name__ == "__main__":
    print(prompt("Hola, ¿cómo estás?"))


