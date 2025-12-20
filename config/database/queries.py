"""Common database query utilities for finding items and sections"""

from sqlmodel import Session, select, func

from database.models import Item, Section


def find_item_by_name(session: Session, name: str) -> Item | None:
    """
    Finds an item by name using case-insensitive search.

    Args:
        session: Database session
        name: Item name to search for (case-insensitive)

    Returns:
        Item instance if found, None otherwise
    """
    statement = select(Item).where(func.lower(Item.name) == name.lower())
    return session.exec(statement).first()


def find_section_by_name(session: Session, name: str) -> Section | None:
    """
    Finds a section by name using case-insensitive search.

    Args:
        session: Database session
        name: Section name to search for (case-insensitive)

    Returns:
        Section instance if found, None otherwise
    """
    statement = select(Section).where(func.lower(Section.name) == name.lower())
    return session.exec(statement).first()
