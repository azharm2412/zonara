"""
@module ModelsBase
@desc Deklarasi DeclarativeBase SQLAlchemy untuk seluruh ORM model.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class untuk seluruh model SQLAlchemy.
    Digunakan oleh Alembic untuk auto-detect schema.
    """
    pass
