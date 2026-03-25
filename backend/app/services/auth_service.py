"""
@module AuthService
@desc Business logic layer untuk autentikasi: login, registrasi, refresh token.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user import User
from app.middleware.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)

logger = logging.getLogger(__name__)


class AuthService:
    """
    Layanan autentikasi yang mengelola proses login, registrasi,
    dan refresh token.
    """

    @staticmethod
    async def authenticate_user(
        db: AsyncSession, username: str, password: str
    ) -> User:
        """
        Memvalidasi kredensial login pengguna.

        @param db: AsyncSession database.
        @param username: Username yang dikirim user.
        @param password: Password plain text.
        @return User: Instance User jika kredensial valid.
        @raises HTTPException: 401 jika username tidak ditemukan atau password salah.
        """
        try:
            result = await db.execute(
                select(User).where(User.username == username)
            )
            user = result.scalar_one_or_none()
        except Exception as exc:
            logger.error("Database error during authentication: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Kesalahan internal saat memproses autentikasi.",
            )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Username tidak ditemukan.",
            )

        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password salah.",
            )

        logger.info("User '%s' authenticated successfully.", username)
        return user

    @staticmethod
    def generate_tokens(user: User) -> dict:
        """
        Menghasilkan access token dan refresh token untuk user.

        @param user: Instance User yang terautentikasi.
        @return dict: Dictionary berisi access_token dan refresh_token.
        """
        token_data = {
            "sub": str(user.id),
            "role": user.role,
            "school_id": user.school_id,
        }
        return {
            "access_token": create_access_token(token_data),
            "refresh_token": create_refresh_token(token_data),
        }

    @staticmethod
    async def register_user(
        db: AsyncSession,
        username: str,
        password: str,
        full_name: str,
        role: str,
        school_id: int = None,
        class_name: str = None,
        child_student_id: int = None,
    ) -> User:
        """
        Mendaftarkan pengguna baru ke database.

        @param db: AsyncSession database.
        @param username: Username unik.
        @param password: Password plain text (akan di-hash).
        @param full_name: Nama lengkap.
        @param role: Peran RBAC.
        @param school_id: ID sekolah (opsional).
        @param class_name: Kelas (opsional, untuk wali_kelas).
        @param child_student_id: ID siswa anak (opsional, untuk orang_tua).
        @return User: Instance User yang baru dibuat.
        @raises HTTPException: 400 jika username sudah terdaftar.
        """
        try:
            # Cek duplikasi username
            existing = await db.execute(
                select(User).where(User.username == username)
            )
            if existing.scalar_one_or_none() is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Username '{username}' sudah terdaftar.",
                )

            # Buat user baru
            new_user = User(
                username=username,
                password_hash=hash_password(password),
                full_name=full_name,
                role=role,
                school_id=school_id,
                class_name=class_name,
                child_student_id=child_student_id,
            )
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)

            logger.info("New user registered: '%s' (role: %s)", username, role)
            return new_user

        except HTTPException:
            raise
        except Exception as exc:
            await db.rollback()
            logger.error("Registration error: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal mendaftarkan pengguna baru.",
            )

    @staticmethod
    async def refresh_access_token(db: AsyncSession, refresh_token: str) -> str:
        """
        Menghasilkan access token baru dari refresh token yang valid.

        @param db: AsyncSession database.
        @param refresh_token: Refresh token JWT.
        @return str: Access token baru.
        @raises HTTPException: 401 jika refresh token tidak valid.
        """
        payload = decode_token(refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token type bukan refresh token.",
            )

        user_id = payload.get("sub")
        try:
            result = await db.execute(select(User).where(User.id == int(user_id)))
            user = result.scalar_one_or_none()
        except Exception as exc:
            logger.error("Database error during token refresh: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal memverifikasi refresh token.",
            )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Pengguna tidak ditemukan.",
            )

        token_data = {
            "sub": str(user.id),
            "role": user.role,
            "school_id": user.school_id,
        }
        return create_access_token(token_data)
