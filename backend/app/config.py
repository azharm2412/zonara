"""
@module Config
@desc Manajemen konfigurasi aplikasi berbasis environment variables.
      Menggunakan Pydantic BaseSettings untuk validasi dan type-safety.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Konfigurasi aplikasi yang dimuat dari environment variables / file .env.

    Attributes:
        PROJECT_NAME (str): Nama proyek untuk metadata API.
        API_V1_STR (str): Prefiks URL untuk API versi 1.
        SECRET_KEY (str): Kunci rahasia untuk signing JWT.
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Masa berlaku access token (menit).
        REFRESH_TOKEN_EXPIRE_DAYS (int): Masa berlaku refresh token (hari).
        DATABASE_URL (str): URL koneksi PostgreSQL (asyncpg).
        POSTGRES_USER (str): Username PostgreSQL.
        POSTGRES_PASSWORD (str): Password PostgreSQL.
        POSTGRES_SERVER (str): Hostname server PostgreSQL.
        POSTGRES_PORT (int): Port server PostgreSQL.
        POSTGRES_DB (str): Nama database PostgreSQL.
    """

    # --- Metadata Aplikasi ---
    PROJECT_NAME: str = "Zonara Character Analytics API"
    API_V1_STR: str = "/api/v1"

    # --- Keamanan JWT ---
    SECRET_KEY: str = "generate-super-secret-key-here-for-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- PostgreSQL Database ---
    POSTGRES_USER: str = "zonara_admin"
    POSTGRES_PASSWORD: str = "zonara_secure_pass"
    POSTGRES_SERVER: str = "db_zonara"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "zonara_analytics"
    DATABASE_URL: Optional[str] = None

    # --- Deployment ---
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    PORT: int = 8000

    @property
    def allowed_origins_list(self) -> list[str]:
        """
        Menghasilkan list CORS origins dari comma-separated string.

        @return list[str]: Daftar origin yang diizinkan.
        """
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def database_url(self) -> str:
        """
        Menghasilkan URL koneksi database.
        Prioritas: DATABASE_URL environment > konstruksi dari komponen.

        @return str: URL koneksi PostgreSQL asyncpg.
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Singleton instance konfigurasi
settings = Settings()
