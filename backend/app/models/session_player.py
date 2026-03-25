"""
@module SessionPlayerModel
@desc ORM model untuk tabel 'session_players' — junction table N:N antara
      game_sessions dan students.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base


class SessionPlayer(Base):
    """
    Representasi tabel 'session_players' di PostgreSQL.
    Tabel junction: menjembatani relasi many-to-many antara game_sessions
    dan students. Satu siswa hanya bisa terdaftar sekali per sesi.

    Attributes:
        id (int): Primary key auto-increment.
        session_id (int): FK ke tabel game_sessions.
        student_id (int): FK ke tabel students.
    """

    __tablename__ = "session_players"
    __table_args__ = (
        UniqueConstraint(
            "session_id", "student_id",
            name="uq_session_player"
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(
        Integer, ForeignKey("game_sessions.id", ondelete="CASCADE"),
        nullable=False, comment="Referensi sesi"
    )
    student_id = Column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False, comment="Referensi siswa pemain"
    )

    # --- Relationships ---
    session = relationship("GameSession", back_populates="players")
    student = relationship("Student", back_populates="session_players")

    def __repr__(self) -> str:
        return f"<SessionPlayer(session={self.session_id}, student={self.student_id})>"
