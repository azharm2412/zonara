"""
@module SchemasInit
@desc Re-export seluruh Pydantic schema untuk kemudahan import.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

from app.schemas.auth import *  # noqa: F401, F403
from app.schemas.school import *  # noqa: F401, F403
from app.schemas.student import *  # noqa: F401, F403
from app.schemas.zone import *  # noqa: F401, F403
from app.schemas.card import *  # noqa: F401, F403
from app.schemas.game_session import *  # noqa: F401, F403
from app.schemas.score import *  # noqa: F401, F403
from app.schemas.analytics import *  # noqa: F401, F403
