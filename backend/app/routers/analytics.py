"""
@module AnalyticsRouter
@desc Endpoint REST API untuk modul analitik (Radar Chart, Class Summary).
      Mengacu pada API Spec §2.3 dan FR-004, FR-006.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.services.analytics_service import AnalyticsService
from app.middleware.auth import get_current_user, RoleChecker

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/radar/{student_id}")
async def get_radar_chart(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mengambil koordinat Radar Chart untuk satu siswa.
    Mengacu pada API Spec §2.3.1.

    Orang tua hanya dapat mengakses data anak sendiri.

    @param student_id: ID siswa target.
    @param db: AsyncSession database.
    @param current_user: User yang login.
    @return dict: Radar data per zona.
    """
    try:
        # Validasi RBAC: orang tua hanya bisa lihat anak sendiri
        if current_user.role == "orang_tua":
            if current_user.child_student_id != student_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Anda hanya dapat mengakses data anak Anda.",
                )

        radar_data = await AnalyticsService.get_radar_data(
            db, student_id, current_user.school_id
        )

        return {
            "status": "success",
            "data": {
                "student_id": student_id,
                "radar_data": radar_data,
            },
            "message": "Data radar chart individu berhasil di-generate.",
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Radar chart error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal menghasilkan data Radar Chart.",
        )


@router.get(
    "/class-summary",
    dependencies=[Depends(RoleChecker(["admin", "guru_bk", "wali_kelas"]))],
)
async def get_class_summary(
    class_name: str = Query(..., description="Nama kelas (e.g., 5A)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mengambil ringkasan analitik kelas: rata-rata per zona dan flagged students.
    Mengacu pada API Spec §2.3.2.

    @param class_name: Nama kelas target.
    @param db: AsyncSession database.
    @param current_user: User yang login (Admin/Guru BK/Wali Kelas).
    @return dict: Class average dan daftar siswa ter-flag.
    """
    try:
        # Wali kelas hanya bisa melihat kelas sendiri
        if current_user.role == "wali_kelas":
            if current_user.class_name != class_name:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Anda hanya dapat mengakses data kelas Anda.",
                )

        summary = await AnalyticsService.get_class_summary(
            db, class_name, current_user.school_id
        )

        return {
            "status": "success",
            "data": summary,
            "message": "Summary kelas beserta flag intervensi berhasil diambil.",
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Class summary error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal menghasilkan ringkasan kelas.",
        )


@router.get("/session-radar/{session_id}")
async def get_session_radar(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mengambil agregasi Radar Chart untuk satu sesi permainan (seluruh siswa digabung).
    Digunakan oleh FocusMode sebagai REST fallback saat WebSocket tidak tersedia.

    @param session_id: ID sesi permainan.
    @param db: AsyncSession database.
    @param current_user: User yang login.
    @return dict: Radar data per zona dan total scan.
    """
    try:
        from sqlalchemy import func as sql_func
        from app.models.score import Score
        from app.models.zone import Zone

        # 1. Ambil semua zona yang ada di database
        all_zones_result = await db.execute(select(Zone.code))
        all_zone_codes = [row[0] for row in all_zones_result.all()]

        # 2. Agregasi skor per zona untuk sesi ini
        #    Query langsung dari scores JOIN zones (bukan outerjoin)
        score_query = (
            select(Zone.code, sql_func.sum(Score.result).label("total"))
            .select_from(Score)
            .join(Zone, Score.zone_id == Zone.id)
            .where(Score.session_id == session_id)
            .group_by(Zone.code)
        )
        score_result = await db.execute(score_query)
        score_map = {row.code: int(row.total) for row in score_result.all()}

        # 3. Gabungkan: semua zona dengan skor (default 0 jika belum ada)
        radar_data = {}
        for code in all_zone_codes:
            radar_data[code] = score_map.get(code, 0)

        # 4. Total scan count
        count_result = await db.execute(
            select(sql_func.count(Score.id)).where(Score.session_id == session_id)
        )
        total_scans = count_result.scalar() or 0

        return {
            "status": "success",
            "data": {
                "session_id": session_id,
                "radar_data": radar_data,
                "total_scans": total_scans,
            },
            "message": "Session radar data berhasil diambil.",
        }

    except Exception as exc:
        logger.error("Session radar error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal menghasilkan session radar data.",
        )
