# MASTER TEST PLAN
## Zonara Character Analytics (Enterprise Edition)
### Mengacu pada IEEE 829-2008

| Atribut | Keterangan |
|---------|-----------|
| **Nomor Dokumen** | ZCA-MTP-2026-001 |
| **Versi** | 1.0 |
| **Tanggal** | 24 Maret 2026 |
| **Klien** | Azhar M |
| **Status** | Draft — Menunggu Persetujuan |

---

## Riwayat Revisi

| Versi | Tanggal | Penulis | Deskripsi |
|-------|---------|---------|-----------|
| 1.0 | 24/03/2026 | Azhar M | Draft awal Master Test Plan |

---

## Daftar Isi

1. [Identifikasi Test Plan](#10-identifikasi-test-plan)
2. [Referensi](#20-referensi)
3. [Item yang Diuji](#30-item-yang-diuji)
4. [Pendekatan Pengujian](#40-pendekatan-pengujian)
5. [Lingkungan Pengujian](#50-lingkungan-pengujian)
6. [Kriteria Lulus/Gagal](#60-kriteria-lulusgagal)
7. [Test Case Detail](#70-test-case-detail)
8. [Matriks Tanggung Jawab](#80-matriks-tanggung-jawab)
9. [Test Case Tambahan](#90-test-case-tambahan)
10. [Jadwal Pengujian](#100-jadwal-pengujian)

---

## 1.0 Identifikasi Test Plan

| Atribut | Nilai |
|---------|-------|
| **Nama Sistem** | Zonara Character Analytics (Enterprise Edition) |
| **Versi Sistem** | 1.0.0 (MVP) |
| **Tanggal Penyusunan** | 24 Maret 2026 |
| **Penulis** | Azhar M |
| **Tipe Pengujian** | Unit, Integration, System, User Acceptance Testing (UAT) |
| **Lingkungan Target** | Docker Compose (PostgreSQL 15, FastAPI, React SPA) |
| **Cakupan** | Seluruh kebutuhan fungsional (FR-001 s/d FR-006) dan kebutuhan non-fungsional terpilih (NFR-01, NFR-02, NFR-06) |

### 1.1 Tujuan Pengujian

Dokumen ini mendefinisikan strategi, lingkungan, kriteria, dan skenario pengujian untuk memverifikasi bahwa sistem Zonara Character Analytics memenuhi seluruh spesifikasi yang tercantum dalam SRS (ZCA-SRS-2026-001) dan beroperasi sesuai arsitektur yang didokumentasikan dalam SAD (ZCA-SAD-2026-001).

### 1.2 Ruang Lingkup Pengujian

| Dalam Cakupan | Di Luar Cakupan |
|----------------|-----------------|
| Autentikasi JWT + RBAC enforcement | Load testing (performa skala ratusan user) |
| QR Scanner decode + card lookup | Penetration testing / security audit |
| Scoring engine + flag intervensi | Cross-browser compatibility (hanya Chrome/Edge) |
| WebSocket broadcast + live sync | Mobile native testing |
| Radar Chart data calculation | Disaster recovery testing |
| PDF & QR code generation | Accessibility (WCAG) testing |
| Time-series & narrative insight | |

---

## 2.0 Referensi

| No. | Dokumen | Nomor | Versi | Relevansi |
|-----|---------|-------|:-----:|-----------|
| 1 | Software Requirements Specification | ZCA-SRS-2026-001 | 1.0 | Sumber kebutuhan fungsional (FR) dan non-fungsional (NFR) yang menjadi basis test case |
| 2 | Software Architecture Document | ZCA-SAD-2026-001 | 1.0 | Definisi lapisan arsitektur, pola komunikasi, dan teknologi yang diuji |
| 3 | Use Case Specification | ZCA-UC-2026-001 | 1.0 | Skenario interaksi (basic/alternative/exception flow) sebagai basis alur pengujian |
| 4 | Database Design Document | ZCA-DBD-2026-001 | 1.0 | Schema, constraint, dan integritas referensial yang harus divalidasi |
| 5 | Project Charter | ZCA-PC-2026-001 | 2.0 | Ruang lingkup dan risiko yang mempengaruhi strategi pengujian |
| 6 | IEEE Std 829-2008 | — | — | Standar format dokumentasi pengujian perangkat lunak |

---

## 3.0 Item yang Diuji

Setiap item pengujian dipetakan ke kebutuhan fungsional dari SRS dan use case yang merepresentasikannya.

| No. | Item Pengujian | FR Terkait | UC Terkait | Prioritas |
|-----|---------------|:----------:|:----------:|:---------:|
| TI-01 | **Autentikasi JWT & RBAC** — Login, register, refresh token, role-based UI rendering, endpoint protection | FR-001 | UC-01 | Critical |
| TI-02 | **QR Scanner & Card Lookup** — Aktivasi kamera, decode QR, card data retrieval, fallback manual input | FR-003 | UC-02 | Critical |
| TI-03 | **Scoring Engine** — Record skor (0/1), agregasi per dimensi, flag intervensi (<80% rata-rata), positive framing | FR-006 | UC-04 | Critical |
| TI-04 | **WebSocket Live-Sync** — Koneksi WS, broadcast skor, auto-reconnect, status indicator | FR-004 | UC-03 | Critical |
| TI-05 | **Radar Chart Rendering** — Data kalkulasi, overlay individu vs kelas, animasi transisi | FR-006 | UC-04 | High |
| TI-06 | **Game Session Management** — Create, add players, complete session, session code generation | FR-002 | UC-06 | High |
| TI-07 | **PDF Report Export** — Generate PDF siswa/kelas, embedded chart, narrative insight, download | FR-005 (implisit) | UC-05 | High |
| TI-08 | **QR Code Generator** — Generate QR per kartu, batch ZIP, printable grid | FR-005 | UC-07 | Medium |
| TI-09 | **Time-Series Growth Tracker** — Query bulanan, line chart data, narrative insight heuristic | — | UC-08 | Medium |
| TI-10 | **Data Integrity & Constraints** — FK, UNIQUE, CHECK constraints, multi-tenant isolation | — | — | High |

---

## 4.0 Pendekatan Pengujian

### 4.1 Unit Testing

| Aspek | Detail |
|-------|--------|
| **Tujuan** | Memverifikasi kebenaran fungsi logika bisnis secara terisolasi (*white-box testing*) |
| **Cakupan** | Service layer backend (Python): `ScoringService`, `AnalyticsService`, `AuthService`, `QRService` |
| **Framework** | `pytest` + `pytest-asyncio` (untuk fungsi async) |
| **Coverage Target** | ≥ 80% *line coverage* pada service layer |
| **Mocking** | `unittest.mock` untuk mengisolasi dependency database (asyncpg) dan external services |

**Fungsi yang diuji secara unit:**

| No. | Fungsi | Modul | Validasi |
|-----|--------|-------|----------|
| UT-01 | `hash_password(plain)` | `auth_service.py` | Output adalah bcrypt hash valid |
| UT-02 | `verify_password(plain, hash)` | `auth_service.py` | Return True untuk password benar, False untuk salah |
| UT-03 | `create_access_token(data)` | `auth_service.py` | JWT valid, exp = 30min, payload benar |
| UT-04 | `calculate_dimension_scores(scores[])` | `scoring_service.py` | Agregasi per zona benar: `{blue: N, green: N, yellow: N, red: N}` |
| UT-05 | `detect_intervention_flags(student_scores, class_avg)` | `scoring_service.py` | Flag muncul jika skor < 80% rata-rata |
| UT-06 | `generate_narrative_insight(current, previous)` | `analytics_service.py` | Narasi berisi kata "peningkatan"/"penguatan" sesuai delta |
| UT-07 | `generate_qr_image(qr_string)` | `qr_service.py` | Output PNG bytes valid |

### 4.2 Integration Testing

| Aspek | Detail |
|-------|--------|
| **Tujuan** | Memverifikasi alur data antar-komponen berjalan benar secara end-to-end dalam satu layer |
| **Cakupan** | Router → Service → Database (FastAPI endpoint testing) |
| **Framework** | `pytest` + `httpx.AsyncClient` (FastAPI TestClient) |
| **Database** | PostgreSQL test database (terpisah dari production), di-recreate per test session |

**Skenario integrasi yang diuji:**

| No. | Skenario | Alur |
|-----|----------|------|
| IT-01 | **Register → Login → Authenticated Request** | `POST /register` → `POST /login` → `GET /me` (dengan JWT header) |
| IT-02 | **QR Scan → Score Record → Database Verification** | `POST /scores` → `SELECT FROM scores WHERE ...` → validasi data tersimpan |
| IT-03 | **Create Session → Add Players → Record Scores → Get Radar** | Full session lifecycle melalui REST endpoints |
| IT-04 | **Score Record → Radar Calculation → Flag Detection** | `POST /scores` → `GET /analytics/radar/class/...` → validasi flags[] |
| IT-05 | **Generate QR → Verify Image** | `GET /qr/cards/1` → validasi response content-type `image/png` |

### 4.3 System Testing

| Aspek | Detail |
|-------|--------|
| **Tujuan** | Memverifikasi sistem secara keseluruhan berfungsi sesuai SRS dalam lingkungan yang menyerupai produksi |
| **Cakupan** | Full-stack: React frontend ↔ FastAPI backend ↔ PostgreSQL, termasuk WebSocket |
| **Metode** | Browser automation testing menggunakan browser subagent |
| **Lingkungan** | Docker Compose (3 container: frontend, backend, db) |

**Skenario sistem yang diuji:**

| No. | Skenario | Deskripsi |
|-----|----------|-----------|
| ST-01 | **WebSocket Cross-Device Sync** | Buka dashboard di Tab A (proyektor) dan game session di Tab B (guru mobile). Record skor di Tab B → verifikasi Radar Chart bergerak di Tab A. |
| ST-02 | **RBAC Enforcement End-to-End** | Login sebagai Orang Tua → verifikasi sidebar hanya menampilkan menu "Ringkasan Anak" → coba akses URL dashboard penuh → verifikasi redirect/403. |
| ST-03 | **Full Game Session Flow** | Login guru → buat sesi → tambah siswa → scan kartu → nilai → akhiri sesi → lihat dashboard → export PDF. |
| ST-04 | **Focus Mode Proyektor** | Buka Focus Mode → verifikasi full-screen, tanpa sidebar, font besar, Radar Chart terbaca dari jarak jauh. |
| ST-05 | **Graceful Degradation** | Putuskan koneksi WebSocket → verifikasi indikator "terputus" muncul → sambungkan kembali → verifikasi auto-reconnect dan data tersinkronisasi. |

### 4.4 User Acceptance Testing (UAT)

| Aspek | Detail |
|-------|--------|
| **Tujuan** | Memvalidasi bahwa sistem memenuhi kebutuhan operasional pengguna akhir (*black-box testing*) |
| **Tester** | Guru BK (1–2 orang), Wali Kelas (1 orang), Orang Tua (1 orang) |
| **Metode** | Skenario berbasis use case, observasi langsung, kuesioner paska-uji |
| **Lingkungan** | Deployment cloud VPS, akses via browser Chrome/Edge |

**Skenario UAT:**

| No. | Skenario | Penguji | Kriteria Sukses |
|-----|----------|---------|-----------------|
| UAT-01 | Guru BK melakukan sesi permainan lengkap (scan QR → nilai → lihat dashboard) | Guru BK | Alur berjalan lancar tanpa error, waktu <30 menit |
| UAT-02 | Guru BK membaca flag intervensi dan narrative insight | Guru BK | Terminologi "Area Pertumbuhan" dipahami, insight relevan |
| UAT-03 | Wali Kelas melihat dashboard kelas dan export PDF | Wali Kelas | Data sesuai, PDF rapi dan informatif |
| UAT-04 | Orang Tua login dan melihat ringkasan anak | Orang Tua | Hanya data anak sendiri yang tampil, tanpa perbandingan |
| UAT-05 | Guru BK mencetak halaman QR code untuk kartu permainan | Guru BK | QR tercetak jelas, terbaca oleh scanner |

---

## 5.0 Lingkungan Pengujian

### 5.1 Kebutuhan Perangkat Keras

| Perangkat | Spesifikasi Minimum | Kegunaan |
|-----------|---------------------|----------|
| **Laptop/PC Pengembang** | CPU 4-core, RAM 8 GB, SSD 50 GB, Webcam 720p | Menjalankan Docker Compose, development, browser testing |
| **Smartphone/Tablet** (opsional) | Android 10+ / iOS 14+, kamera belakang ≥ 8MP | UAT: simulasi scan QR oleh guru di kelas |
| **Proyektor / Monitor Eksternal** | Resolusi ≥ 1024×768 | UAT: simulasi tampilan Focus Mode |
| **Printer A4** | Printer inkjet/laser standar | UAT: cetak halaman QR code |

### 5.2 Kebutuhan Perangkat Lunak

| Komponen | Versi | Keterangan |
|----------|:-----:|------------|
| **Docker Desktop** | 24+ | Container runtime untuk seluruh stack |
| **Docker Compose** | 2.x | Orkestrasi 3 container (frontend, backend, db) |
| **PostgreSQL** | 15 (via Docker) | Database pengujian |
| **Python** | 3.11+ | Backend runtime + test runner |
| **Node.js** | 20 LTS | Frontend build + dev server |
| **pytest** | 8.x | Unit + integration test framework |
| **httpx** | 0.27+ | Async HTTP client untuk integration test |
| **Google Chrome** | Latest | Browser utama pengujian (WebRTC support) |
| **Microsoft Edge** | Latest | Browser alternatif pengujian |

### 5.3 Konfigurasi Lingkungan

| Lingkungan | Konfigurasi | Penggunaan |
|------------|-------------|------------|
| **Development** | `docker-compose -f docker-compose.dev.yml up` | Unit test, integration test, development |
| **Staging** | `docker-compose up` (production config) | System test, UAT |
| **Test Database** | `zonara_test` (terpisah dari `zonara`) | Isolated test data, di-reset per session |

---

## 6.0 Kriteria Lulus/Gagal

### 6.1 Kriteria Global

| Kode | Kriteria | Ambang Batas | Tipe |
|------|----------|:------------:|:----:|
| GL-01 | Seluruh test case **critical** berstatus PASS | 100% | Wajib |
| GL-02 | Seluruh test case **high priority** berstatus PASS | ≥ 95% | Wajib |
| GL-03 | Seluruh test case **medium priority** berstatus PASS | ≥ 90% | Direkomendasikan |
| GL-04 | Tidak ada defect dengan severity **Critical** atau **Blocker** yang belum terselesaikan | 0 defect | Wajib |
| GL-05 | Defect severity **Major** yang belum terselesaikan | ≤ 2 defect | Wajib |
| GL-06 | Unit test code coverage pada service layer | ≥ 80% | Direkomendasikan |

### 6.2 Kriteria Per Tipe Pengujian

| Tipe Pengujian | Kriteria Lulus | Kriteria Gagal |
|----------------|---------------|----------------|
| **Unit Testing** | Seluruh assertion PASS, coverage ≥ 80% | ≥ 1 assertion FAIL pada fungsi kritikal |
| **Integration Testing** | Alur data end-to-end menghasilkan output sesuai expected | Data tidak tersimpan, response mismatch, FK violation |
| **System Testing** | Fitur berjalan di browser Chrome tanpa console error, WebSocket sync < 500ms | Fitur crash, WebSocket gagal connect, UI render error |
| **UAT** | Pengguna dapat menyelesaikan skenario tanpa bantuan teknis, rating kepuasan ≥ 4/5 | Pengguna tidak dapat menyelesaikan alur utama, rating < 3/5 |

### 6.3 Klasifikasi Severity Defect

| Severity | Definisi | Contoh |
|----------|----------|--------|
| **Blocker** | Sistem tidak dapat dijalankan sama sekali | Docker gagal start, database connection refused |
| **Critical** | Fitur utama tidak berfungsi, tidak ada workaround | Login gagal, skor tidak tersimpan, WebSocket crash |
| **Major** | Fitur berfungsi parsial atau ada workaround | Radar Chart tidak menampilkan overlay, PDF tanpa grafik |
| **Minor** | Masalah kosmetik atau UX yang tidak menghambat fungsionalitas | Typo, warna zona tidak presisi, animasi sedikit patah |
| **Trivial** | Sangat kecil, tidak berdampak pada pengguna | Log message tidak rapi, tooltip kurang informatif |

---

## 7.0 Test Case Detail

### TC-01: Login dengan Kredensial Valid dan Verifikasi Token JWT

| Atribut | Detail |
|---------|--------|
| **ID** | TC-01 |
| **Kategori** | Integration Testing |
| **Prioritas** | Critical |
| **FR Terkait** | FR-001.1, FR-001.2, FR-001.3, FR-001.4 |
| **UC Terkait** | UC-01 (Basic Flow, langkah 3–9) |

| Aspek | Deskripsi |
|-------|-----------|
| **Deskripsi** | Memverifikasi bahwa pengguna dengan kredensial valid dapat login dan menerima JWT token yang berisi payload role dan school_id yang benar, serta UI merender navigasi sesuai role |
| **Prasyarat** | (1) Akun guru demo terdaftar: username=`guru_demo`, password=`Demo@1234`, role=`guru_bk`, school_id=1. (2) Backend dan database berjalan. |

| No. | Input | Langkah Pengujian | Expected Output |
|:---:|-------|-------------------|-----------------|
| 1 | — | Buka halaman `/login` | Formulir login tampil: field username, password, tombol "Masuk" |
| 2 | username: `guru_demo`, password: `Demo@1234` | Isi formulir login dan tekan "Masuk" | Request `POST /api/v1/auth/login` terkirim |
| 3 | — | Periksa response API | HTTP 200, body: `{access_token: "eyJ...", refresh_token: "eyJ...", user: {id, role: "guru_bk", school_id: 1}}` |
| 4 | — | Decode access_token (JWT) | Payload: `{sub: user_id, role: "guru_bk", school_id: 1, exp: NOW + 30min}` |
| 5 | — | Verifikasi redirect setelah login | Pengguna diarahkan ke halaman Dashboard |
| 6 | — | Verifikasi sidebar navigasi | Sidebar menampilkan menu lengkap: Game Session, Dashboard, Growth, Reports, QR Generator (role guru_bk) |

| **Status** | ⬜ Belum Dieksekusi |
|------------|---------------------|

---

### TC-02: Pemindaian QR Kartu Tantangan Zona Hijau

| Atribut | Detail |
|---------|--------|
| **ID** | TC-02 |
| **Kategori** | System Testing |
| **Prioritas** | Critical |
| **FR Terkait** | FR-003.1, FR-003.2, FR-003.3, FR-003.4 |
| **UC Terkait** | UC-02 (Basic Flow, langkah 3–11) |

| Aspek | Deskripsi |
|-------|-----------|
| **Deskripsi** | Memverifikasi bahwa pemindaian QR code pada kartu zona hijau menghasilkan popup yang menampilkan misi dengan benar, dan penilaian guru tercatat ke database |
| **Prasyarat** | (1) Guru terautentikasi. (2) Sesi aktif dengan minimal 1 siswa. (3) Kartu fisik zona hijau dengan QR code `ZCA-G-001` tersedia (dicetak dari QR Generator). (4) Kamera perangkat berfungsi. |

| No. | Input | Langkah Pengujian | Expected Output |
|:---:|-------|-------------------|-----------------|
| 1 | — | Buka halaman Game Session, pilih sesi aktif | Daftar pemain tampil |
| 2 | — | Pilih siswa "Andi Pratama" | Siswa ter-highlight |
| 3 | — | Tekan tombol "Scan Kartu" | Kamera aktif, viewfinder QR scanner tampil |
| 4 | QR code kartu `ZCA-G-001` | Arahkan kamera ke QR code pada kartu fisik | QR berhasil di-decode, request `GET /api/v1/cards?qr=ZCA-G-001` terkirim |
| 5 | — | Verifikasi Card Popup | Popup tampil: Judul misi (e.g., "Mendengarkan Teman"), deskripsi misi, badge **hijau** dengan label "Relationship Skills" |
| 6 | — | Tekan tombol **"✅ Berhasil"** | Request `POST /api/v1/scores` terkirim: `{session_id, student_id, card_id, zone_id: 2, result: 1}` |
| 7 | — | Verifikasi database | `SELECT * FROM scores WHERE card_id = [id_kartu] AND student_id = [id_andi]` → 1 row, `result = 1`, `zone_id = 2` (green) |
| 8 | — | Verifikasi notifikasi UI | Popup tertutup, notifikasi "Skor tercatat ✓" muncul dengan animasi fade |

| **Status** | ⬜ Belum Dieksekusi |
|------------|---------------------|

---

### TC-03: Push Update Skor via WebSocket ke Dashboard Proyektor

| Atribut | Detail |
|---------|--------|
| **ID** | TC-03 |
| **Kategori** | System Testing |
| **Prioritas** | Critical |
| **FR Terkait** | FR-004.1, FR-004.2, FR-004.3, FR-004.4 |
| **UC Terkait** | UC-03 (Basic Flow, langkah 1–8) |

| Aspek | Deskripsi |
|-------|-----------|
| **Deskripsi** | Memverifikasi bahwa setelah guru menilai siswa, dashboard yang terbuka di tab/perangkat lain (proyektor) menerima update skor via WebSocket dan Radar Chart beranimasi secara real-time |
| **Prasyarat** | (1) Sesi aktif. (2) Tab A: Dashboard/Focus Mode terbuka untuk sesi yang sama. (3) Tab B: Game Session (untuk input skor). (4) Kedua tab terhubung ke WS. |

| No. | Input | Langkah Pengujian | Expected Output |
|:---:|-------|-------------------|-----------------|
| 1 | — | Di Tab A: Buka Dashboard atau Focus Mode untuk sesi aktif | Radar Chart tampil dengan data saat ini. Indikator koneksi WS berwarna **hijau** ("Terhubung") |
| 2 | — | Di Tab A: Buka browser DevTools → tab Network → filter "WS" | Koneksi WebSocket `ws://host/ws/dashboard/{session_id}` terbuka, status 101 |
| 3 | — | Di Tab B: Scan kartu + tekan "Berhasil" (seperti TC-02) | Skor tercatat di database |
| 4 | — | Di Tab A: Observasi WebSocket messages di DevTools | Pesan diterima: `{event: "score_update", student_id, radar_data: [b,g,y,r], class_average: [...], flags: [...]}` |
| 5 | — | Di Tab A: Observasi Radar Chart | Chart beranimasi: titik pada sumbu zona hijau ("Relationship Skills") bergerak ke posisi baru. **Durasi animasi ≤ 500ms** |
| 6 | — | Ukur latensi: waktu dari tombol "Berhasil" ditekan (Tab B) hingga animasi selesai (Tab A) | **Total latensi ≤ 500ms** (sesuai NFR-02) |

| **Status** | ⬜ Belum Dieksekusi |
|------------|---------------------|

---

### TC-04: Kalkulasi Radar Chart dengan Overlay Rata-rata Kelas

| Atribut | Detail |
|---------|--------|
| **ID** | TC-04 |
| **Kategori** | Integration Testing |
| **Prioritas** | Critical |
| **FR Terkait** | FR-006.1, FR-006.2, FR-006.3, FR-006.5 |
| **UC Terkait** | UC-04 (Basic Flow, langkah 2–9) |

| Aspek | Deskripsi |
|-------|-----------|
| **Deskripsi** | Memverifikasi bahwa endpoint analytics mengembalikan data Radar Chart yang benar (skor individu + rata-rata kelas) dan overlay ditampilkan dengan tepat |
| **Prasyarat** | Sesi `completed` untuk kelas 5A dengan data skor berikut: |

**Data skor sesi yang telah selesai:**

| Siswa | Zona Biru (Self-Awareness) | Zona Hijau (Relationship) | Zona Kuning (Decision Making) | Zona Merah (Assertiveness) |
|-------|:-:|:-:|:-:|:-:|
| Andi | 3/3 = 3 | 2/3 = 2 | 3/3 = 3 | 1/3 = 1 |
| Budi | 2/3 = 2 | 3/3 = 3 | 2/3 = 2 | 2/3 = 2 |
| Citra | 3/3 = 3 | 3/3 = 3 | 3/3 = 3 | 3/3 = 3 |

| No. | Input | Langkah Pengujian | Expected Output |
|:---:|-------|-------------------|-----------------|
| 1 | `GET /api/v1/analytics/radar/class/5A?school_id=1` | Kirim request analytics | HTTP 200 |
| 2 | — | Verifikasi `class_average` | `{blue: 2.67, green: 2.67, yellow: 2.67, red: 2.0}` (rata-rata 3 siswa) |
| 3 | — | Verifikasi data Andi | `radar: [3, 2, 3, 1]` |
| 4 | — | Verifikasi flags Andi | `flags: ["red"]` → karena skor merah Andi (1) < 80% rata-rata kelas (2.0 × 0.8 = 1.6) |
| 5 | — | Buka Dashboard → pilih kelas 5A → klik "Andi" | Radar Chart menampilkan: trace Andi (berwarna) + trace rata-rata kelas (abu-abu transparan) |
| 6 | — | Verifikasi overlay visual | Trace Andi terlihat **lebih kecil** dari rata-rata kelas pada sumbu "Social Awareness & Assertiveness" (Merah) |
| 7 | — | Verifikasi label positive framing | Tabel menampilkan: **"Area Kekuatan"** = Self-Awareness, Decision Making; **"Area Pertumbuhan"** = Social Awareness & Assertiveness |

| **Status** | ⬜ Belum Dieksekusi |
|------------|---------------------|

---

### TC-05: Trigger Alert Anomali (Flag Intervensi)

| Atribut | Detail |
|---------|--------|
| **ID** | TC-05 |
| **Kategori** | Unit + Integration Testing |
| **Prioritas** | Critical |
| **FR Terkait** | FR-006.2, FR-006.3, FR-006.4 |
| **UC Terkait** | UC-04 (Basic Flow, langkah 8–9) |

| Aspek | Deskripsi |
|-------|-----------|
| **Deskripsi** | Memverifikasi bahwa sistem secara otomatis mendeteksi dan menandai (*flag*) siswa yang skornya pada suatu dimensi berada di bawah 80% rata-rata kelas |
| **Prasyarat** | Sama dengan TC-04 (data 3 siswa). Rata-rata kelas zona merah = 2.0. Threshold = 80% × 2.0 = 1.6 |

| No. | Input | Langkah Pengujian | Expected Output |
|:---:|-------|-------------------|-----------------|
| 1 | `student_scores = {blue:3, green:2, yellow:3, red:1}`, `class_avg = {blue:2.67, green:2.67, yellow:2.67, red:2.0}` | Panggil `detect_intervention_flags(student_scores, class_avg)` | Return `["red"]` → skor merah (1) < threshold (1.6) |
| 2 | `student_scores = {blue:3, green:3, yellow:3, red:3}` | Panggil fungsi yang sama untuk Citra | Return `[]` → semua skor ≥ threshold |
| 3 | — | `GET /api/v1/analytics/flags/5A?school_id=1` | Response: `[{student_id: andi_id, name: "Andi", flagged_zones: ["red"], zone_name: "Social Awareness & Assertiveness"}]` |
| 4 | — | Buka Dashboard → kelas 5A | Daftar "Siswa yang Membutuhkan Pendampingan" menampilkan: Andi + ikon ⚠️ merah pada dimensi Assertiveness |
| 5 | — | Verifikasi Radar Chart Andi | Ikon ⚠️ tampil pada sumbu "Social Awareness & Assertiveness" dengan tooltip: *"Area Pertumbuhan: skor di bawah rata-rata kelas"* |

| **Status** | ⬜ Belum Dieksekusi |
|------------|---------------------|

---

### TC-06: Export Laporan PDF Siswa dengan Grafik dan Insight

| Atribut | Detail |
|---------|--------|
| **ID** | TC-06 |
| **Kategori** | Integration Testing |
| **Prioritas** | High |
| **FR Terkait** | FR-006.5 (positive framing) |
| **UC Terkait** | UC-05 (Basic Flow, langkah 1–10) |

| Aspek | Deskripsi |
|-------|-----------|
| **Deskripsi** | Memverifikasi bahwa PDF laporan siswa dihasilkan dengan benar, berisi Radar Chart, tabel skor, narrative insight, dan menggunakan terminologi positive framing |
| **Prasyarat** | Data skor untuk siswa Andi pada kelas 5A tersedia |

| No. | Input | Langkah Pengujian | Expected Output |
|:---:|-------|-------------------|-----------------|
| 1 | — | Buka halaman Reports → pilih "Laporan Per Siswa" → pilih Andi | Preview ringkasan data tampil |
| 2 | — | Tekan "📄 Generate PDF" | Loading indicator tampil, request `GET /api/v1/reports/student/{id}/pdf` terkirim |
| 3 | — | Verifikasi response HTTP | HTTP 200, Content-Type: `application/pdf`, Content-Disposition: `attachment; filename="..."` |
| 4 | — | Buka file PDF yang diunduh | PDF terbuka di viewer, halaman ≥ 1 |
| 5 | — | Verifikasi konten halaman 1 | Header: logo + nama sekolah + tanggal. Data: nama siswa "Andi", NIS, kelas "5A" |
| 6 | — | Verifikasi grafik dalam PDF | Radar Chart ter-embed sebagai gambar (resolusi jelas, 4 sumbu terlabel) |
| 7 | — | Verifikasi terminologi | Menggunakan **"Area Kekuatan"** dan **"Area Pertumbuhan"** — BUKAN "kelemahan" |
| 8 | — | Verifikasi narrative insight | Paragraf deskriptif hadir, mencantumkan dimensi yang kuat dan yang perlu penguatan |

| **Status** | ⬜ Belum Dieksekusi |
|------------|---------------------|

---

### TC-07: Generate & Download QR Code Kartu (Batch ZIP)

| Atribut | Detail |
|---------|--------|
| **ID** | TC-07 |
| **Kategori** | Integration Testing |
| **Prioritas** | Medium |
| **FR Terkait** | FR-005.2, FR-005.3, FR-005.4 |
| **UC Terkait** | UC-07 |

| Aspek | Deskripsi |
|-------|-----------|
| **Deskripsi** | Memverifikasi bahwa sistem dapat menghasilkan QR code untuk seluruh kartu dan mengunduhnya dalam format ZIP |
| **Prasyarat** | 40 kartu seed data tersedia di database (10 per zona) |

| No. | Input | Langkah Pengujian | Expected Output |
|:---:|-------|-------------------|-----------------|
| 1 | — | `GET /api/v1/qr/cards/1` | HTTP 200, Content-Type: `image/png`, gambar QR terbaca |
| 2 | — | Decode QR dari gambar output (menggunakan tools QR reader) | String: `ZCA-B-001` (sesuai `qr_code` di database) |
| 3 | — | `GET /api/v1/qr/cards` (batch) | HTTP 200, Content-Type: `application/zip` |
| 4 | — | Extract ZIP file | 40 file PNG dengan nama `ZCA-B-001.png` s/d `ZCA-R-010.png` |
| 5 | — | Buka halaman QR Generator di frontend | Grid 40 kartu dengan QR preview, label zona, warna badge |

| **Status** | ⬜ Belum Dieksekusi |
|------------|---------------------|

---

### TC-08: RBAC Enforcement — Orang Tua Tidak Dapat Akses Data Siswa Lain

| Atribut | Detail |
|---------|--------|
| **ID** | TC-08 |
| **Kategori** | System Testing (Security) |
| **Prioritas** | Critical |
| **FR Terkait** | FR-001.4 |
| **UC Terkait** | UC-01 (Business Rule BR-03, BR-04) |

| Aspek | Deskripsi |
|-------|-----------|
| **Deskripsi** | Memverifikasi bahwa role Orang Tua hanya dapat mengakses data anak yang terhubung dengan akunnya, dan ditolak saat mengakses data siswa lain |
| **Prasyarat** | (1) Akun orang tua `ortu_andi` terhubung ke `student_id = 1` (Andi). (2) Siswa Budi memiliki `student_id = 2`. |

| No. | Input | Langkah Pengujian | Expected Output |
|:---:|-------|-------------------|-----------------|
| 1 | — | Login sebagai `ortu_andi` | Login berhasil, role = `orang_tua` |
| 2 | — | Verifikasi sidebar | Hanya menu "Ringkasan Anak" yang tampil (tanpa Dashboard, Game Session, Reports penuh) |
| 3 | — | `GET /api/v1/analytics/radar/student/1` (Andi — anak sendiri) | HTTP 200, data radar Andi ditampilkan |
| 4 | — | `GET /api/v1/analytics/radar/student/2` (Budi — anak orang lain) | **HTTP 403 Forbidden** — akses ditolak |
| 5 | — | `GET /api/v1/analytics/radar/class/5A` (dashboard kelas) | **HTTP 403 Forbidden** — Orang Tua tidak boleh lihat perbandingan kelas |
| 6 | — | Verifikasi tampilan Portal Anak | Ringkasan karakter Andi tampil **tanpa perbandingan** dengan siswa lain |

| **Status** | ⬜ Belum Dieksekusi |
|------------|---------------------|

---

### TC-09: Time-Series Growth Tracker — Data Bulanan

| Atribut | Detail |
|---------|--------|
| **ID** | TC-09 |
| **Kategori** | Integration Testing |
| **Prioritas** | High |
| **FR Terkait** | — (time-series analytics) |
| **UC Terkait** | UC-08 |

| Aspek | Deskripsi |
|-------|-----------|
| **Deskripsi** | Memverifikasi bahwa endpoint growth tracker mengembalikan data skor teragregasi per bulan per dimensi untuk siswa tertentu |
| **Prasyarat** | Siswa Andi memiliki skor pada 2 bulan berbeda: Januari (sesi 1) dan Februari (sesi 2) |

| No. | Input | Langkah Pengujian | Expected Output |
|:---:|-------|-------------------|-----------------|
| 1 | `GET /api/v1/analytics/growth/1` (Andi) | Kirim request | HTTP 200 |
| 2 | — | Verifikasi struktur response | Array of `{period: "2026-01", scores: {blue: N, green: N, yellow: N, red: N}}` |
| 3 | — | Verifikasi data Januari | `period: "2026-01", scores: {blue: 2, green: 1, yellow: 2, red: 1}` |
| 4 | — | Verifikasi data Februari | `period: "2026-02", scores: {blue: 3, green: 2, yellow: 3, red: 1}` |
| 5 | — | Buka halaman Growth Tracker → pilih Andi | Line chart menampilkan 4 garis (satu per dimensi) dengan 2 titik data (Jan, Feb) |
| 6 | — | Verifikasi tren visual | Garis biru (Self-Awareness) naik dari 2 ke 3; garis merah (Assertiveness) datar di 1 |

| **Status** | ⬜ Belum Dieksekusi |
|------------|---------------------|

---

### TC-10: Narrative Insight Otomatis — Heuristic Logic

| Atribut | Detail |
|---------|--------|
| **ID** | TC-10 |
| **Kategori** | Unit Testing |
| **Prioritas** | High |
| **FR Terkait** | — (analytics insight) |
| **UC Terkait** | UC-08 |

| Aspek | Deskripsi |
|-------|-----------|
| **Deskripsi** | Memverifikasi bahwa narrative insight generator menghasilkan teks deskriptif yang akurat berdasarkan perbandingan skor antar-periode |
| **Prasyarat** | — |

| No. | Input | Langkah Pengujian | Expected Output |
|:---:|-------|-------------------|-----------------|
| 1 | `current = {blue:3, green:2, yellow:3, red:1}`, `previous = {blue:2, green:1, yellow:2, red:1}` | Panggil `generate_narrative_insight("Andi", current, previous)` | Narasi mengandung: (a) kata "peningkatan" untuk blue, green, yellow; (b) kata "konsisten" atau "penguatan" untuk red |
| 2 | — | Verifikasi positive framing | Narasi TIDAK mengandung kata: "kelemahan", "gagal", "buruk", "rendah" |
| 3 | — | Verifikasi personalisasi | Narasi menyebut nama "Andi" |
| 4 | — | Verifikasi rekomendasi | Terdapat kalimat rekomendasi tindak lanjut untuk dimensi yang stagnan/menurun |
| 5 | `current = {blue:3, green:3, yellow:3, red:3}`, `previous = None` | Panggil fungsi (tanpa data sebelumnya) | Narasi berisi deskripsi umum profil tanpa perbandingan tren |

| **Status** | ⬜ Belum Dieksekusi |
|------------|---------------------|

---

## 8.0 Matriks Tanggung Jawab

Matriks berikut mendefinisikan pembagian tanggung jawab untuk setiap aktivitas pengujian. Mengacu pada model **RACI** (*Responsible, Accountable, Consulted, Informed*).

### 8.1 Matriks RACI Pengujian

| Aktivitas | Pelaksana (R) | Reviewer (A) | Konsultasi (C) | Informasi (I) |
|-----------|:-------------:|:------------:|:--------------:|:-------------:|
| Penyusunan Test Plan | Azhar M | Pembimbing | Guru BK | Klien |
| Perancangan Test Case | Azhar M | Pembimbing | — | Klien |
| Eksekusi Unit Test | Azhar M | — | — | Pembimbing |
| Eksekusi Integration Test | Azhar M | — | — | Pembimbing |
| Eksekusi System Test | Azhar M | Pembimbing | — | Klien |
| Eksekusi UAT | Guru BK, Wali Kelas, Orang Tua | Azhar M | Pembimbing | Klien |
| Pelaporan Defect | Azhar M | Pembimbing | — | Klien |
| Perbaikan Defect (*Bug Fix*) | Azhar M | — | — | Pembimbing |
| Regresi Test (Re-test) | Azhar M | — | — | Pembimbing |
| Validasi Akhir & Sign-off | Pembimbing | Klien | Guru BK | — |

### 8.2 Detail Peran

| Peran | Nama / Jabatan | Tanggung Jawab |
|-------|----------------|----------------|
| **Test Lead / Developer** | Azhar M | Menyusun test plan, merancang test case, mengeksekusi unit/integration/system test, melaporkan defect, memperbaiki bug |
| **Reviewer / Pembimbing** | Dosen Pembimbing | Me-review test plan dan hasil pengujian, memberikan persetujuan (*sign-off*) |
| **UAT Tester — Guru BK** | Perwakilan Guru BK | Mengeksekusi skenario UAT-01 s/d UAT-05 sebagai pengguna utama |
| **UAT Tester — Wali Kelas** | Perwakilan Wali Kelas | Mengeksekusi skenario UAT-03 (dashboard + PDF) |
| **UAT Tester — Orang Tua** | Perwakilan Orang Tua | Mengeksekusi skenario UAT-04 (portal anak) |
| **Klien / Stakeholder** | Azhar M | Menerima laporan hasil pengujian, memberikan *final approval* |

---

## 9.0 Test Case Tambahan

### TC-11: Manajemen Sesi Permainan — Create, Play, Complete

| Atribut | Detail |
|---------|--------|
| **ID** | TC-11 |
| **Kategori** | Integration Testing |
| **Prioritas** | High |
| **FR Terkait** | FR-002.1, FR-002.2, FR-002.5 |
| **UC Terkait** | UC-06 |

| Aspek | Deskripsi |
|-------|-----------|
| **Deskripsi** | Memverifikasi siklus hidup lengkap sesi permainan: pembuatan, penambahan pemain, pelaksanaan, dan pengakhiran |
| **Prasyarat** | Guru BK terautentikasi, minimal 3 siswa terdaftar di kelas 5A |

| No. | Input | Langkah Pengujian | Expected Output |
|:---:|-------|-------------------|-----------------|
| 1 | class_name: "5A" | `POST /api/v1/sessions` → buat sesi baru | HTTP 201, `{id, session_code: "[6 char]", status: "active", started_at: timestamp}` |
| 2 | — | Verifikasi `session_code` | 6 karakter alfanumerik, unik |
| 3 | student_ids: [1, 2, 3] | `POST /api/v1/sessions/{id}/players` → tambah 3 siswa | HTTP 200, `{players: [{id, name}, ...]}` (3 pemain) |
| 4 | — | Coba tambah siswa yang sama | HTTP 409 Conflict (UNIQUE constraint `session_id + student_id`) |
| 5 | — | `PATCH /api/v1/sessions/{id}/complete` → akhiri sesi | HTTP 200, `{status: "completed", ended_at: timestamp}` |
| 6 | — | Verifikasi database | `SELECT * FROM game_sessions WHERE id = ...` → `status = 'completed'`, `ended_at IS NOT NULL` |

| **Status** | ⬜ Belum Dieksekusi |
|------------|---------------------|

---

### TC-12: Fallback Input Manual Ketika Kamera Tidak Tersedia

| Atribut | Detail |
|---------|--------|
| **ID** | TC-12 |
| **Kategori** | System Testing |
| **Prioritas** | High |
| **FR Terkait** | FR-003.5 |
| **UC Terkait** | UC-02 (Alternative Flow AF-01) |

| Aspek | Deskripsi |
|-------|-----------|
| **Deskripsi** | Memverifikasi bahwa mekanisme fallback input manual berfungsi ketika kamera tidak tersedia atau izin akses ditolak |
| **Prasyarat** | Guru terautentikasi, sesi aktif. Kamera diblokir di pengaturan browser. |

| No. | Input | Langkah Pengujian | Expected Output |
|:---:|-------|-------------------|-----------------|
| 1 | — | Blokir izin kamera di Chrome: Settings → Site Settings → Camera → Block | Kamera diblokir |
| 2 | — | Tekan tombol "Scan Kartu" di Game Session | Pesan: *"Akses kamera tidak tersedia."* + form input manual otomatis tampil |
| 3 | ID kartu: `ZCA-G-001` | Ketik ID kartu di text field → tekan "Cari Kartu" | Card Popup tampil identik dengan hasil scan QR (judul, deskripsi, badge hijau) |
| 4 | — | Tekan "✅ Berhasil" | Skor tercatat identik dengan alur scan QR (TC-02 langkah 6–8) |

| **Status** | ⬜ Belum Dieksekusi |
|------------|---------------------|

---

### TC-13: Refresh Token Otomatis Saat Access Token Kedaluwarsa

| Atribut | Detail |
|---------|--------|
| **ID** | TC-13 |
| **Kategori** | Integration Testing |
| **Prioritas** | Critical |
| **FR Terkait** | FR-001.2, FR-001.6 |
| **UC Terkait** | UC-01 (Alternative Flow AF-02) |

| Aspek | Deskripsi |
|-------|-----------|
| **Deskripsi** | Memverifikasi bahwa RTK Query base query secara otomatis memperbarui access token menggunakan refresh token tanpa interupsi pengguna |
| **Prasyarat** | Guru terautentikasi, access token dikonfigurasi dengan expiry sangat pendek (e.g., 10 detik untuk testing) |

| No. | Input | Langkah Pengujian | Expected Output |
|:---:|-------|-------------------|-----------------|
| 1 | — | Login sebagai guru → catat waktu | Access token diterima |
| 2 | — | Tunggu > 10 detik (access token expire) | — |
| 3 | — | Navigasi ke halaman Dashboard (trigger API call) | RTK Query otomatis mengirim `POST /api/v1/auth/refresh` |
| 4 | — | Verifikasi di Network tab | Request refresh berhasil → access token baru diterima → request Dashboard dilanjutkan dengan token baru |
| 5 | — | Verifikasi UX | Pengguna **tidak melihat** halaman login atau interupsi apapun; Dashboard tampil normal |

| **Status** | ⬜ Belum Dieksekusi |
|------------|---------------------|

---

### TC-14: Focus Mode — Tampilan Proyektor Full-Screen

| Atribut | Detail |
|---------|--------|
| **ID** | TC-14 |
| **Kategori** | System Testing |
| **Prioritas** | High |
| **FR Terkait** | — (presentation mode) |
| **UC Terkait** | UC-04 (Alternative Flow AF-01) |

| Aspek | Deskripsi |
|-------|-----------|
| **Deskripsi** | Memverifikasi bahwa Focus Mode menampilkan Radar Chart dalam mode full-screen optimal untuk proyektor kelas |
| **Prasyarat** | Guru terautentikasi, sesi aktif dengan data skor |

| No. | Input | Langkah Pengujian | Expected Output |
|:---:|-------|-------------------|-----------------|
| 1 | — | Buka Dashboard → tekan tombol "Focus Mode" | Halaman beralih ke tampilan full-screen |
| 2 | — | Verifikasi elemen UI | Sidebar **tersembunyi**, header **tersembunyi**, hanya Radar Chart yang tampil |
| 3 | — | Verifikasi ukuran chart | Radar Chart memenuhi ≥ 80% area viewport |
| 4 | — | Verifikasi font | Label sumbu (zona) terbaca dari jarak ≥ 3 meter (font size ≥ 18px) |
| 5 | — | Input skor baru di tab lain | Radar Chart di Focus Mode beranimasi real-time via WebSocket |
| 6 | — | Tekan tombol "Exit" atau Escape | Kembali ke tampilan Dashboard normal dengan sidebar |

| **Status** | ⬜ Belum Dieksekusi |
|------------|---------------------|

---

### TC-15: Integritas Data — Constraint Database

| Atribut | Detail |
|---------|--------|
| **ID** | TC-15 |
| **Kategori** | Integration Testing |
| **Prioritas** | High |
| **FR Terkait** | FR-002.4 (multi-tenant) |
| **UC Terkait** | — |

| Aspek | Deskripsi |
|-------|-----------|
| **Deskripsi** | Memverifikasi bahwa constraint database (FK, UNIQUE, CHECK) berfungsi dengan benar untuk menjaga integritas data |
| **Prasyarat** | Database dengan schema terbuat dan seed data ter-insert |

| No. | Input | Langkah Pengujian | Expected Output |
|:---:|-------|-------------------|-----------------|
| 1 | `result: 2` | `INSERT INTO scores (..., result) VALUES (..., 2)` | **Gagal** — CHECK constraint: `result IN (0, 1)` |
| 2 | `role: 'hacker'` | `INSERT INTO users (..., role) VALUES (..., 'hacker')` | **Gagal** — CHECK constraint: `role IN ('admin','guru_bk','wali_kelas','orang_tua')` |
| 3 | `session_id: 999` | `INSERT INTO scores (session_id, ...) VALUES (999, ...)` | **Gagal** — FK constraint: `session_id` tidak ada di `game_sessions` |
| 4 | Duplikat `session_id + student_id` | `INSERT INTO session_players` dengan kombinasi yang sudah ada | **Gagal** — UNIQUE constraint `uq_session_player` |
| 5 | `DELETE FROM schools WHERE id = 1` | Hapus sekolah yang memiliki siswa dan sesi | **Berhasil** — CASCADE menghapus seluruh data terkait (students, sessions, scores) |
| 6 | `DELETE FROM zones WHERE id = 1` | Hapus zona yang memiliki kartu dengan skor | **Gagal** — RESTRICT: `cards.zone_id` dan `scores.zone_id` mencegah penghapusan |

| **Status** | ⬜ Belum Dieksekusi |
|------------|---------------------|

---

## 10.0 Jadwal Pengujian

### 10.1 Fase Pengujian

| Fase | Aktivitas | Durasi Estimasi | Prasyarat | Deliverable |
|:----:|-----------|:---------------:|-----------|-------------|
| **I** | Persiapan Lingkungan | 0.5 hari | Docker terinstall, kode selesai | Docker Compose berjalan, test DB siap |
| **II** | Unit Testing | 1 hari | Backend service layer selesai | Laporan pytest + coverage ≥80% |
| **III** | Integration Testing | 1 hari | Seluruh endpoint selesai | Laporan httpx test (API flow) |
| **IV** | System Testing | 1 hari | Frontend + backend terintegrasi | Laporan browser test, screenshot |
| **V** | User Acceptance Testing | 1 hari | Deployment staging, pengguna hadir | Kuesioner UAT, sign-off |

### 10.2 Timeline Gantt (Tekstual)

```
Minggu 1                          Minggu 2
Sen  Sel  Rab  Kam  Jum          Sen  Sel  Rab  Kam  Jum
 ├────┤                            │    │    │    │    │
 Fase I                            │    │    │    │    │
      ├─────────┤                  │    │    │    │    │
      Fase II                      │    │    │    │    │
                ├─────────┤        │    │    │    │    │
                Fase III           │    │    │    │    │
                          ├────────┤    │    │    │    │
                          Fase IV       │    │    │    │
                                        ├────┤    │    │
                                        Fase V    │    │
                                             ├────┤
                                          Bug Fix &
                                          Re-test
                                                  ├────┤
                                                Sign-off
```

### 10.3 Kriteria Masuk & Keluar Per Fase

| Fase | Kriteria Masuk (*Entry*) | Kriteria Keluar (*Exit*) |
|:----:|--------------------------|-------------------------|
| **I** | Docker Desktop terinstall, source code lengkap | `docker-compose up` berhasil, semua container healthy |
| **II** | Fase I selesai, service layer lengkap | Seluruh unit test PASS, coverage ≥ 80% |
| **III** | Fase II selesai, seluruh endpoint tersedia | Seluruh integration test PASS, alur data terverifikasi |
| **IV** | Fase III selesai, frontend terintegrasi | Browser test PASS di Chrome, WebSocket sync terverifikasi |
| **V** | Fase IV selesai, deployment staging aktif | UAT PASS, kepuasan pengguna ≥ 4/5, sign-off diperoleh |

---

## Lampiran: Ringkasan Seluruh Test Case

| ID | Deskripsi | Tipe | Prioritas | FR | Status |
|----|-----------|:----:|:---------:|:--:|:------:|
| TC-01 | Login JWT + role rendering | Integration | Critical | FR-001 | ⬜ |
| TC-02 | Scan QR zona hijau + record skor | System | Critical | FR-003 | ⬜ |
| TC-03 | WebSocket push ke proyektor | System | Critical | FR-004 | ⬜ |
| TC-04 | Radar Chart overlay + kalkulasi | Integration | Critical | FR-006 | ⬜ |
| TC-05 | Flag intervensi anomali | Unit+Integration | Critical | FR-006 | ⬜ |
| TC-06 | PDF export dengan grafik + insight | Integration | High | FR-006 | ⬜ |
| TC-07 | Generate QR batch (ZIP) | Integration | Medium | FR-005 | ⬜ |
| TC-08 | RBAC orang tua (child-scoped) | System | Critical | FR-001 | ⬜ |
| TC-09 | Time-series growth data | Integration | High | — | ⬜ |
| TC-10 | Narrative insight heuristic | Unit | High | — | ⬜ |
| TC-11 | Siklus hidup sesi permainan | Integration | High | FR-002 | ⬜ |
| TC-12 | Fallback input manual (tanpa kamera) | System | High | FR-003 | ⬜ |
| TC-13 | Refresh token otomatis | Integration | Critical | FR-001 | ⬜ |
| TC-14 | Focus Mode proyektor | System | High | — | ⬜ |
| TC-15 | Constraint database integrity | Integration | High | FR-002 | ⬜ |

> **Total:** 15 Test Cases (7 Critical, 7 High, 1 Medium)

---

> **Catatan:** Dokumen ini akan diperbarui dengan hasil eksekusi pengujian setelah fase implementasi selesai. Kolom "Status" akan diisi: ✅ PASS, ❌ FAIL, atau ⚠️ BLOCKED.
