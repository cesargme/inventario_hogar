from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func

from auth.basic import verify_credentials
from database.db import get_session
from database.models import Item, Section, User

router = APIRouter(prefix="/inventory", tags=["inventory"])


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


def find_item_by_name(session: Session, name: str) -> Item | None:
    """Busca item por nombre (case-insensitive)"""
    statement = select(Item).where(func.lower(Item.name) == name.lower())
    return session.exec(statement).first()


def find_section_by_name(session: Session, name: str) -> Section | None:
    """Busca sección por nombre (case-insensitive)"""
    statement = select(Section).where(func.lower(Section.name) == name.lower())
    return session.exec(statement).first()
