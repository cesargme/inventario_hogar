from datetime import datetime
import json

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, func

from auth.basic import verify_credentials
from config.settings import ITEMS_PER_PAGE, HISTORY_RECORDS_PER_ITEM
from database.db import get_session
from database.models import Item, ItemHistory, Section, User
from database.queries import find_item_by_name, find_section_by_name
from utils.serializers import serialize_items_for_template
from utils.time import humanize_time

router = APIRouter(prefix="/inventory", tags=["inventory"])
templates = Jinja2Templates(directory="templates")


@router.get("/items")
async def list_items(
    section_id: int | None = Query(None),
    user: User = Depends(verify_credentials),
    session: Session = Depends(get_session),
):
    """Lista todos los items o filtrados por sección"""

    statement = select(Item).order_by(Item.updated_at.desc())

    if section_id:
        statement = statement.where(Item.section_id == section_id)

    items = session.exec(statement).all()

    return {
        "items": [
            {
                "id": item.id,
                "name": item.name,
                "emoji": item.emoji,
                "quantity": item.quantity,
                "unit": item.unit,
                "threshold": item.threshold,
                "section_id": item.section_id,
                "section_name": item.section.name,
                "section_emoji": item.section.emoji,
                "updated_at": item.updated_at.isoformat(),
                "is_below_threshold": item.is_below_threshold,
            }
            for item in items
        ]
    }


@router.get("/sections")
async def list_sections(
    user: User = Depends(verify_credentials),
    session: Session = Depends(get_session),
):
    """Lista todas las secciones"""

    statement = select(Section).order_by(Section.name)
    sections = session.exec(statement).all()

    return {
        "sections": [
            {
                "id": section.id,
                "name": section.name,
                "emoji": section.emoji,
                "created_at": section.created_at.isoformat(),
            }
            for section in sections
        ]
    }


@router.get("/api/items", response_class=HTMLResponse)
async def get_items_paginated(
    request: Request,
    offset: int = Query(0),
    limit: int = Query(ITEMS_PER_PAGE),
    section_id: int | None = Query(None),
    user: User = Depends(verify_credentials),
    session: Session = Depends(get_session),
):
    """
    Retorna items paginados para infinite scroll
    """
    stmt = select(Item).order_by(Item.updated_at.desc())

    if section_id:
        stmt = stmt.where(Item.section_id == section_id)

    stmt = stmt.offset(offset).limit(limit)
    items = session.exec(stmt).all()

    # Preparar data para template
    items_data = serialize_items_for_template(items)

    # Determinar si hay más items por cargar
    has_more = len(items) == limit

    return templates.TemplateResponse(
        "components/items_list.html",
        {
            "request": request,
            "items": items_data,
            "offset": offset + limit,
            "section_id": section_id,
            "has_more": has_more,
        }
    )


@router.get("/api/context", response_class=HTMLResponse)
async def get_context(
    user: User = Depends(verify_credentials),
    session: Session = Depends(get_session),
):
    """
    Retorna <script> con contexto completo para el LLM
    Se carga asíncronamente al entrar a la app
    """
    sections = session.exec(select(Section)).all()
    items = session.exec(select(Item)).all()

    context_data = {
        "sections": [{"id": s.id, "name": s.name, "emoji": s.emoji} for s in sections],
        "items": [{"id": i.id, "name": i.name, "section_id": i.section_id} for i in items]
    }

    context_json = json.dumps(context_data, ensure_ascii=False)

    return f"""
<script>
    window.inventoryContext = {context_json};
    window.contextLoaded = true;
    console.log('Contexto del inventario cargado:', window.inventoryContext);
</script>
"""


@router.get("/item/{item_id}/history-view", response_class=HTMLResponse)
async def get_item_history_view(
    request: Request,
    item_id: int,
    user: User = Depends(verify_credentials),
    session: Session = Depends(get_session),
):
    """Vista completa de historial con infinite scroll"""
    item = session.get(Item, item_id)
    if not item:
        return templates.TemplateResponse(
            "components/error.html",
            {"request": request, "message": "Item no encontrado"}
        )

    # Cargar primer batch de historial directamente
    all_history = session.exec(
        select(ItemHistory)
        .where(ItemHistory.item_id == item_id)
        .order_by(ItemHistory.changed_at.desc())
    ).all()

    # Paginar primer batch
    limit = HISTORY_RECORDS_PER_ITEM
    history = all_history[0:limit]

    # Calcular before/after
    history_data = []
    for i, record in enumerate(history):
        before = all_history[i + 1].quantity if i + 1 < len(all_history) else 0
        after = record.quantity
        history_data.append({
            "before": before,
            "after": after,
            "changed_at": record.changed_at,
            "date_human": humanize_time(record.changed_at)
        })

    has_more = limit < len(all_history)

    return templates.TemplateResponse(
        "components/history_view.html",
        {
            "request": request,
            "item": item,
            "history": history_data,
            "offset": limit,
            "has_more": has_more
        }
    )


@router.get("/api/item/{item_id}/history", response_class=HTMLResponse)
async def get_item_history_paginated(
    request: Request,
    item_id: int,
    offset: int = Query(0),
    limit: int = Query(HISTORY_RECORDS_PER_ITEM),
    user: User = Depends(verify_credentials),
    session: Session = Depends(get_session),
):
    """
    Retorna historial paginado de un item con before/after calculado
    """
    # Obtener todos los registros para calcular before correctamente
    all_history = session.exec(
        select(ItemHistory)
        .where(ItemHistory.item_id == item_id)
        .order_by(ItemHistory.changed_at.desc())
    ).all()

    # Paginar
    history = all_history[offset:offset + limit]

    # Calcular before/after
    history_data = []
    for i, record in enumerate(history):
        actual_index = offset + i
        before = all_history[actual_index + 1].quantity if actual_index + 1 < len(all_history) else 0
        after = record.quantity
        history_data.append({
            "before": before,
            "after": after,
            "changed_at": record.changed_at,
            "date_human": humanize_time(record.changed_at)
        })

    has_more = (offset + limit) < len(all_history)

    return templates.TemplateResponse(
        "components/history_list.html",
        {
            "request": request,
            "history": history_data,
            "item_id": item_id,
            "offset": offset + limit,
            "has_more": has_more
        }
    )
