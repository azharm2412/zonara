# PROJECT CHARTER
## Zonara Character Analytics (Enterprise Edition)

| Atribut | Keterangan |
|---------|-----------|
| **Nomor Dokumen** | ZCA-PC-2026-001 |
| **Versi** | 2.0 |
| **Tanggal** | 24 Maret 2026 |
| **Status** | Draft — Menunggu Persetujuan |

---

## Daftar Isi

1. [Informasi Proyek](#10-informasi-proyek)
2. [Latar Belakang & Permasalahan](#20-latar-belakang--permasalahan)
3. [Tujuan & Manfaat Sistem](#30-tujuan--manfaat-sistem)
4. [Ruang Lingkup (Scope)](#40-ruang-lingkup-scope)
5. [Stakeholder & Peran](#50-stakeholder--peran)
6. [Asumsi & Kendala](#60-asumsi--kendala)
7. [Risiko Awal](#70-risiko-awal)
8. [Milestone Utama](#80-milestone-utama)
9. [Persetujuan](#90-persetujuan)

---

## Riwayat Revisi

| Versi | Tanggal | Penulis | Deskripsi Perubahan |
|-------|---------|---------|---------------------|
| 1.0 | 24/03/2026 | Azhar M | Draft awal (arsitektur Streamlit) |
| 2.0 | 24/03/2026 | Azhar M | Migrasi ke Decoupled Architecture (React + FastAPI + PostgreSQL) |

---

## 1.0 Informasi Proyek

| Atribut | Detail |
|---------|--------|
| **Nama Sistem** | Zonara Character Analytics (Enterprise Edition) |
| **Nama Klien** | Azhar M |
| **Lembaga Terkait** | BAPPERIDA Kabupaten Kebumen & Dinas Pendidikan |
| **Domain** | Pendidikan Karakter — Sekolah Dasar |
| **Arsitektur** | Decoupled Architecture (Separation of Concerns) |
| **Tanggal Inisiasi** | 24 Maret 2026 |
| **Versi Dokumen** | 2.0 |
| **Klasifikasi** | KRENOVA (Kreativitas dan Inovasi) — Proposal Inovasi Daerah |

### 1.1 Deskripsi Singkat

Zonara Character Analytics (Enterprise Edition) merupakan sistem **phygital** (*Physical + Digital Integration*) berskala kabupaten yang dirancang untuk mengonversi data kualitatif dari simulasi *board game* fisik menjadi diagnostik kuantitatif berbasis **Radar Chart**. Sistem ini berfungsi sebagai instrumen psikometrik berbasis data yang mengacu pada **CASEL Social-Emotional Learning (SEL) Framework** untuk memetakan profil karakter siswa Sekolah Dasar.

### 1.2 Teknologi Utama

| Layer | Teknologi |
|-------|-----------|
| Frontend | React.js 18 + Tailwind CSS v3 + Framer Motion |
| State Management | Redux Toolkit + RTK Query |
| Visualisasi | Recharts + Framer Motion (animated transitions) |
| QR Scanner | html5-qrcode (frontend-side decoding) |
| Backend | FastAPI (Python 3.11+, asynchronous) |
| Database | PostgreSQL 15 (shared schema, asyncpg pool) |
| Real-time | WebSocket (FastAPI native) |
| Autentikasi | JWT (Access + Refresh Token) + RBAC Middleware |
| QR Generator | qrcode + Pillow (server-side generation) |
| PDF Export | FPDF2 / ReportLab |
| DevOps | Docker Compose (monorepo) |
| API Documentation | OpenAPI 3.0 (Swagger auto-generated) |
| Dokumentasi Formal | IEEE 830 (SRS), IEEE 1016 (SAD), IEEE 829 (Test Plan) |

---

## 2.0 Latar Belakang & Permasalahan

### 2.1 Konteks Permasalahan

Fenomena kenakalan remaja di Kabupaten Kebumen menunjukkan tren yang memerlukan perhatian serius dari seluruh pemangku kepentingan pendidikan. Data dari berbagai lembaga pendidikan dan pemerintahan mengindikasikan bahwa perilaku menyimpang seperti perundungan (*bullying*), penyalahgunaan zat, serta tingginya angka putus sekolah, seringkali berakar dari **kerentanan moral** yang tidak terdeteksi sejak usia dini.

Permasalahan utama yang diidentifikasi:

1. **Absennya Instrumen Deteksi Dini** — Saat ini tidak tersedia sistem terstandarisasi untuk memetakan profil karakter siswa SD secara kuantitatif dan objektif.
2. **Penilaian Subjektif** — Evaluasi karakter masih bergantung pada observasi guru yang bersifat kualitatif, inkonsisten, dan rentan terhadap bias personal.
3. **Tidak Ada Mekanisme Tracking** — Perkembangan karakter siswa tidak terdokumentasi secara longitudinal, sehingga intervensi bersifat reaktif, bukan preventif.
4. **Deskoneksi Fisik-Digital** — Pendekatan pendidikan karakter berbasis permainan (*gamification*) sudah ada, namun hasilnya tidak terdigitalisasi untuk keperluan analitik dan pelaporan.

### 2.2 Solusi yang Diajukan

Zonara Character Analytics menawarkan pendekatan **phygital** yang menjembatani kesenjangan antara interaksi fisik yang engaging (board game) dengan kekuatan analitik digital (Radar Chart diagnostik). Dengan mengacu pada **CASEL SEL Framework**, sistem ini memposisikan diri sebagai:

- **Instrumen psikometrik berbasis data**, bukan sekadar permainan edukatif
- **Early Warning System** yang mendeteksi kerentanan moral sebelum bermanifestasi menjadi kenakalan remaja
- **Platform longitudinal** yang melacak pertumbuhan karakter secara *time-series* per bulan

---

## 3.0 Tujuan & Manfaat Sistem

### 3.1 Tujuan Utama

Membangun sistem analitik karakter yang **scalable**, **aman**, dan memiliki **visualisasi data tingkat tinggi** untuk mentransformasi data kualitatif dari simulasi board game fisik menjadi diagnostik kuantitatif berbasis data.

### 3.2 Tujuan Spesifik

| No. | Tujuan | Indikator Keberhasilan |
|-----|--------|------------------------|
| T-01 | Digitalisasi penilaian karakter berbasis CASEL | ≥90% data sesi permainan terekam secara digital |
| T-02 | Deteksi dini kerentanan moral (Early Warning) | Flag Intervensi otomatis jika skor dimensi < 80% rata-rata kelas |
| T-03 | Monitoring pertumbuhan karakter longitudinal | Tersedia grafik *time-series* per dimensi per siswa (evaluasi bulanan) |
| T-04 | Sinkronisasi phygital secara real-time | QR scan → WebSocket push → Radar Chart beranimasi di proyektor (< 500ms) |
| T-05 | Pelaporan profesional bergaya akademik | Export PDF dengan grafik, rekomendasi, dan format formal |
| T-06 | Skalabilitas tingkat kabupaten | Multi-tenant (school_id) untuk seluruh SD di Kebumen |

### 3.3 Manfaat Sistem

| Pemangku Kepentingan | Manfaat |
|----------------------|---------|
| **Guru BK** | Peta karakter digital per siswa, deteksi anomali otomatis, laporan siap cetak |
| **Wali Kelas** | Monitoring perkembangan karakter kelas secara visual dan terukur |
| **Orang Tua** | Sertifikat karakter anak dengan framing positif, tanpa perbandingan antar-siswa |
| **Kepala Sekolah** | Agregat data karakter seluruh sekolah untuk pelaporan dinas |
| **BAPPERIDA** | Data berbasis bukti untuk kebijakan pendidikan karakter di tingkat kabupaten |
| **Juri KRENOVA** | Inovasi phygital yang terukur, ilmiah, dan berdampak sosial |

---

## 4.0 Ruang Lingkup (Scope)

### 4.1 In-Scope (MVP)

| Kode | Fitur | Deskripsi |
|------|-------|-----------|
| SC-01 | Decoupled Architecture | Frontend (React SPA) ↔ Backend (FastAPI REST+WS) ↔ PostgreSQL |
| SC-02 | Autentikasi JWT + RBAC | 3 role: Admin/Guru BK (full), Wali Kelas (class-scoped), Orang Tua (child-scoped) |
| SC-03 | QR Scanner Frontend | Decode QR kartu via webcam, fallback input manual |
| SC-04 | QR Code Generator | Generate & print QR untuk 40 kartu (PNG individual + halaman print-ready) |
| SC-05 | Game Session Management | Create, manage, complete sesi permainan |
| SC-06 | Scoring Engine (4 Dimensi CASEL) | Record skor per kartu (Berhasil=1, Gagal=0), agregasi per dimensi |
| SC-07 | WebSocket Live-Sync | Push score update ke Dashboard proyektor secara real-time |
| SC-08 | Dashboard Radar Chart Overlay | Individu (berwarna) vs rata-rata kelas (abu transparan) |
| SC-09 | Flag Intervensi Otomatis | Ikon ⚠️ jika skor dimensi < 80% rata-rata kelas |
| SC-10 | Time-Series Growth Tracker | Line chart perkembangan per dimensi per bulan |
| SC-11 | Narrative Insight | Insight otomatis berbasis simple heuristic logic |
| SC-12 | Focus/Presentation Mode | Full-screen tanpa navigasi untuk proyektor |
| SC-13 | PDF Export Akademik | Laporan siswa & ringkasan kelas bergaya akademik |
| SC-14 | Docker Compose Deployment | One-command deployment (`docker-compose up`) |

### 4.2 Out-of-Scope (Pengembangan Masa Depan)

| Kode | Fitur | Keterangan |
|------|-------|------------|
| OS-01 | Integrasi Dapodik | API integrasi data siswa nasional |
| OS-02 | OAuth2 SSO | Single Sign-On via Google/Microsoft |
| OS-03 | AI/ML Prediction | Model prediksi perilaku berbasis machine learning |
| OS-04 | Offline-First PWA | Mode offline penuh dengan service worker |
| OS-05 | Mobile Native App | Aplikasi Android/iOS dedicated |
| OS-06 | Dashboard Kepala Dinas | Agregat data seluruh kabupaten |

---

## 5.0 Stakeholder & Peran

| No. | Stakeholder | Peran dalam Proyek | Akses Sistem |
|-----|-------------|-------------------|--------------|
| 1 | **Azhar M** (Klien) | Pemilik proyek, pemberi keputusan final | — |
| 2 | **Guru Bimbingan Konseling (BK)** | Operator utama, pemindai QR, penilai siswa | Full Access |
| 3 | **Wali Kelas** | Pemantau perkembangan karakter kelas | Class-Scoped |
| 4 | **Orang Tua / Wali Murid** | Penerima laporan karakter anak | Child-Scoped (Read-Only) |
| 5 | **Kepala Sekolah** | Supervisi dan persetujuan kebijakan sekolah | School-Scoped (Read-Only) |
| 6 | **BAPPERIDA Kabupaten Kebumen** | Evaluator inovasi (KRENOVA), mitra strategis | Dashboard Agregat (Future) |
| 7 | **Dinas Pendidikan Kebumen** | Stakeholder kebijakan, dukungan implementasi | Dashboard Agregat (Future) |

---

## 6.0 Asumsi & Kendala

### 6.1 Asumsi

| Kode | Asumsi |
|------|--------|
| A-01 | Setiap sekolah yang berpartisipasi memiliki setidaknya 1 perangkat dengan kamera (laptop/tablet) dan akses internet |
| A-02 | Guru BK telah menerima pelatihan dasar pengoperasian sistem (1 sesi sosialisasi) |
| A-03 | Kartu permainan fisik telah dicetak beserta QR code masing-masing (disediakan oleh sistem via QR Generator) |
| A-04 | Evaluasi karakter dilakukan secara rutin setiap bulan untuk menghasilkan data *time-series* yang bermakna |
| A-05 | Infrastruktur Docker tersedia di server deployment (cloud VPS atau server lokal Dinas) |
| A-06 | Browser yang digunakan mendukung WebRTC dan modern JavaScript (Chrome, Edge, Firefox versi terbaru) |

### 6.2 Kendala

| Kode | Kendala | Dampak | Mitigasi |
|------|---------|--------|----------|
| K-01 | Koneksi internet tidak stabil di beberapa SD pedesaan | Data sesi mungkin tertunda | Graceful degradation + retry logic; konsep PWA *local caching* untuk fase selanjutnya |
| K-02 | Durasi pengembangan terbatas (target sebelum KRENOVA) | Fitur MVP harus diprioritaskan dengan ketat | Scope kontrol ketat, iterasi bertahap |
| K-03 | Variasi perangkat hardware guru (spesifikasi rendah) | Performa rendering chart mungkin lambat | Optimasi lazy loading, pagination, responsif |
| K-04 | Sensitivitas data karakter anak (regulasi perlindungan anak) | Potensi masalah etika dan hukum | Positive framing, RBAC ketat, enkripsi data |

---

## 7.0 Risiko Awal

| Kode | Risiko | Probabilitas | Dampak | Strategi Mitigasi |
|------|--------|:------------:|:------:|-------------------|
| R-01 | **Privasi & Keamanan Data Anak** — Kebocoran data karakter siswa yang bersifat sensitif | Sedang | Tinggi | Enkripsi password (bcrypt), JWT token expiry, RBAC enforcement, positive framing untuk menghindari labeling negatif |
| R-02 | **Akurasi QR Scanning** — Kondisi pencahayaan kelas yang buruk menyebabkan kegagalan pemindaian | Sedang | Sedang | Fallback input manual ID kartu, optimasi kontras QR code, panduan pencahayaan minimal |
| R-03 | **Adopsi Pengguna Rendah** — Guru BK enggan atau kesulitan mengadopsi teknologi baru | Sedang | Tinggi | UI/UX intuitif, pelatihan singkat (1 sesi), *onboarding wizard*, dokumentasi bantuan dalam Bahasa Indonesia |
| R-04 | **Skalabilitas Database** — Lonjakan data saat banyak sekolah menggunakan sistem secara bersamaan | Rendah | Sedang | PostgreSQL indexing, connection pooling (asyncpg), pagination, query optimization |
| R-05 | **Validitas Instrumen** — Pertanyaan terhadap keabsahan pemetaan 4 dimensi ke CASEL Framework | Rendah | Tinggi | Referensi dokumentasi CASEL resmi, konsultasi dengan praktisi BK, disclamer bahwa sistem bersifat *screening tool* bukan diagnosis klinis |
| R-06 | **Kestabilan WebSocket** — Koneksi terputus saat sesi permainan berlangsung (proyektor) | Sedang | Sedang | Auto-reconnect mechanism, fallback ke polling REST, indikator status koneksi di UI |
| R-07 | **Ketergantungan Docker** — Server deployment tidak mendukung Docker | Rendah | Sedang | Menyediakan panduan instalasi manual (non-Docker) sebagai alternatif |

---

## 8.0 Milestone Utama

| Fase | Milestone | Estimasi Durasi | Deliverable |
|------|-----------|:---------------:|-------------|
| **Fase 0** | Inisiasi & Perencanaan | 1 sesi | Project Charter, SRS (IEEE 830), Implementation Plan |
| **Fase 1** | Backend Core | 1–2 sesi | FastAPI + PostgreSQL + Auth + Scoring Engine + WebSocket |
| **Fase 2** | Frontend Core | 1–2 sesi | React SPA + Dashboard + Radar Chart + QR Scanner |
| **Fase 3** | Integrasi & Fitur Lanjutan | 1 sesi | Full-stack flow, PDF Export, QR Generator, Focus Mode |
| **Fase 4** | Testing & QA | 1 sesi | Unit test, browser test, bug fixing |
| **Fase 5** | Deployment & Dokumentasi | 1 sesi | Docker deploy, IEEE docs final, demo video, walkthrough |
| **Fase 6** | Presentasi KRENOVA | — | Demo live, poster, slide presentasi |

---

## 9.0 Persetujuan

Dengan menandatangani dokumen ini, pihak-pihak di bawah ini menyatakan persetujuan terhadap ruang lingkup, tujuan, dan rencana proyek **Zonara Character Analytics (Enterprise Edition)** sebagaimana tercantum dalam Project Charter ini.

| No. | Nama | Jabatan/Peran | Tanda Tangan | Tanggal |
|-----|------|---------------|:------------:|---------|
| 1 | Azhar M | Klien / Pemilik Proyek | ________________ | ____/____/2026 |
| 2 | ______________ | Pembimbing / Supervisor | ________________ | ____/____/2026 |
| 3 | ______________ | Guru BK (Perwakilan User) | ________________ | ____/____/2026 |

---

> **Catatan:** Dokumen ini bersifat *living document* dan dapat diperbarui sesuai kebutuhan proyek dengan persetujuan pihak terkait. Setiap perubahan akan dicatat dalam tabel Riwayat Revisi.
