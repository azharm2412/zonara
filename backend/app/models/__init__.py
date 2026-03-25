"""
@module ModelsInit
@desc Re-export seluruh model SQLAlchemy untuk Alembic auto-detection
      dan kemudahan import di seluruh aplikasi.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

from app.models.base import Base  # noqa: F401
from app.models.school import School  # noqa: F401
from app.models.student import Student  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.zone import Zone  # noqa: F401
from app.models.card import Card  # noqa: F401
from app.models.game_session import GameSession  # noqa: F401
from app.models.session_player import SessionPlayer  # noqa: F401
from app.models.score import Score  # noqa: F401

__all__ = [
    "Base",
    "School",
    "Student",
    "User",
    "Zone",
    "Card",
    "GameSession",
    "SessionPlayer",
    "Score",
]
