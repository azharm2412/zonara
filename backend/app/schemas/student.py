"""
@module StudentSchemas
@desc Pydantic models untuk validasi request/response entitas siswa.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StudentCreate(BaseModel):
    """Schema untuk mendaftarkan siswa baru."""
    nis: Optional[str] = Field(None, max_length=50, description="Nomor Induk Siswa")
    full_name: str = Field(..., min_length=2, max_length=255, description="Nama lengkap siswa")
    class_name: str = Field(..., min_length=1, max_length=50, description="Kelas aktif (e.g., 5A)")


class StudentUpdate(BaseModel):
    """Schema untuk memperbarui data siswa."""
    nis: Optional[str] = Field(None, max_length=50)
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    class_name: Optional[str] = Field(None, min_length=1, max_length=50)


class StudentResponse(BaseModel):
    """Schema response untuk data siswa."""
    id: int
    nis: Optional[str] = None
    full_name: str
    class_name: str
    school_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class StudentListResponse(BaseModel):
    """Schema response untuk daftar siswa."""
    status: str = "success"
    data: dict
    message: str
