"""
@module ScoreModel
@desc ORM model untuk tabel 'scores' — tabel fakta utama penilaian karakter.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

from sqlalchemy import Column, Integer, SmallInteger, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import relationship
from app.models.base import Base


class Score(Base):
    """
    Representasi tabel 'scores' di PostgreSQL.
    Tabel fakta utama: rekaman hasil penilaian per siswa per kartu per sesi.

    Catatan: zone_id merupakan denormalisasi deliberat dari cards.zone_id
    untuk menghindari JOIN tambahan pada query analitik Radar Chart.

    Attributes:
        id (int): Primary key auto-increment.
        session_id (int): FK ke tabel game_sessions.
        student_id (int): FK ke tabel students.
        card_id (int): FK ke tabel cards.
        zone_id (int): FK ke tabel zones (denormalisasi deliberat).
        result (int): Hasil — 0 (Gagal) atau 1 (Berhasil).
        scored_at (datetime): Waktu penilaian dicatat.
    """

    __tablename__ = "scores"
    __table_args__ = (
        CheckConstraint(
            "result IN (0, 1)",
            name="ck_scores_result"
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(
        Integer, ForeignKey("game_sessions.id", ondelete="CASCADE"),
        nullable=False, comment="Sesi di mana penilaian terjadi"
    )
    student_id = Column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False, comment="Siswa yang dinilai"
    )
    card_id = Column(
        Integer, ForeignKey("cards.id", ondelete="RESTRICT"),
        nullable=False, comment="Kartu yang diuji"
    )
    zone_id = Column(
        Integer, ForeignKey("zones.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Denormalisasi deliberat dari cards.zone_id untuk performa analitik"
    )
    result = Column(
        SmallInteger, nullable=False,
        comment="0 = Gagal, 1 = Berhasil"
    )
    scored_at = Column(
        DateTime, nullable=False, server_default=func.now(),
        comment="Waktu penilaian dicatat"
    )

    # --- Relationships ---
    session = relationship("GameSession", back_populates="scores")
    student = relationship("Student", back_populates="scores")
    card = relationship("Card", back_populates="scores")
    zone = relationship("Zone", back_populates="scores")

    def __repr__(self) -> str:
        return f"<Score(id={self.id}, student={self.student_id}, result={self.result})>"
