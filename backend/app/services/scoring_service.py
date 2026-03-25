"""
@module ScoringService
@desc Business logic layer untuk pencatatan skor: QR lookup, score recording,
      WebSocket broadcast.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

import logging
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.card import Card
from app.models.score import Score
from app.models.zone import Zone
from app.models.game_session import GameSession
from app.models.session_player import SessionPlayer

# new 
from sqlalchemy.orm import joinedload

logger = logging.getLogger(__name__)


class ScoringService:
    """
    Layanan scoring yang mengelola proses lookup kartu dari QR code,
    pencatatan skor, dan persiapan data broadcast WebSocket.
    """

    @staticmethod
    async def lookup_card_by_qr(db: AsyncSession, qr_code: str) -> Card:
        """
        Mencari kartu berdasarkan QR code string.

        @param db: AsyncSession database.
        @param qr_code: String QR code yang dipindai.
        @return Card: Instance Card yang ditemukan.
        @raises HTTPException: 404 jika QR code tidak ditemukan di database.
        """
        try:
            # Gunakan options(joinedload(Card.zone)) agar data zona ikut terbawa
            result = await db.execute(
                select(Card)
                .options(joinedload(Card.zone)) 
                .where(Card.qr_code == qr_code)
            )
            card = result.scalar_one_or_none()
        except Exception as exc:
            logger.error("Database error during QR lookup: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal mencari data kartu.",
            )

        if card is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"QR code '{qr_code}' tidak ditemukan dalam database.",
            )

        return card

    @staticmethod
    async def validate_session_player(
        db: AsyncSession, session_id: int, student_id: int
    ) -> None:
        """
        Memvalidasi bahwa sesi aktif dan siswa terdaftar sebagai pemain.

        @param db: AsyncSession database.
        @param session_id: ID sesi permainan.
        @param student_id: ID siswa.
        @raises HTTPException: 400 jika sesi tidak aktif, 404 jika siswa tidak terdaftar.
        """
        try:
            # Validasi sesi aktif
            session_result = await db.execute(
                select(GameSession).where(GameSession.id == session_id)
            )
            session = session_result.scalar_one_or_none()

            if session is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Sesi permainan dengan ID {session_id} tidak ditemukan.",
                )

            if session.status != "active":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Sesi permainan sudah selesai (completed). Tidak dapat menambah skor.",
                )

            # Validasi pemain terdaftar
            player_result = await db.execute(
                select(SessionPlayer).where(
                    SessionPlayer.session_id == session_id,
                    SessionPlayer.student_id == student_id,
                )
            )
            player = player_result.scalar_one_or_none()

            if player is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Siswa ID {student_id} tidak terdaftar di sesi {session_id}.",
                )

        except HTTPException:
            raise
        except Exception as exc:
            logger.error("Validation error: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal memvalidasi sesi dan pemain.",
            )

    @staticmethod
    async def record_score(
        db: AsyncSession,
        session_id: int,
        student_id: int,
        card_id: int,
        zone_id: int,
        result_value: int,
    ) -> Score:
        """
        Mencatat skor penilaian ke database.

        @param db: AsyncSession database.
        @param session_id: ID sesi permainan.
        @param student_id: ID siswa yang dinilai.
        @param card_id: ID kartu yang diuji.
        @param zone_id: ID zona (denormalisasi dari card.zone_id).
        @param result_value: Hasil — 0 (Gagal) atau 1 (Berhasil).
        @return Score: Instance Score yang baru dibuat.
        @raises HTTPException: 500 jika gagal menyimpan ke database.
        """
        try:
            new_score = Score(
                session_id=session_id,
                student_id=student_id,
                card_id=card_id,
                zone_id=zone_id,
                result=result_value,
            )
            db.add(new_score)
            await db.commit()
            await db.refresh(new_score)

            logger.info(
                "Score recorded: session=%d, student=%d, card=%d, result=%d",
                session_id, student_id, card_id, result_value,
            )

            # --- WebSocket Broadcast ke Focus Mode ---
            try:
                from app.routers.ws_analytics import manager

                # Hitung radar data terbaru untuk sesi ini (semua siswa digabung)
                radar_query = (
                    select(Zone.code, func.coalesce(func.sum(Score.result), 0).label("total"))
                    .outerjoin(Score, (Score.zone_id == Zone.id) & (Score.session_id == session_id))
                    .group_by(Zone.code)
                    .order_by(Zone.code)
                )
                radar_result = await db.execute(radar_query)
                radar_data = {row.code: int(row.total) for row in radar_result.all()}

                # Hitung total scan dalam sesi
                count_query = select(func.count(Score.id)).where(Score.session_id == session_id)
                count_result = await db.execute(count_query)
                total_scans = count_result.scalar() or 0

                await manager.broadcast_to_session(session_id, {
                    "event": "score_update",
                    "data": {
                        "radar_data": radar_data,
                        "total_scans": total_scans,
                    },
                })
            except Exception as broadcast_err:
                # Broadcast failure tidak boleh menggagalkan skor yang sudah tersimpan
                logger.warning("WS broadcast error (non-fatal): %s", str(broadcast_err))

            return new_score

        except Exception as exc:
            await db.rollback()
            logger.error("Score recording error: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal mencatat skor ke database.",
            )
