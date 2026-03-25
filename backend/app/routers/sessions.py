"""
@module SessionsRouter
@desc Endpoint REST API untuk manajemen sesi permainan board game.
      Mengacu pada API Spec §2.2.1 dan FR-002.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

import logging
import string
import random
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.game_session import GameSession
from app.models.session_player import SessionPlayer
from app.models.student import Student
from app.schemas.game_session import SessionCreate, SessionCreateResponse
from app.middleware.auth import get_current_user, RoleChecker

logger = logging.getLogger(__name__)
router = APIRouter()


def generate_session_code(length: int = 6) -> str:
    """
    Menghasilkan kode sesi alfanumerik acak.

    @param length: Panjang kode sesi (default: 6).
    @return str: Kode sesi unik.
    """
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=length))


@router.post(
    "",
    response_model=SessionCreateResponse,
    dependencies=[Depends(RoleChecker(["admin", "guru_bk"]))],
)
async def create_session(
    request: SessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Membuat sesi permainan baru. Hanya Admin dan Guru BK yang diizinkan.
    Auto-close: semua sesi aktif milik guru ini akan di-completed sebelum membuat sesi baru.
    Mengacu pada API Spec §2.2.1.

    @param request: SessionCreate dengan class_name dan student_ids.
    @param db: AsyncSession database.
    @param current_user: User yang membuat sesi.
    @return SessionCreateResponse: Data sesi yang baru dibuat.
    """
    try:
        # --- AUTO-CLOSE: Tutup semua sesi aktif milik guru ini ---
        try:
            auto_close_result = await db.execute(
                update(GameSession)
                .where(
                    GameSession.teacher_id == current_user.id,
                    GameSession.status == "active",
                )
                .values(
                    status="completed",
                    ended_at=func.now(),
                )
            )
            closed_count = auto_close_result.rowcount
            if closed_count > 0:
                logger.info(
                    "Auto-closed %d active session(s) for teacher %s",
                    closed_count, current_user.username,
                )
        except Exception as auto_close_err:
            logger.warning("Auto-close failed (non-fatal): %s", str(auto_close_err))

        # Validasi siswa ada di database dan di sekolah yang sama
        for sid in request.student_ids:
            result = await db.execute(
                select(Student).where(
                    Student.id == sid,
                    Student.school_id == current_user.school_id,
                )
            )
            if result.scalar_one_or_none() is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Siswa ID {sid} tidak ditemukan di sekolah Anda.",
                )

        # Generate kode sesi unik
        session_code = generate_session_code()

        # Buat sesi baru
        new_session = GameSession(
            session_code=session_code,
            school_id=current_user.school_id,
            class_name=request.class_name,
            teacher_id=current_user.id,
        )
        db.add(new_session)
        await db.flush()

        # Daftarkan pemain ke sesi
        for sid in request.student_ids:
            player = SessionPlayer(session_id=new_session.id, student_id=sid)
            db.add(player)

        await db.commit()
        await db.refresh(new_session)

        logger.info(
            "Session %s created by %s for class %s",
            session_code, current_user.username, request.class_name,
        )

        return SessionCreateResponse(
            status="success",
            data={
                "session_id": new_session.id,
                "session_code": new_session.session_code,
                "status": new_session.status,
            },
            message="Sesi permainan berhasil dibuat.",
        )

    except HTTPException:
        raise
    except Exception as exc:
        await db.rollback()
        logger.error("Create session error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal membuat sesi permainan.",
        )


@router.patch(
    "/{session_id}/end",
    dependencies=[Depends(RoleChecker(["admin", "guru_bk"]))],
)
async def end_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mengakhiri sesi permainan (status → completed).
    Mengacu pada FR-002.5.

    @param session_id: ID sesi yang akan diakhiri.
    @param db: AsyncSession database.
    @param current_user: User yang mengakhiri sesi.
    @return dict: Konfirmasi sesi berakhir.
    """
    try:
        result = await db.execute(
            select(GameSession).where(
                GameSession.id == session_id,
                GameSession.school_id == current_user.school_id,
            )
        )
        session = result.scalar_one_or_none()

        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sesi permainan tidak ditemukan.",
            )

        if session.status == "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sesi sudah selesai.",
            )

        session.status = "completed"
        session.ended_at = func.now()
        await db.commit()

        logger.info("Session %d ended by %s", session_id, current_user.username)

        return {
            "status": "success",
            "data": {"session_id": session_id, "status": "completed"},
            "message": "Sesi permainan berhasil diakhiri.",
        }

    except HTTPException:
        raise
    except Exception as exc:
        await db.rollback()
        logger.error("End session error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mengakhiri sesi permainan.",
        )


@router.get("/{session_id}/players")
async def get_session_players(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mengambil daftar siswa yang terdaftar sebagai pemain di sesi tertentu.

    @param session_id: ID sesi permainan.
    @param db: AsyncSession database.
    @param current_user: User yang login.
    @return dict: Daftar pemain sesi.
    """
    try:
        # Validasi sesi milik sekolah user
        session_result = await db.execute(
            select(GameSession).where(
                GameSession.id == session_id,
                GameSession.school_id == current_user.school_id,
            )
        )
        session = session_result.scalar_one_or_none()

        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sesi permainan tidak ditemukan.",
            )

        # Ambil pemain dengan data siswa
        player_result = await db.execute(
            select(SessionPlayer, Student)
            .join(Student, SessionPlayer.student_id == Student.id)
            .where(SessionPlayer.session_id == session_id)
        )
        players = player_result.all()

        return {
            "status": "success",
            "data": {
                "players": [
                    {
                        "id": student.id,
                        "full_name": student.full_name,
                        "nis": student.nis if hasattr(student, 'nis') else None,
                        "class_name": student.class_name,
                    }
                    for _, student in players
                ]
            },
            "message": f"Daftar pemain sesi {session_id} berhasil diambil.",
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Get session players error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mengambil daftar pemain sesi.",
        )


@router.get("")
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mengambil daftar sesi permainan milik sekolah pengguna.

    @param db: AsyncSession database.
    @param current_user: User yang login.
    @return dict: Daftar sesi permainan.
    """
    try:
        result = await db.execute(
            select(GameSession)
            .where(GameSession.school_id == current_user.school_id)
            .order_by(GameSession.started_at.desc())
        )
        sessions = result.scalars().all()

        return {
            "status": "success",
            "data": {
                "sessions": [
                    {
                        "id": s.id,
                        "session_code": s.session_code,
                        "class_name": s.class_name,
                        "status": s.status,
                        "started_at": s.started_at.isoformat() if s.started_at else None,
                        "ended_at": s.ended_at.isoformat() if s.ended_at else None,
                    }
                    for s in sessions
                ]
            },
            "message": "Daftar sesi berhasil diambil.",
        }

    except Exception as exc:
        logger.error("List sessions error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mengambil daftar sesi.",
        )
