from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Section(SQLModel, table=True):
    """Secciones del inventario (Refrigerador, Almacén 1, etc.)"""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    emoji: str = Field(default="📦")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relación
    items: list["Item"] = Relationship(back_populates="section")


class Item(SQLModel, table=True):
    """Items del inventario de alimentos"""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)  # Case-insensitive en queries
    emoji: str = Field(default="🍽️")
    quantity: float = Field(default=0)
    unit: str = Field(default="unidades")  # kg, L, unidades, etc.
    threshold: float = Field(default=1)  # Umbral de alerta
    section_id: int = Field(foreign_key="section.id")
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relaciones
    section: Section = Relationship(back_populates="items")
    history: list["ItemHistory"] = Relationship(back_populates="item")

    @property
    def is_below_threshold(self) -> bool:
        """Verifica si el item está por debajo del umbral"""
        return self.quantity < self.threshold


class ItemHistory(SQLModel, table=True):
    """Historial de cambios de cantidad de items"""

    id: Optional[int] = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="item.id")
    quantity: float
    changed_at: datetime = Field(default_factory=datetime.utcnow)

    # Relación
    item: Item = Relationship(back_populates="history")


class User(SQLModel, table=True):
    """Usuario único de la aplicación"""

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    password_hash: str  # bcrypt hash
