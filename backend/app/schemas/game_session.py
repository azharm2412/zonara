"""
@module GameSessionSchemas
@desc Pydantic models untuk validasi request/response sesi permainan.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SessionCreate(BaseModel):
    """
    Schema untuk membuat sesi permainan baru.

    Attributes:
        class_name (str): Kelas yang akan bermain.
        student_ids (List[int]): Daftar ID siswa yang berpartisipasi.
    """
    class_name: str = Field(..., min_length=1, max_length=50, description="Kelas yang bermain")
    student_ids: List[int] = Field(..., min_length=1, description="Daftar ID siswa pemain")


class SessionResponse(BaseModel):
    """Schema response untuk data sesi permainan."""
    id: int
    session_code: str
    school_id: int
    class_name: str
    teacher_id: int
    status: str
    started_at: datetime
    ended_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SessionCreateResponse(BaseModel):
    """Schema response setelah sesi berhasil dibuat."""
    status: str = "success"
    data: dict
    message: str
