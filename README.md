# Zonara Character Analytics (Enterprise Edition)

**Phygital Early Warning System** — Mengonversi hasil board game fisik menjadi analitik Radar Chart real-time untuk deteksi dini kerentanan moral siswa Sekolah Dasar.

## Arsitektur

| Layer | Teknologi |
|-------|-----------|
| **Frontend** | React 18, Vite, Tailwind CSS v3, Redux Toolkit, Recharts, Framer Motion |
| **Backend** | FastAPI, SQLAlchemy (async), Alembic, Pydantic v2 |
| **Database** | PostgreSQL 15 |
| **Deployment** | Docker & Docker Compose |

## Prasyarat

- Docker & Docker Compose (Wajib)
- Node.js v20 LTS (Untuk local development frontend)
- Python 3.11+ (Untuk local development backend)

## Memulai Aplikasi (Docker Mode)

```bash
# 1. Salin file environment
cp .env.example .env

# 2. Jalankan orkestrasi Docker
docker-compose up --build -d

# 3. Jalankan migrasi database
docker-compose exec backend alembic upgrade head

# 4. Jalankan seeder data awal
docker-compose exec backend python app/seed.py
```

## Akses Aplikasi

| Layanan | URL |
|---------|-----|
| Frontend (UI) | `http://localhost:5173` |
| Backend (Swagger Docs) | `http://localhost:8000/docs` |
| PostgreSQL | `localhost:5432` |

## Struktur Proyek

```text
zonara-enterprise/
├── docker-compose.yml
├── backend/              # FastAPI + SQLAlchemy + Alembic
│   ├── app/
│   │   ├── models/       # ORM models (8 tabel)
│   │   ├── schemas/      # Pydantic validasi
│   │   ├── routers/      # REST API endpoints
│   │   ├── services/     # Business logic
│   │   └── middleware/   # JWT & RBAC
│   └── tests/            # Pytest
├── frontend/             # React + Vite + Tailwind v3
│   └── src/
│       ├── pages/        # Halaman utama
│       ├── components/   # Komponen UI
│       └── store/        # Redux & RTK Query
└── docs/                 # Dokumen IEEE (SRS, DBD, API Spec)
```

## Standar Dokumen

- **SRS** — IEEE 830-1998
- **Database Design** — ISO/IEC 9075
- **API Specification** — OpenAPI 3.0
- **Quality Assurance** — IEEE 730

## Lisensi

Hak Cipta © 2026 Azhar Maulana. Seluruh hak dilindungi.
