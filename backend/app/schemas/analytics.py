"""
@module AnalyticsSchemas
@desc Pydantic models untuk validasi response modul analitik (Radar Chart, Class Summary).
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

from pydantic import BaseModel
from typing import Dict, List, Optional


class RadarDataResponse(BaseModel):
    """
    Schema response untuk koordinat Radar Chart individu siswa.

    Attributes:
        student_id (int): ID siswa.
        radar_data (dict): Skor per zona (blue, green, yellow, red).
    """
    student_id: int
    radar_data: Dict[str, int]


class FlaggedStudent(BaseModel):
    """
    Schema untuk siswa yang terdeteksi memerlukan intervensi.

    Attributes:
        student_id (int): ID siswa.
        name (str): Nama lengkap siswa.
        flags (list): Daftar kode zona yang ter-flag.
    """
    student_id: int
    name: str
    flags: List[str]


class ClassSummaryResponse(BaseModel):
    """
    Schema response untuk ringkasan analitik kelas.

    Attributes:
        class_average (dict): Rata-rata skor per zona untuk kelas.
        flagged_students (list): Siswa dengan flag intervensi.
    """
    class_average: Dict[str, float]
    flagged_students: List[FlaggedStudent]


class AnalyticsResponse(BaseModel):
    """Schema response wrapper standar untuk analitik."""
    status: str = "success"
    data: Optional[RadarDataResponse | ClassSummaryResponse] = None
    message: str
