"""
@module AnalyticsService
@desc Business logic layer untuk analitik: Radar Chart, rata-rata kelas,
      flag intervensi, dan growth tracker.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

import logging
from typing import Dict, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.score import Score
from app.models.zone import Zone
from app.models.student import Student
from app.models.game_session import GameSession

logger = logging.getLogger(__name__)

# Ambang batas flag intervensi: skor siswa < 80% rata-rata kelas
FLAG_THRESHOLD_RATIO = 0.80


class AnalyticsService:
    """
    Layanan analitik yang menyediakan aggregasi data untuk Radar Chart,
    ringkasan kelas, dan deteksi flag intervensi.
    """

    @staticmethod
    async def get_radar_data(
        db: AsyncSession, student_id: int, school_id: int
    ) -> Dict[str, int]:
        """
        Mengambil agregasi skor per dimensi zona untuk satu siswa.
        Query ini menggunakan indeks idx_scores_composite untuk performa optimal.

        @param db: AsyncSession database.
        @param student_id: ID siswa target.
        @param school_id: ID sekolah untuk isolasi multi-tenant.
        @return dict: Skor per zona (e.g., {"blue": 3, "green": 2, ...}).
        @raises HTTPException: 404 jika siswa tidak ditemukan, 500 jika query gagal.
        """
        try:
            # Validasi siswa termasuk sekolah yang benar
            student_result = await db.execute(
                select(Student).where(
                    Student.id == student_id,
                    Student.school_id == school_id,
                )
            )
            student = student_result.scalar_one_or_none()
            if student is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Siswa dengan ID {student_id} tidak ditemukan di sekolah ini.",
                )

            # Agregasi skor per zona
            query = (
                select(Zone.code, func.coalesce(func.sum(Score.result), 0).label("total"))
                .outerjoin(Score, (Score.zone_id == Zone.id) & (Score.student_id == student_id))
                .group_by(Zone.code)
                .order_by(Zone.code)
            )
            result = await db.execute(query)
            rows = result.all()

            radar_data = {row.code: int(row.total) for row in rows}
            return radar_data

        except HTTPException:
            raise
        except Exception as exc:
            logger.error("Radar data query error: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal mengambil data Radar Chart.",
            )

    @staticmethod
    async def get_class_summary(
        db: AsyncSession, class_name: str, school_id: int
    ) -> dict:
        """
        Menghitung rata-rata skor kelas per dimensi dan mengidentifikasi
        siswa yang memerlukan intervensi (flag).

        Flag intervensi: skor siswa < 80% dari rata-rata kelas pada zona tersebut.

        @param db: AsyncSession database.
        @param class_name: Nama kelas (e.g., "5A").
        @param school_id: ID sekolah untuk isolasi multi-tenant.
        @return dict: {class_average: {...}, flagged_students: [...]}.
        @raises HTTPException: 404 jika tidak ada data, 500 jika query gagal.
        """
        try:
            # Ambil seluruh siswa di kelas
            students_result = await db.execute(
                select(Student).where(
                    Student.school_id == school_id,
                    Student.class_name == class_name,
                )
            )
            students = students_result.scalars().all()

            if not students:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Tidak ada siswa ditemukan di kelas '{class_name}'.",
                )

            student_ids = [s.id for s in students]

            # Ambil semua zona
            zones_result = await db.execute(select(Zone))
            zones = zones_result.scalars().all()
            zone_codes = {z.id: z.code for z in zones}

            # Hitung skor per siswa per zona
            student_scores = {}
            for student in students:
                query = (
                    select(Score.zone_id, func.sum(Score.result).label("total"))
                    .where(Score.student_id == student.id)
                    .group_by(Score.zone_id)
                )
                result = await db.execute(query)
                scores = {zone_codes.get(row.zone_id, "unknown"): int(row.total) for row in result.all()}
                student_scores[student.id] = scores

            # Hitung rata-rata kelas per zona
            class_average = {}
            for zone in zones:
                zone_totals = [
                    student_scores.get(sid, {}).get(zone.code, 0)
                    for sid in student_ids
                ]
                avg = sum(zone_totals) / len(zone_totals) if zone_totals else 0
                class_average[zone.code] = round(avg, 2)

            # Deteksi flag intervensi
            flagged_students = []
            for student in students:
                flags = []
                scores = student_scores.get(student.id, {})
                for zone in zones:
                    student_score = scores.get(zone.code, 0)
                    avg = class_average.get(zone.code, 0)
                    if avg > 0 and student_score < (avg * FLAG_THRESHOLD_RATIO):
                        flags.append(zone.code)

                if flags:
                    flagged_students.append({
                        "student_id": student.id,
                        "name": student.full_name,
                        "flags": flags,
                    })

            return {
                "class_average": class_average,
                "flagged_students": flagged_students,
            }

        except HTTPException:
            raise
        except Exception as exc:
            logger.error("Class summary error: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal menghasilkan ringkasan kelas.",
            )
