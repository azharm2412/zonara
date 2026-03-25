"""
@module CardModel
@desc ORM model untuk tabel 'cards' — kartu tantangan permainan Zonara.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base


class Card(Base):
    """
    Representasi tabel 'cards' di PostgreSQL.
    Master kartu tantangan permainan (10 per zona = 40 total).

    Attributes:
        id (int): Primary key auto-increment.
        qr_code (str): String QR unik untuk pemindaian (e.g., "ZCA-B-001").
        zone_id (int): FK ke tabel zones.
        title (str): Judul misi kartu.
        description (str): Deskripsi lengkap misi.
        difficulty (str): Tingkat kesulitan — 'easy', 'normal', 'hard'.
    """

    __tablename__ = "cards"
    __table_args__ = (
        CheckConstraint(
            "difficulty IN ('easy', 'normal', 'hard')",
            name="ck_cards_difficulty"
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    qr_code = Column(
        String(100), unique=True, nullable=False,
        comment="String unik untuk QR code (contoh: ZCA-B-001)"
    )
    zone_id = Column(
        Integer, ForeignKey("zones.id", ondelete="RESTRICT"),
        nullable=False, comment="Zona yang mengkategorikan kartu"
    )
    title = Column(
        String(255), nullable=False,
        comment="Judul misi kartu"
    )
    description = Column(
        Text, nullable=False,
        comment="Deskripsi lengkap misi"
    )
    difficulty = Column(
        String(20), nullable=False, server_default="normal",
        comment="Tingkat kesulitan: easy, normal, hard"
    )

    # --- Relationships ---
    zone = relationship("Zone", back_populates="cards")
    scores = relationship("Score", back_populates="card", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Card(id={self.id}, qr='{self.qr_code}', title='{self.title}')>"
