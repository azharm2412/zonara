"""
@module ScanRouter
@desc Endpoint REST API untuk proses scan QR code dan pencatatan skor.
      Mengacu pada API Spec §2.2.3 dan FR-003.
      
      v1.1:
      - Pisahkan alur menjadi 2 step: lookup kartu → catat skor
      - Endpoint lookup mengembalikan info kartu lengkap (title, zone, description)
      - Endpoint score menerima card_id + result dari frontend
      
@author Azhar Maulana
@date 25 Maret 2026
@version 1.1
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.score import ScanScoreRequest, ScanScoreResponse
from app.services.scoring_service import ScoringService
from app.middleware.auth import get_current_user, RoleChecker

logger = logging.getLogger(__name__)
router = APIRouter()


# --- Request/Response schemas untuk lookup ---

class CardLookupRequest(BaseModel):
    """Schema untuk request lookup kartu via QR code."""
    session_id: int = Field(..., gt=0, description="ID sesi permainan aktif")
    student_id: int = Field(..., gt=0, description="ID siswa yang dinilai")
    qr_code: str = Field(..., min_length=1, max_length=100, description="String QR code kartu")


class CardLookupResponse(BaseModel):
    """Schema response setelah kartu berhasil ditemukan."""
    status: str = "success"
    data: dict
    message: str


class ScoreConfirmRequest(BaseModel):
    """Schema untuk request konfirmasi skor setelah lookup kartu."""
    session_id: int = Field(..., gt=0, description="ID sesi permainan aktif")
    student_id: int = Field(..., gt=0, description="ID siswa yang dinilai")
    card_id: int = Field(..., gt=0, description="ID kartu (dari hasil lookup)")
    zone_id: int = Field(..., gt=0, description="ID zona (dari hasil lookup)")
    result: int = Field(..., ge=0, le=1, description="0 = Gagal, 1 = Berhasil")


# --- Endpoint 1: Lookup kartu + validasi sesi (TANPA catat skor) ---

@router.post(
    "/lookup",
    response_model=CardLookupResponse,
    dependencies=[Depends(RoleChecker(["admin", "guru_bk"]))],
)
async def lookup_card(
    request: CardLookupRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Step 1: Lookup kartu dari QR code dan validasi sesi + siswa.
    Mengembalikan info kartu lengkap (title, zona, deskripsi, difficulty)
    TANPA mencatat skor — skor dicatat di step 2 setelah guru konfirmasi.

    @param request: CardLookupRequest dengan session_id, student_id, qr_code.
    @param db: AsyncSession database.
    @param current_user: Guru BK / Admin yang memindai.
    @return CardLookupResponse: Info kartu lengkap.
    """
    try:
        # 1. Lookup kartu dari QR code (dengan joinedload zone)
        card = await ScoringService.lookup_card_by_qr(db, request.qr_code)

        # 2. Validasi sesi aktif dan siswa terdaftar
        await ScoringService.validate_session_player(
            db, request.session_id, request.student_id
        )

        # 3. Kembalikan info kartu lengkap
        return CardLookupResponse(
            status="success",
            data={
                "card_id": card.id,
                "qr_code": card.qr_code,
                "title": card.title,
                "description": card.description,
                "difficulty": card.difficulty,
                "zone_id": card.zone_id,
                "zone_name": card.zone.name if card.zone else "Unknown",
                "zone_code": card.zone.code if card.zone else "unknown",
                "zone_color": card.zone.color_hex if card.zone else "#888888",
                "zone_dimension": card.zone.sel_dimension if card.zone else "",
            },
            message=f"Kartu '{card.title}' ditemukan di zona {card.zone.name if card.zone else 'Unknown'}.",
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Card lookup error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mencari data kartu.",
        )


# --- Endpoint 2: Konfirmasi dan catat skor ---

@router.post(
    "/confirm",
    response_model=ScanScoreResponse,
    dependencies=[Depends(RoleChecker(["admin", "guru_bk"]))],
)
async def confirm_score(
    request: ScoreConfirmRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Step 2: Guru konfirmasi hasil (Berhasil/Gagal) dan skor dicatat ke database.
    Dipanggil setelah step 1 (lookup) menampilkan info kartu ke guru.

    @param request: ScoreConfirmRequest dengan card_id, zone_id, result.
    @param db: AsyncSession database.
    @param current_user: Guru BK / Admin.
    @return ScanScoreResponse: Konfirmasi skor tercatat.
    """
    try:
        # Catat skor ke database + broadcast ke WebSocket
        score = await ScoringService.record_score(
            db=db,
            session_id=request.session_id,
            student_id=request.student_id,
            card_id=request.card_id,
            zone_id=request.zone_id,
            result_value=request.result,
        )

        status_label = "Berhasil" if request.result == 1 else "Perlu Bimbingan"

        return ScanScoreResponse(
            status="success",
            data={
                "score_id": score.id,
                "zone_id": request.zone_id,
                "result": request.result,
            },
            message=f"Skor '{status_label}' berhasil dicatat ke database.",
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Confirm score error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mencatat skor.",
        )


# --- Legacy endpoint (backward compat) ---

@router.post(
    "",
    response_model=ScanScoreResponse,
    dependencies=[Depends(RoleChecker(["admin", "guru_bk"]))],
)
async def scan_and_score(
    request: ScanScoreRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Legacy: Memproses QR scan dan langsung mencatat skor (1-step).
    Dipertahankan untuk backward compatibility.
    Mengacu pada API Spec §2.2.3.

    @param request: ScanScoreRequest dengan session_id, student_id, qr_code, result.
    @param db: AsyncSession database.
    @param current_user: Guru BK / Admin yang memindai.
    @return ScanScoreResponse: Konfirmasi skor tercatat dengan data zona.
    """
    try:
        # 1. Lookup kartu dari QR code
        card = await ScoringService.lookup_card_by_qr(db, request.qr_code)

        # 2. Validasi sesi aktif dan siswa terdaftar
        await ScoringService.validate_session_player(
            db, request.session_id, request.student_id
        )

        # 3. Catat skor ke database
        score = await ScoringService.record_score(
            db=db,
            session_id=request.session_id,
            student_id=request.student_id,
            card_id=card.id,
            zone_id=card.zone_id,
            result_value=request.result,
        )

        return ScanScoreResponse(
            status="success",
            data={
                "score_id": score.id,
                "zone_id": card.zone_id,
                "zone_name": card.zone.name if card.zone else "Unknown",
                "card_title": card.title,
                "card_description": card.description,
            },
            message="Skor berhasil dicatat.",
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Scan and score error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal memproses scan dan skor.",
        )
