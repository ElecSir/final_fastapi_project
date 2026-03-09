from __future__ import annotations

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

COUNTER = 1  # Каунтер, иметирующий присвоение id в базе данных

# симулируем хранилище данных. Просто сохраняем объекты в память, в словаре.
# {0: {"id": 1, "title": "blabla", ...., "year": 2023}}
fake_storage = {}

# ORM
class Book(BaseModel):
    __tablename__ = "books_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    author: Mapped[str] = mapped_column(String(50), nullable=False)
    year: Mapped[int] = mapped_column(nullable=True)
    pages: Mapped[int]
    seller_id: Mapped[int] = mapped_column(ForeignKey("sellers_table.id"), nullable=False) # Внешний ключ на продавца
    seller: Mapped["Seller"] = relationship(back_populates="books") # Связь с продавцом (обратная связь)