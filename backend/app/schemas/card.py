"""
@module CardSchemas
@desc Pydantic models untuk validasi request/response entitas kartu tantangan.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

from pydantic import BaseModel, Field
from typing import Optional


class CardResponse(BaseModel):
    """Schema response untuk data kartu tantangan."""
    id: int
    qr_code: str
    zone_id: int
    title: str
    description: str
    difficulty: str

    model_config = {"from_attributes": True}


class CardCreate(BaseModel):
    """Schema untuk membuat kartu baru."""
    qr_code: str = Field(..., max_length=100, description="String unik QR code")
    zone_id: int = Field(..., gt=0, description="ID zona")
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    difficulty: str = Field("normal", pattern="^(easy|normal|hard)$")
