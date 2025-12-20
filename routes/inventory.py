from datetime import datetime
import json

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select, func

from auth.basic import verify_credentials
from config.settings import ITEMS_PER_PAGE, HISTORY_RECORDS_PER_ITEM
from config.database.db import get_session
from config.database.models import Item, ItemHistory, Section, User
from config.database.queries import find_item_by_name, find_section_by_name
from utils.serializers import serialize_items_for_template
from utils.time import humanize_time

router = APIRouter(prefix="/inventory", tags=["inventory"])

# Lazy import to avoid circular dependency
def get_catalog():
    import jinjax
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")
    # Get or create catalog
    if "catalog" not in templates.env.globals:
        catalog = jinjax.Catalog(jinja_env=templates.env)
        catalog.add_folder("components")
        templates.env.globals["catalog"] = catalog
    return templates.env.globals["catalog"]


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

    # 🆕 Usar componente JinjaX
    return HTMLResponse(
        get_catalog().render(
            "features/ItemsList",
            items=items_data,
            offset=offset + limit,
            section_id=section_id,
            has_more=has_more
        )
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
        return HTMLResponse("<div class='text-red-500 p-4'>Item no encontrado</div>")

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

    # 🆕 Usar componente JinjaX
    return HTMLResponse(
        get_catalog().render(
            "features/HistoryView",
            item=item,
            history=history_data,
            offset=limit,
            has_more=has_more
        )
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

    # 🆕 Usar componente JinjaX
    return HTMLResponse(
        get_catalog().render(
            "features/HistoryList",
            history=history_data,
            item_id=item_id,
            offset=offset + limit,
            has_more=has_more
        )
    )


@router.get("/api/items/batch-history-views")
async def get_batch_history_views(
    item_ids: str = Query(...),
    user: User = Depends(verify_credentials),
    session: Session = Depends(get_session),
):
    """
    Retorna múltiples history-views en una sola llamada
    item_ids: string separado por comas (ej: "1,2,3,4,5")
    """
    ids = [int(id.strip()) for id in item_ids.split(",") if id.strip()]

    result = {}
    for item_id in ids:
        item = session.get(Item, item_id)
        if not item:
            continue

        # Cargar primer batch de historial
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

        # Renderizar componente
        html = get_catalog().render(
            "features/HistoryView",
            item=item,
            history=history_data,
            offset=limit,
            has_more=has_more
        )

        result[str(item_id)] = html

    return result
