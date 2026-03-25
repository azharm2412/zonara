"""
@module GameSessionModel
@desc ORM model untuk tabel 'game_sessions' — sesi permainan board game.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import relationship
from app.models.base import Base


class GameSession(Base):
    """
    Representasi tabel 'game_sessions' di PostgreSQL.
    Sesi permainan board game Zonara yang difasilitasi oleh guru.

    Attributes:
        id (int): Primary key auto-increment.
        session_code (str): Kode sesi 6 karakter alfanumerik (auto-generated).
        school_id (int): FK ke tabel schools.
        class_name (str): Kelas yang bermain.
        teacher_id (int): FK ke tabel users (guru fasilitator).
        status (str): Status sesi — 'active', 'completed'.
        started_at (datetime): Waktu mulai sesi.
        ended_at (datetime): Waktu selesai (diisi saat completed).
    """

    __tablename__ = "game_sessions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'completed')",
            name="ck_sessions_status"
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_code = Column(
        String(10), unique=True, nullable=False,
        comment="Kode sesi 6 karakter alfanumerik (auto-generated)"
    )
    school_id = Column(
        Integer, ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False, comment="Sekolah tempat sesi berlangsung"
    )
    class_name = Column(
        String(50), nullable=False,
        comment="Kelas yang bermain"
    )
    teacher_id = Column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False, comment="Guru yang memfasilitasi sesi"
    )
    status = Column(
        String(20), nullable=False, server_default="active",
        comment="Status: active (berlangsung), completed (selesai)"
    )
    started_at = Column(
        DateTime, nullable=False, server_default=func.now(),
        comment="Waktu mulai sesi"
    )
    ended_at = Column(
        DateTime, nullable=True,
        comment="Waktu selesai (diisi saat status → completed)"
    )

    # --- Relationships ---
    school = relationship("School", back_populates="game_sessions")
    teacher = relationship("User", back_populates="facilitated_sessions")
    players = relationship("SessionPlayer", back_populates="session", lazy="selectin")
    scores = relationship("Score", back_populates="session", lazy="selectin")

    def __repr__(self) -> str:
        return f"<GameSession(id={self.id}, code='{self.session_code}', status='{self.status}')>"
