"""
@module AuthSchemas
@desc Pydantic models untuk validasi request/response modul autentikasi.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

from pydantic import BaseModel, Field
from typing import Optional


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------
class LoginRequest(BaseModel):
    """
    Schema validasi untuk request login.

    Attributes:
        username (str): Username pengguna (wajib, 3-100 karakter).
        password (str): Password pengguna (wajib, minimal 6 karakter).
    """
    username: str = Field(..., min_length=3, max_length=100, description="Username login")
    password: str = Field(..., min_length=6, description="Password pengguna")


class RegisterRequest(BaseModel):
    """
    Schema validasi untuk request registrasi pengguna baru.

    Attributes:
        username (str): Username unik.
        password (str): Password minimal 6 karakter.
        full_name (str): Nama lengkap pengguna.
        role (str): Peran RBAC.
        school_id (int): ID sekolah (opsional).
        class_name (str): Kelas (opsional, untuk wali_kelas).
        child_student_id (int): ID siswa anak (opsional, untuk orang_tua).
    """
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2, max_length=255)
    role: str = Field(..., pattern="^(admin|guru_bk|wali_kelas|orang_tua)$")
    school_id: Optional[int] = None
    class_name: Optional[str] = None
    child_student_id: Optional[int] = None


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------
class UserResponse(BaseModel):
    """
    Schema response untuk data pengguna (tanpa password_hash).
    """
    id: int
    username: str
    full_name: str
    role: str
    school_id: Optional[int] = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """
    Schema response untuk token JWT setelah login berhasil.
    """
    access_token: str
    refresh_token: str
    user: UserResponse


class RefreshTokenResponse(BaseModel):
    """
    Schema response untuk access token baru setelah refresh.
    """
    access_token: str


class AuthResponse(BaseModel):
    """
    Schema response wrapper standar untuk modul autentikasi.
    """
    status: str = "success"
    data: Optional[TokenResponse | RefreshTokenResponse | None] = None
    message: str
