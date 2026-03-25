"""
@module RoutersInit
@desc Re-export seluruh router untuk kemudahan import di main.py.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

from app.routers import auth, sessions, students, scan, analytics, export  # noqa: F401
