"""
@module UserModel
@desc ORM model untuk tabel 'users' — pengguna sistem dengan RBAC.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import relationship
from app.models.base import Base


class User(Base):
    """
    Representasi tabel 'users' di PostgreSQL.
    Menyimpan data pengguna dengan Role-Based Access Control (RBAC).

    Attributes:
        id (int): Primary key auto-increment.
        username (str): Username login, unik secara global.
        password_hash (str): Hash password (bcrypt, salt round >= 12).
        full_name (str): Nama lengkap pengguna.
        role (str): Peran RBAC — 'admin', 'guru_bk', 'wali_kelas', 'orang_tua'.
        school_id (int): FK ke tabel schools (opsional).
        class_name (str): Kelas yang diampu (jika role = wali_kelas).
        child_student_id (int): FK ke tabel students (jika role = orang_tua).
        created_at (datetime): Waktu registrasi akun.
    """

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('admin', 'guru_bk', 'wali_kelas', 'orang_tua')",
            name="ck_users_role"
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(
        String(100), unique=True, nullable=False,
        comment="Username login, unik secara global"
    )
    password_hash = Column(
        String(255), nullable=False,
        comment="Hash password (bcrypt)"
    )
    full_name = Column(
        String(255), nullable=False,
        comment="Nama lengkap pengguna"
    )
    role = Column(
        String(20), nullable=False,
        comment="Peran: admin, guru_bk, wali_kelas, orang_tua"
    )
    school_id = Column(
        Integer, ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=True, comment="Referensi ke sekolah pengguna"
    )
    class_name = Column(
        String(50), nullable=True,
        comment="Kelas yang diampu (diisi jika role = wali_kelas)"
    )
    child_student_id = Column(
        Integer, ForeignKey("students.id", ondelete="SET NULL"),
        nullable=True, comment="ID siswa anak (diisi jika role = orang_tua)"
    )
    created_at = Column(
        DateTime, nullable=False, server_default=func.now(),
        comment="Waktu registrasi akun"
    )

    # --- Relationships ---
    school = relationship("School", back_populates="users")
    child_student = relationship("Student", foreign_keys=[child_student_id])
    facilitated_sessions = relationship("GameSession", back_populates="teacher", lazy="selectin")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
