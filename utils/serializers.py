"""Data serialization utilities for converting database models to template-ready dictionaries"""

from config.database.models import Item, Section
from utils.time import humanize_time


def serialize_item_for_template(item: Item) -> dict:
    """
    Converts an Item model instance to a template-ready dictionary.

    Args:
        item: Item instance from database

    Returns:
        Dictionary with item data formatted for template rendering
    """
    return {
        "id": item.id,
        "name": item.name,
        "emoji": item.emoji,
        "quantity": item.quantity,
        "unit": item.unit,
        "section_emoji": item.section.emoji,
        "section_name": item.section.name,
        "updated_at_human": humanize_time(item.updated_at),
        "is_below_threshold": item.is_below_threshold,
    }


def serialize_items_for_template(items: list[Item]) -> list[dict]:
    """
    Converts a list of Item instances to template-ready dictionaries.

    Args:
        items: List of Item instances from database

    Returns:
        List of dictionaries with item data formatted for template rendering
    """
    return [serialize_item_for_template(item) for item in items]


def serialize_section_for_template(section: Section) -> dict:
    """
    Converts a Section model instance to a template-ready dictionary.

    Args:
        section: Section instance from database

    Returns:
        Dictionary with section data formatted for template rendering
    """
    return {
        "id": section.id,
        "name": section.name,
        "emoji": section.emoji,
    }


def serialize_sections_for_template(sections: list[Section]) -> list[dict]:
    """
    Converts a list of Section instances to template-ready dictionaries.

    Args:
        sections: List of Section instances from database

    Returns:
        List of dictionaries with section data formatted for template rendering
    """
    return [serialize_section_for_template(section) for section in sections]
