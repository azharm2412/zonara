"""
@module AuthMiddleware
@desc Middleware autentikasi JWT dan otorisasi RBAC.
      Menyediakan dependency injection untuk FastAPI: get_current_user, RoleChecker.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Password Hashing — bcrypt dengan salt round 12
# ---------------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------------------------------------------------------------
# JWT Configuration
# ---------------------------------------------------------------------------
ALGORITHM = "HS256"
security_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    """
    Meng-hash password menggunakan bcrypt.

    @param password: Password plain text.
    @return str: Password yang sudah di-hash.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Memverifikasi password plain terhadap hash.

    @param plain_password: Password plain text dari input user.
    @param hashed_password: Password hash dari database.
    @return bool: True jika cocok, False jika tidak.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Membuat JWT access token.

    @param data: Payload data yang akan di-encode ke dalam token.
    @param expires_delta: Durasi kadaluarsa token (opsional).
    @return str: JWT access token string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """
    Membuat JWT refresh token dengan masa berlaku lebih lama.

    @param data: Payload data yang akan di-encode ke dalam token.
    @return str: JWT refresh token string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Mendekode dan memvalidasi JWT token.

    @param token: JWT token string.
    @return dict: Payload data dari token.
    @raises HTTPException: Jika token tidak valid atau sudah kadaluarsa.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning("JWT decode failed: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid atau sudah kedaluwarsa.",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency injection: mengambil user aktif dari JWT access token.

    @param credentials: HTTP Bearer token dari header Authorization.
    @param db: AsyncSession database.
    @return User: Instance model User yang sedang login.
    @raises HTTPException: 401 jika token invalid, 404 jika user tidak ditemukan.
    """
    payload = decode_token(credentials.credentials)

    # Validasi tipe token — hanya access token yang diterima
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token type tidak valid. Gunakan access token.",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak mengandung informasi pengguna.",
        )

    try:
        result = await db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()
    except Exception as exc:
        logger.error("Database query error in get_current_user: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mengambil data pengguna dari database.",
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pengguna tidak ditemukan.",
        )

    return user


class RoleChecker:
    """
    Dependency injection untuk validasi RBAC.
    Mengecek apakah user memiliki role yang diizinkan untuk mengakses endpoint.

    Usage:
        @router.get("/admin-only", dependencies=[Depends(RoleChecker(["admin"]))])
    """

    def __init__(self, allowed_roles: List[str]):
        """
        @param allowed_roles: Daftar role yang diizinkan (e.g., ["admin", "guru_bk"]).
        """
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        """
        Memvalidasi role user terhadap daftar role yang diizinkan.

        @param current_user: User dari dependency get_current_user.
        @return User: User yang tervalidasi.
        @raises HTTPException: 403 jika role tidak diizinkan.
        """
        if current_user.role not in self.allowed_roles:
            logger.warning(
                "Access denied for user %s (role: %s). Required: %s",
                current_user.username, current_user.role, self.allowed_roles
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Akses ditolak. Role '{current_user.role}' tidak memiliki izin.",
            )
        return current_user
