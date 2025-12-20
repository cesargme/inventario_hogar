from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, func

from auth.basic import verify_credentials
from config.settings import ITEMS_PER_PAGE
from database.db import get_session
from database.models import Item, Section, User
from database.queries import find_item_by_name, find_section_by_name
from utils.serializers import serialize_items_for_template

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
