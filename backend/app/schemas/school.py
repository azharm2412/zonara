"""
@module SchoolSchemas
@desc Pydantic models untuk validasi request/response entitas sekolah.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SchoolCreate(BaseModel):
    """Schema untuk membuat sekolah baru."""
    name: str = Field(..., min_length=3, max_length=255, description="Nama resmi sekolah")
    address: Optional[str] = Field(None, description="Alamat lengkap sekolah")


class SchoolUpdate(BaseModel):
    """Schema untuk memperbarui data sekolah."""
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    address: Optional[str] = None


class SchoolResponse(BaseModel):
    """Schema response untuk data sekolah."""
    id: int
    name: str
    address: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
