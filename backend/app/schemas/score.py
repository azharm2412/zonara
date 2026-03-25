"""
@module ScoreSchemas
@desc Pydantic models untuk validasi request/response pencatatan skor.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

from pydantic import BaseModel, Field


class ScanScoreRequest(BaseModel):
    """
    Schema validasi untuk request scan QR & input skor.

    Attributes:
        session_id (int): ID sesi permainan yang aktif.
        student_id (int): ID siswa yang dinilai.
        qr_code (str): String QR code yang dipindai dari kartu.
        result (int): Hasil penilaian — 0 (Gagal) atau 1 (Berhasil).
    """
    session_id: int = Field(..., gt=0, description="ID sesi permainan aktif")
    student_id: int = Field(..., gt=0, description="ID siswa yang dinilai")
    qr_code: str = Field(..., min_length=1, max_length=100, description="String QR code kartu")
    result: int = Field(..., ge=0, le=1, description="0 = Gagal, 1 = Berhasil")


class ScanScoreResponse(BaseModel):
    """Schema response setelah skor berhasil dicatat."""
    status: str = "success"
    data: dict
    message: str
