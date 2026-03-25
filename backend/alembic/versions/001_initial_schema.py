"""Initial schema — 8 tabel Zonara Character Analytics

Revision ID: 001_initial_schema
Revises: None
Create Date: 2026-03-25

Migrasi awal yang membuat seluruh 8 tabel, constraints, dan indeks
sesuai dokumen ZCA-DBD-2026-001.
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# Revision identifiers
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Membuat seluruh tabel, constraints, dan indeks sistem Zonara."""

    # 1. schools
    op.create_table(
        "schools",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # 2. students
    op.create_table(
        "students",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("nis", sa.String(50), unique=True, nullable=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("class_name", sa.String(50), nullable=False),
        sa.Column("school_id", sa.Integer, sa.ForeignKey("schools.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # 3. users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(100), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("school_id", sa.Integer, sa.ForeignKey("schools.id", ondelete="CASCADE"), nullable=True),
        sa.Column("class_name", sa.String(50), nullable=True),
        sa.Column("child_student_id", sa.Integer, sa.ForeignKey("students.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("role IN ('admin', 'guru_bk', 'wali_kelas', 'orang_tua')", name="ck_users_role"),
    )

    # 4. zones
    op.create_table(
        "zones",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(20), unique=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("color_hex", sa.String(7), nullable=False),
        sa.Column("sel_dimension", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
    )

    # 5. cards
    op.create_table(
        "cards",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("qr_code", sa.String(100), unique=True, nullable=False),
        sa.Column("zone_id", sa.Integer, sa.ForeignKey("zones.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("difficulty", sa.String(20), nullable=False, server_default="normal"),
        sa.CheckConstraint("difficulty IN ('easy', 'normal', 'hard')", name="ck_cards_difficulty"),
    )

    # 6. game_sessions
    op.create_table(
        "game_sessions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("session_code", sa.String(10), unique=True, nullable=False),
        sa.Column("school_id", sa.Integer, sa.ForeignKey("schools.id", ondelete="CASCADE"), nullable=False),
        sa.Column("class_name", sa.String(50), nullable=False),
        sa.Column("teacher_id", sa.Integer, sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("started_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("ended_at", sa.DateTime, nullable=True),
        sa.CheckConstraint("status IN ('active', 'completed')", name="ck_sessions_status"),
    )

    # 7. session_players
    op.create_table(
        "session_players",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.Integer, sa.ForeignKey("game_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("student_id", sa.Integer, sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("session_id", "student_id", name="uq_session_player"),
    )

    # 8. scores
    op.create_table(
        "scores",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.Integer, sa.ForeignKey("game_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("student_id", sa.Integer, sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("card_id", sa.Integer, sa.ForeignKey("cards.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("zone_id", sa.Integer, sa.ForeignKey("zones.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("result", sa.SmallInteger, nullable=False),
        sa.Column("scored_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("result IN (0, 1)", name="ck_scores_result"),
    )

    # --- Indeks Performa ---
    op.create_index("idx_users_school", "users", ["school_id"])
    op.create_index("idx_users_role", "users", ["role"])
    op.create_index("idx_students_school", "students", ["school_id"])
    op.create_index("idx_students_class", "students", ["class_name"])
    op.create_index("idx_students_school_class", "students", ["school_id", "class_name"])
    op.create_index("idx_cards_zone", "cards", ["zone_id"])
    op.create_index("idx_sessions_school", "game_sessions", ["school_id"])
    op.create_index("idx_sessions_teacher", "game_sessions", ["teacher_id"])
    op.create_index("idx_sessions_status", "game_sessions", ["status"])
    op.create_index("idx_splayers_session", "session_players", ["session_id"])
    op.create_index("idx_splayers_student", "session_players", ["student_id"])
    op.create_index("idx_scores_session", "scores", ["session_id"])
    op.create_index("idx_scores_student", "scores", ["student_id"])
    op.create_index("idx_scores_zone", "scores", ["zone_id"])
    op.create_index("idx_scores_composite", "scores", ["session_id", "student_id", "zone_id"])
    op.create_index("idx_scores_scored_at", "scores", ["scored_at"])


def downgrade() -> None:
    """Menghapus seluruh tabel dan indeks (rollback)."""
    op.drop_table("scores")
    op.drop_table("session_players")
    op.drop_table("game_sessions")
    op.drop_table("cards")
    op.drop_table("zones")
    op.drop_table("users")
    op.drop_table("students")
    op.drop_table("schools")
