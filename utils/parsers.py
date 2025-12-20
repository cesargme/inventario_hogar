import json
from typing import Any


def parse_llm_commands(llm_response: str) -> list[dict[str, Any]]:
    """
    Parsea la respuesta del LLM y extrae comandos JSON.

    Espera formato:
    [
      {"action": "add", "item": "leche", "quantity": 2, "unit": "L"},
      {"action": "set", "item": "huevos", "quantity": 6}
    ]
    """
    try:
        # Intentar parsear JSON directo
        commands = json.loads(llm_response)

        # Si es un objeto único, convertirlo a lista
        if isinstance(commands, dict):
            commands = [commands]

        if not isinstance(commands, list):
            return []

        # Validar estructura básica
        valid_commands = []
        for cmd in commands:
            if isinstance(cmd, dict) and "action" in cmd:
                valid_commands.append(cmd)

        return valid_commands

    except json.JSONDecodeError:
        # Si no es JSON válido, buscar JSON dentro del texto
        try:
            start = llm_response.find("[")
            end = llm_response.rfind("]") + 1

            if start != -1 and end > start:
                json_str = llm_response[start:end]
                commands = json.loads(json_str)

                if isinstance(commands, list):
                    return [cmd for cmd in commands if isinstance(cmd, dict) and "action" in cmd]
        except:
            pass

        return []
