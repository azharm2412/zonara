"""
@module ZoneModel
@desc ORM model untuk tabel 'zones' — 4 dimensi karakter CASEL.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.models.base import Base


class Zone(Base):
    """
    Representasi tabel 'zones' di PostgreSQL.
    Master dimensi karakter berdasarkan CASEL SEL Framework (4 zona).

    Attributes:
        id (int): Primary key auto-increment.
        code (str): Kode zona — 'blue', 'green', 'yellow', 'red'.
        name (str): Nama dimensi SEL (e.g., "Self-Awareness").
        color_hex (str): Kode warna hex (e.g., "#3B82F6").
        sel_dimension (str): Pemetaan ke kompetensi CASEL.
        description (str): Deskripsi lengkap dimensi (opsional).
    """

    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(
        String(20), unique=True, nullable=False,
        comment="Kode zona: blue, green, yellow, red"
    )
    name = Column(
        String(100), nullable=False,
        comment="Nama dimensi SEL"
    )
    color_hex = Column(
        String(7), nullable=False,
        comment="Warna hex: #3B82F6, #22C55E, #F59E0B, #EF4444"
    )
    sel_dimension = Column(
        String(100), nullable=False,
        comment="Pemetaan ke kompetensi CASEL"
    )
    description = Column(
        Text, nullable=True,
        comment="Deskripsi lengkap dimensi"
    )

    # --- Relationships ---
    cards = relationship("Card", back_populates="zone", lazy="selectin")
    scores = relationship("Score", back_populates="zone", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Zone(id={self.id}, code='{self.code}', name='{self.name}')>"
