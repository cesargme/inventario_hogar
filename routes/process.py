from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from auth.basic import verify_credentials
from database.db import get_session
from database.models import Item, ItemHistory, Section, User
from database.queries import find_item_by_name, find_section_by_name
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
- move_item: mueve un item a otra sección. Formato: {"action": "move_item", "item": "leche", "to_section": "refrigerador"}
- change_emoji: cambia emoji de item o sección. Formato: {"action": "change_emoji", "target_type": "item", "target_name": "leche", "emoji": "🥛"} o {"action": "change_emoji", "target_type": "section", "target_name": "refrigerador", "emoji": "❄️"}
- delete_item: elimina un item. Formato: {"action": "delete_item", "item": "leche"}
- delete_section: elimina una sección. Formato: {"action": "delete_section", "section": "almacen 1"}

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
    context: str = Form(None),
    user: User = Depends(verify_credentials),
    session: Session = Depends(get_session),
):
    """Procesa texto dictado y ejecuta comandos LLM"""

    # Preparar contexto para el LLM
    context_info = ""
    if context:
        try:
            import json
            context_data = json.loads(context)
            sections_list = ", ".join([s['name'] for s in context_data.get('sections', [])])
            items_list = ", ".join([i['name'] for i in context_data.get('items', [])])
            context_info = f"\n\nContexto actual del inventario:\n- Secciones disponibles: {sections_list}\n- Items existentes: {items_list}"
        except:
            pass  # Si falla el parseo, continuar sin contexto

    # Llamar LLM con contexto
    llm_input = f"{SYSTEM_PROMPT}{context_info}\n\nUsuario dice: {text}"
    print(f"[LLM] Input: {llm_input}")
    llm_response = prompt(llm_input)
    print(f"[LLM] Response: {llm_response}")

    # Parsear comandos
    commands = parse_llm_commands(llm_response)
    print(f"[LLM] Parsed commands: {commands}")

    if not commands:
        error_msg = "No se pudieron entender los comandos. Intenta ser más específico."
        if llm_response:
            error_msg = f"Error parseando respuesta del LLM. Ver logs del servidor para detalles."
            print(f"[ERROR] No se pudieron parsear comandos de la respuesta: {llm_response}")

        return templates.TemplateResponse(
            "components/feedback.html",
            {
                "request": request,
                "changes": [],
                "errors": [error_msg],
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

                    # Guardar en historial
                    session.add(ItemHistory(item_id=item.id, quantity=item.quantity))

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

                    # Guardar en historial
                    session.add(ItemHistory(item_id=item.id, quantity=item.quantity))

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

                    # Guardar en historial
                    session.add(ItemHistory(item_id=existing_item.id, quantity=existing_item.quantity))

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
                    session.flush()  # Para obtener el ID del nuevo item

                    # Guardar en historial
                    session.add(ItemHistory(item_id=new_item.id, quantity=new_item.quantity))

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

            elif action == "move_item":
                item = find_item_by_name(session, cmd["item"])
                if not item:
                    errors.append(f"Item '{cmd['item']}' no existe")
                else:
                    section_name = cmd.get("to_section", "")
                    new_section = find_section_by_name(session, section_name)

                    if not new_section:
                        errors.append(f"Sección '{section_name}' no existe")
                    else:
                        old_section = item.section.name
                        item.section_id = new_section.id
                        item.updated_at = datetime.utcnow()
                        changes.append(
                            f"Movido: {item.emoji} {item.name} de {old_section} → {new_section.name}"
                        )

            elif action == "change_emoji":
                target_type = cmd.get("target_type")  # "item" o "section"
                target_name = cmd.get("target_name", "")
                new_emoji = cmd.get("emoji", "")

                if target_type == "item":
                    item = find_item_by_name(session, target_name)
                    if item:
                        old_emoji = item.emoji
                        item.emoji = new_emoji
                        item.updated_at = datetime.utcnow()
                        changes.append(f"Emoji cambiado: {item.name} {old_emoji} → {new_emoji}")
                    else:
                        errors.append(f"Item '{target_name}' no existe")

                elif target_type == "section":
                    section = find_section_by_name(session, target_name)
                    if section:
                        old_emoji = section.emoji
                        section.emoji = new_emoji
                        changes.append(f"Emoji cambiado: {section.name} {old_emoji} → {new_emoji}")
                    else:
                        errors.append(f"Sección '{target_name}' no existe")
                else:
                    errors.append(f"target_type '{target_type}' inválido (debe ser 'item' o 'section')")

            elif action == "delete_item":
                item = find_item_by_name(session, cmd["item"])
                if item:
                    item_name = item.name
                    item_emoji = item.emoji
                    session.delete(item)
                    changes.append(f"Eliminado: {item_emoji} {item_name}")
                else:
                    errors.append(f"Item '{cmd['item']}' no existe")

            elif action == "delete_section":
                section_name = cmd.get("section", "")
                section = find_section_by_name(session, section_name)

                if not section:
                    errors.append(f"Sección '{section_name}' no existe")
                else:
                    # Verificar si tiene items
                    from sqlmodel import select
                    items_in_section = session.exec(
                        select(Item).where(Item.section_id == section.id)
                    ).all()

                    if items_in_section:
                        errors.append(
                            f"No se puede eliminar '{section.name}' porque contiene {len(items_in_section)} items. Mueve o elimina los items primero."
                        )
                    else:
                        section_name_display = section.name
                        section_emoji_display = section.emoji
                        session.delete(section)
                        changes.append(f"Eliminada sección: {section_emoji_display} {section_name_display}")

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
