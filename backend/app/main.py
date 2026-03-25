"""
@module Main
@desc Entry point aplikasi FastAPI. Mengonfigurasi CORS, router, logging,
      dan lifespan events (startup/shutdown) untuk koneksi database.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.routers import auth, sessions, students, scan, analytics, export, ws_analytics

# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan Events — Startup & Shutdown
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Mengelola siklus hidup aplikasi.
    - Startup: Log konfirmasi koneksi database.
    - Shutdown: Menutup connection pool engine.

    @param app: Instance FastAPI.
    """
    logger.info("🚀 Zonara API starting — Database: %s", settings.POSTGRES_SERVER)
    yield
    await engine.dispose()
    logger.info("🛑 Zonara API shutdown — Connection pool disposed.")


# ---------------------------------------------------------------------------
# FastAPI Application Instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Phygital Early Warning System — Mengonversi hasil board game fisik "
        "menjadi analitik Radar Chart real-time untuk deteksi dini kerentanan "
        "moral siswa Sekolah Dasar."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS Middleware — Izinkan frontend dev server
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("🔒 CORS Origins: %s", settings.allowed_origins_list)

# ---------------------------------------------------------------------------
# Router Registration — Prefixed under /api/v1
# ---------------------------------------------------------------------------
API_PREFIX = settings.API_V1_STR

app.include_router(auth.router, prefix=f"{API_PREFIX}/auth", tags=["Autentikasi"])
app.include_router(sessions.router, prefix=f"{API_PREFIX}/sessions", tags=["Sesi Permainan"])
app.include_router(students.router, prefix=f"{API_PREFIX}/students", tags=["Siswa"])
app.include_router(scan.router, prefix=f"{API_PREFIX}/scan", tags=["QR Scan & Scoring"])
app.include_router(analytics.router, prefix=f"{API_PREFIX}/analytics", tags=["Analitik"])
app.include_router(export.router, prefix=f"{API_PREFIX}/export", tags=["Ekspor & Laporan"])

# WebSocket Router — tanpa prefix API (langsung /ws/analytics)
app.include_router(ws_analytics.router, prefix="/ws/analytics", tags=["WebSocket Analytics"])


# ---------------------------------------------------------------------------
# Root Health Check
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"])
async def health_check():
    """
    Endpoint health check untuk memvalidasi bahwa API berjalan.

    @return dict: Status kesehatan API.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
    }
