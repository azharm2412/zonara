# PROJECT SCAFFOLD & INITIAL SETUP
## Zonara Character Analytics (Enterprise Edition)

### 1. STRUKTUR FOLDER LENGKAP
Proyek ini menggunakan struktur *Monorepo* untuk memudahkan manajemen versi dan orkestrasi menggunakan Docker.

```text
zonara-enterprise/
├── docker-compose.yml           # Orkestrasi container (Frontend, Backend, Database)
├── .env.example                 # Template environment variables
├── .gitignore                   # Aturan pengabaian file Git
├── README.md                    # Dokumentasi utama repositori
│
├── backend/                     # Lapisan Layanan (FastAPI)
│   ├── Dockerfile               # Instruksi build image backend
│   ├── requirements.txt         # Daftar dependensi Python
│   ├── alembic/                 # Manajemen migrasi skema database (PostgreSQL)
│   ├── app/                     # Kode sumber aplikasi utama
│   │   ├── main.py              # Entry point aplikasi & konfigurasi CORS
│   │   ├── config.py            # Manajemen konfigurasi berbasis environment
│   │   ├── database.py          # Logika koneksi asyncpg (Connection pool)
│   │   ├── models/              # Representasi tabel database (SQLAlchemy)
│   │   ├── schemas/             # Pydantic models untuk validasi request/response
│   │   ├── routers/             # Endpoint REST API (Controller layer)
│   │   ├── services/            # Business Logic Layer (Scoring, Auth, Analytics)
│   │   └── middleware/          # JWT verifier & penanganan RBAC
│   └── tests/                   # Skrip pengujian otomatis (Pytest)
│
├── frontend/                    # Lapisan Presentasi (React.js)
│   ├── Dockerfile               # Instruksi build image frontend
│   ├── package.json             # Dependensi Node.js (React, Redux, Recharts, dll)
│   ├── tailwind.config.js       # Konfigurasi utility CSS & palet warna Zonara
│   ├── index.html               # Entry point HTML browser
│   └── src/                     # Kode sumber frontend
│       ├── main.jsx             # React DOM rendering
│       ├── App.jsx              # Konfigurasi React Router & Global Provider
│       ├── store/               # Redux state management & RTK Query
│       ├── pages/               # Halaman utama (Dashboard, Login, Focus Mode)
│       ├── components/          # Komponen UI modular (RadarChart, QRScanner)
│       └── utils/               # Fungsi bantuan teknis dan konstanta (warna zona)
│
└── docs/                        # Repositori Dokumen Rekayasa Perangkat Lunak
    ├── ZCA-PC-2026-001.md       # Project Charter
    ├── ZCA-SRS-2026-001.md      # Spesifikasi Kebutuhan Perangkat Lunak (IEEE 830)
    ├── ZCA-DBD-2026-001.md      # Desain Basis Data (ISO/IEC 9075)
    └── ZCA-API-2026-001.md      # Spesifikasi API (OpenAPI 3.0)
```

### 2. FILE KONFIGURASI DASAR

**A. `.env.example`**
Menyimpan variabel rahasia dan pengaturan lingkungan aplikasi.
```env
# === BACKEND CONFIGURATION ===
PROJECT_NAME="Zonara Character Analytics API"
API_V1_STR="/api/v1"

# Security (JWT)
SECRET_KEY="generate-super-secret-key-here-for-production"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# PostgreSQL Database
POSTGRES_USER=zonara_admin
POSTGRES_PASSWORD=zonara_secure_pass
POSTGRES_SERVER=db_zonara
POSTGRES_PORT=5432
POSTGRES_DB=zonara_analytics
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_SERVER}:${POSTGRES_PORT}/${POSTGRES_DB}

# === FRONTEND CONFIGURATION ===
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_BASE_URL=ws://localhost:8000/ws/analytics
```

**B. `.gitignore`**
Mencegah *file* sampah dan informasi sensitif terunggah ke repositori.
```text
# Python & Backend
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
alembic.ini

# Node.js & Frontend
node_modules/
dist/
build/
.npm/

# Environment
.env
.env.local

# IDEs & OS
.vscode/
.idea/
.DS_Store
```

