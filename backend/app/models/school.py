"""
@module SchoolModel
@desc ORM model untuk tabel 'schools' — entitas organisasi tingkat atas (tenant).
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import relationship
from app.models.base import Base


class School(Base):
    """
    Representasi tabel 'schools' di PostgreSQL.
    Entitas master multi-tenant: seluruh data terisolasi per school_id.

    Attributes:
        id (int): Primary key auto-increment.
        name (str): Nama resmi sekolah (e.g., "SDN 1 Kebumen").
        address (str): Alamat lengkap sekolah (opsional).
        created_at (datetime): Waktu pencatatan entitas.
    """

    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, comment="Nama resmi sekolah")
    address = Column(Text, nullable=True, comment="Alamat lengkap sekolah")
    created_at = Column(
        DateTime, nullable=False, server_default=func.now(),
        comment="Waktu pencatatan entitas"
    )

    # --- Relationships ---
    users = relationship("User", back_populates="school", lazy="selectin")
    students = relationship("Student", back_populates="school", lazy="selectin")
    game_sessions = relationship("GameSession", back_populates="school", lazy="selectin")

    def __repr__(self) -> str:
        return f"<School(id={self.id}, name='{self.name}')>"
