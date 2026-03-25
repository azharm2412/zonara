"""
@module StudentModel
@desc ORM model untuk tabel 'students' — siswa SD subjek penilaian karakter.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.models.base import Base


class Student(Base):
    """
    Representasi tabel 'students' di PostgreSQL.
    Menyimpan data siswa Sekolah Dasar yang menjadi subjek penilaian karakter.

    Attributes:
        id (int): Primary key auto-increment.
        nis (str): Nomor Induk Siswa (opsional, unik jika diisi).
        full_name (str): Nama lengkap siswa.
        class_name (str): Kelas aktif siswa (e.g., "5A", "6B").
        school_id (int): FK ke tabel schools.
        created_at (datetime): Waktu pendaftaran siswa.
    """

    __tablename__ = "students"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nis = Column(
        String(50), unique=True, nullable=True,
        comment="Nomor Induk Siswa (opsional, unik jika diisi)"
    )
    full_name = Column(
        String(255), nullable=False,
        comment="Nama lengkap siswa"
    )
    class_name = Column(
        String(50), nullable=False,
        comment="Kelas aktif siswa, contoh: 5A, 6B"
    )
    school_id = Column(
        Integer, ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False, comment="Referensi ke sekolah"
    )
    created_at = Column(
        DateTime, nullable=False, server_default=func.now(),
        comment="Waktu pendaftaran siswa"
    )

    # --- Relationships ---
    school = relationship("School", back_populates="students")
    session_players = relationship("SessionPlayer", back_populates="student", lazy="selectin")
    scores = relationship("Score", back_populates="student", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, nis='{self.nis}', name='{self.full_name}')>"
