"""
@module AuthRouter
@desc Endpoint REST API untuk modul autentikasi (login, register, logout, refresh).
      Mengacu pada API Spec §2.1.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    AuthResponse,
    UserResponse,
    TokenResponse,
    RefreshTokenResponse,
)
from app.services.auth_service import AuthService
from app.middleware.auth import get_current_user, decode_token
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Issue JWT token melalui autentikasi username/password.
    Mengacu pada API Spec §2.1.1.

    @param request: LoginRequest dengan username dan password.
    @param db: AsyncSession database.
    @return AuthResponse: Token JWT dan data pengguna.
    """
    try:
        user = await AuthService.authenticate_user(db, request.username, request.password)
        tokens = AuthService.generate_tokens(user)

        return AuthResponse(
            status="success",
            data=TokenResponse(
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                user=UserResponse.model_validate(user),
            ),
            message="Login berhasil.",
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Login endpoint error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan saat memproses login.",
        )


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    Mendaftarkan pengguna baru (Guru BK / Orang Tua).
    Mengacu pada FR-001.1.

    @param request: RegisterRequest dengan data registrasi.
    @param db: AsyncSession database.
    @return AuthResponse: Data pengguna baru tanpa token.
    """
    try:
        user = await AuthService.register_user(
            db=db,
            username=request.username,
            password=request.password,
            full_name=request.full_name,
            role=request.role,
            school_id=request.school_id,
            class_name=request.class_name,
            child_student_id=request.child_student_id,
        )

        tokens = AuthService.generate_tokens(user)
        return AuthResponse(
            status="success",
            data=TokenResponse(
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                user=UserResponse.model_validate(user),
            ),
            message="Registrasi berhasil.",
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Register endpoint error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan saat memproses registrasi.",
        )


@router.post("/logout", response_model=AuthResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout — mencabut token (sisi klien).
    Mengacu pada API Spec §2.1.2.

    @param current_user: User aktif dari JWT.
    @return AuthResponse: Konfirmasi logout.
    """
    logger.info("User '%s' logged out.", current_user.username)
    return AuthResponse(
        status="success",
        data=None,
        message="Token berhasil dicabut. Sesi diakhiri.",
    )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Memperbarui access token menggunakan refresh token.
    Mengacu pada API Spec §2.1.3.

    @param db: AsyncSession database.
    @param current_user: User aktif.
    @return AuthResponse: Access token baru.
    """
    try:
        tokens = AuthService.generate_tokens(current_user)
        return AuthResponse(
            status="success",
            data=RefreshTokenResponse(access_token=tokens["access_token"]),
            message="Access token berhasil diperbarui.",
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Refresh token error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal memperbarui access token.",
        )
