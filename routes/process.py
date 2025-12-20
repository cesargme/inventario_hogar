from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from auth.basic import verify_credentials
from database.db import get_session
from database.models import Item, Section, User
from routes.inventory import find_item_by_name, find_section_by_name
from utils.llm import prompt
from utils.parsers import parse_llm_commands

router = APIRouter(prefix="/process", tags=["process"])
templates = Jinja2Templates(directory="templates")


SYSTEM_PROMPT = """Eres un asistente para gestionar inventario de alimentos.
El usuario dictará comandos por voz para actualizar su inventario.

IMPORTANTE: Cuando el usuario mencione un item, SIEMPRE usa "create_item" porque NO sabes si existe o no en la base de datos.

Debes devolver un array JSON con los comandos a ejecutar. Formato:

[
  {"action": "create_item", "item": "leche", "quantity": 2, "unit": "L", "section": "refrigerador", "emoji": "🥛", "threshold": 1},
  {"action": "create_item", "item": "huevos", "quantity": 6, "unit": "unidades", "section": "refrigerador", "emoji": "🥚", "threshold": 3},
  {"action": "create_item", "item": "arroz", "quantity": 2, "unit": "kg", "section": "almacen 1", "emoji": "🍚", "threshold": 1}
]

Acciones disponibles:
- create_item: SIEMPRE usa esta acción para cualquier item mencionado. Si el item ya existe, se actualizará automáticamente.
- create_section: crea nueva sección (infiere emoji)

Reglas:
- SIEMPRE usa "create_item" para todos los items mencionados
- Nombres en minúsculas sin tildes (huevos, leche, arroz, etc)
- Inferir unidades apropiadas (kg, L, unidades, gramos, etc)
- Emojis apropiados para cada item (🥛 leche, 🥚 huevos, 🍚 arroz, 🥖 pan, etc)
- Secciones comunes: refrigerador, almacen 1, almacen 2, congelador, despensa
- Threshold razonable (1-3 unidades generalmente)

Responde SOLO con el JSON, sin texto adicional."""


@router.post("/text", response_class=HTMLResponse)
async def process_text(
    request: Request,
    text: str = Form(...),
    user: User = Depends(verify_credentials),
    session: Session = Depends(get_session),
):
    """Procesa texto dictado y ejecuta comandos LLM"""

    # Llamar LLM
    llm_input = f"{SYSTEM_PROMPT}\n\nUsuario dice: {text}"
    llm_response = prompt(llm_input)

    # Parsear comandos
    commands = parse_llm_commands(llm_response)

    if not commands:
        return templates.TemplateResponse(
            "components/feedback.html",
            {
                "request": request,
                "changes": [],
                "errors": [
                    "No se pudieron entender los comandos. Intenta ser más específico."
                ],
            },
        )

    # Ejecutar comandos
    changes = []
    errors = []

    for cmd in commands:
        try:
            action = cmd.get("action")

            if action == "add":
                item = find_item_by_name(session, cmd["item"])
                if item:
                    old_qty = item.quantity
                    item.quantity += cmd["quantity"]
                    item.updated_at = datetime.utcnow()
                    changes.append(
                        f"Agregado: {item.name} {old_qty} → {item.quantity} {item.unit}"
                    )
                else:
                    errors.append(f"Item '{cmd['item']}' no existe (usar create_item)")

            elif action == "set":
                item = find_item_by_name(session, cmd["item"])
                if item:
                    old_qty = item.quantity
                    item.quantity = cmd["quantity"]
                    item.updated_at = datetime.utcnow()
                    changes.append(
                        f"Actualizado: {item.name} {old_qty} → {item.quantity} {item.unit}"
                    )
                else:
                    errors.append(f"Item '{cmd['item']}' no existe")

            elif action == "remove":
                item = find_item_by_name(session, cmd["item"])
                if item:
                    session.delete(item)
                    changes.append(f"Eliminado: {item.name}")
                else:
                    errors.append(f"Item '{cmd['item']}' no existe")

            elif action == "create_item":
                # Buscar si el item ya existe
                existing_item = find_item_by_name(session, cmd["item"])

                if existing_item:
                    # Actualizar item existente
                    old_qty = existing_item.quantity
                    existing_item.quantity = cmd.get("quantity", existing_item.quantity)
                    existing_item.updated_at = datetime.utcnow()
                    changes.append(
                        f"Actualizado: {existing_item.emoji} {existing_item.name} {old_qty} → {existing_item.quantity} {existing_item.unit}"
                    )
                else:
                    # Buscar sección
                    section_name = cmd.get("section", "almacen 1")
                    section = find_section_by_name(session, section_name)

                    if not section:
                        # Crear sección si no existe
                        section = Section(
                            name=section_name.title(),
                            emoji=cmd.get("section_emoji", "📦"),
                        )
                        session.add(section)
                        session.flush()

                    # Crear item nuevo
                    new_item = Item(
                        name=cmd["item"],
                        emoji=cmd.get("emoji", "🍽️"),
                        quantity=cmd.get("quantity", 0),
                        unit=cmd.get("unit", "unidades"),
                        threshold=cmd.get("threshold", 1),
                        section_id=section.id,
                    )
                    session.add(new_item)
                    changes.append(
                        f"Creado: {new_item.emoji} {new_item.name} ({new_item.quantity} {new_item.unit}) en {section.name}"
                    )

            elif action == "create_section":
                section_name = cmd.get("section", "")
                existing = find_section_by_name(session, section_name)

                if not existing:
                    new_section = Section(
                        name=section_name.title(),
                        emoji=cmd.get("emoji", "📦"),
                    )
                    session.add(new_section)
                    changes.append(f"Creada sección: {new_section.emoji} {new_section.name}")
                else:
                    errors.append(f"Sección '{section_name}' ya existe")

        except Exception as e:
            errors.append(f"Error en comando {cmd}: {str(e)}")

    # Commit cambios
    session.commit()

    # Retornar feedback HTML con evento HTMX para invalidar cache
    response = templates.TemplateResponse(
        "components/feedback.html",
        {"request": request, "changes": changes, "errors": errors},
    )

    # Si hubo cambios exitosos, disparar evento para invalidar cache del inventario
    if changes:
        response.headers["HX-Trigger"] = "inventoryUpdated"

    return response