**C. `README.md` (Instruksi Setup Singkat)**
```markdown
# Zonara Character Analytics (Enterprise Edition)
Phygital Early Warning System mengonversi hasil board game fisik menjadi analitik Radar Chart real-time.

## Prasyarat
- Docker & Docker Compose (Wajib)
- Node.js v20 LTS (Untuk local development frontend)
- Python 3.11+ (Untuk local development backend)

## Memulai Aplikasi (Docker Mode)
1. Salin `.env.example` menjadi `.env`.
2. Jalankan perintah `docker-compose up --build -d`.
3. Frontend dapat diakses di `http://localhost:5173`.
4. API Documentation (Swagger) di `http://localhost:8000/docs`.
```

### 3. KONVENSI KODE

Untuk menjaga standar rekayasa perangkat lunak S2, seluruh anggota tim diwajibkan mematuhi konsensus berikut:

* **Naming Convention:**
    * **PostgreSQL & Python (Backend):** Wajib menggunakan `snake_case` (contoh: `school_id`, `game_sessions`, `def calculate_score()`).
    * **React & JavaScript (Frontend):** Komponen menggunakan `PascalCase` (contoh: `RadarChart.jsx`, `QRScanner.jsx`), sedangkan variabel dan fungsi menggunakan `camelCase` (contoh: `handleScanResult`, `studentData`).
* **Struktur Komentar:**
    * **Backend:** Menggunakan standar *Docstring* Python (PEP 257) di bawah definisi fungsi/kelas untuk menjelaskan argumen, *return type*, dan eksepsi.
    * **Frontend:** Menggunakan *JSDoc* untuk komponen yang menerima *props* kompleks.
* **Error Handling Pattern:**
    * **Backend:** Menangkap galat logika bisnis menggunakan klausa `try...except` dan melempar `HTTPException` standar FastAPI dengan kode status yang tepat (400, 401, 403, 404).
    * **Frontend:** Menangkap galat API secara terpusat melalui *RTK Query middleware* dan menampilkannya sebagai `Toast/Notification` komponen kepada pengguna.
* **Logging Strategy:**
    * Menggunakan modul `logging` standar Python. Menyediakan log level `INFO` untuk jejak *request* REST, dan `ERROR` untuk kegagalan koneksi *database* atau putusnya jaringan *WebSocket*.

### 4. SETUP INSTRUKSI (Localhost via Docker)

Sesuai kesepakatan arsitektur, *setup* akan dilakukan melalui Docker Compose agar terhindar dari isu inkonsistensi *environment* saat demonstrasi KRENOVA.

**Langkah 1: Kloning & Persiapan Lingkungan**
Buka terminal dan navigasikan ke ruang kerja Anda.
```bash
# Clone repository
git clone https://github.com/username/zonara-enterprise.git
cd zonara-enterprise

# Persiapkan file environment
cp .env.example .env
```

**Langkah 2: Orkestrasi Docker**
Eksekusi orkestrasi untuk membangun *image* Frontend (Vite), Backend (FastAPI), dan mengunduh image Database (PostgreSQL 15).
```bash
docker-compose up --build -d
```
*Catatan: Proses ini mungkin membutuhkan waktu beberapa menit pada run pertama.*

**Langkah 3: Migrasi Database & Seeding**
Setelah kontainer aktif, terapkan skema DDL ke PostgreSQL dan masukkan *seed data* (zona, kartu tantangan).
```bash
# Jalankan migrasi Alembic
docker-compose exec backend alembic upgrade head

# Jalankan skrip penyemaian data awal
docker-compose exec backend python app/seed.py
```

**Langkah 4: Validasi Aplikasi Berjalan**
Buka browser modern (Google Chrome/Microsoft Edge):
* Akses UI Aplikasi: `http://localhost:5173`
* Akses Dokumentasi API Interaktif: `http://localhost:8000/docs`



