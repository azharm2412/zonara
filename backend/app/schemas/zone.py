"""
@module ZoneSchemas
@desc Pydantic models untuk validasi response entitas zona karakter.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

from pydantic import BaseModel
from typing import Optional


class ZoneResponse(BaseModel):
    """Schema response untuk data zona karakter CASEL."""
    id: int
    code: str
    name: str
    color_hex: str
    sel_dimension: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}
