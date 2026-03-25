"""
@module ServicesInit
@desc Re-export seluruh service untuk kemudahan import.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

from app.services.auth_service import AuthService  # noqa: F401
from app.services.scoring_service import ScoringService  # noqa: F401
from app.services.analytics_service import AnalyticsService  # noqa: F401

__all__ = ["AuthService", "ScoringService", "AnalyticsService"]
