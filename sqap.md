# SOFTWARE QUALITY ASSURANCE PLAN (SQAP)
## Zonara Character Analytics (Enterprise Edition)
### Mengacu pada Standar IEEE 730-2014

| Atribut | Keterangan |
|---------|-----------|
| **Nomor Dokumen** | ZCA-SQAP-2026-001 |
| **Versi** | 1.0 |
| **Tanggal** | 25 Maret 2026 |
| **Arsitektur** | Decoupled (React.js + FastAPI + PostgreSQL) |
| **Status** | Final (Disetujui untuk Implementasi) |

---

## 1.0 TUJUAN & RUANG LINGKUP SQA
Tujuan dari *Software Quality Assurance Plan* (SQAP) ini adalah mendefinisikan standar, proses, dan metrik yang akan digunakan untuk mengevaluasi kualitas perangkat lunak secara objektif pada sistem **Zonara Character Analytics (Enterprise Edition)**. Ruang lingkup SQAP ini mencakup seluruh siklus hidup pengembangan sistem (*Software Development Life Cycle*), mulai dari tinjauan spesifikasi kebutuhan (SRS), perancangan arsitektur, implementasi kode (Frontend & Backend), hingga pengujian *User Acceptance Testing* (UAT) sebelum tahap peluncuran akhir.

## 2.0 MANAJEMEN SQA

### 2.1 Organisasi & Tanggung Jawab
Manajemen jaminan mutu harus dikelola secara independen namun tetap terintegrasi dengan siklus pengembangan. Pembagian tugas ditetapkan sebagai berikut:

| Peran | Penanggung Jawab | Deskripsi Tanggung Jawab |
|-------|-----------------|--------------------------|
| **QA Manager / Tech Lead** | Azhar Maulana | Menetapkan standar metrik (SQAP), menyetujui *Pull Request* (PR), dan memberikan *sign-off* pada *Quality Gates* utama. |
| **QA Engineer / Co-Developer** | Diayu Nur Aini | Melakukan *code review* silang (*peer review*), merancang skrip *automated testing*, dan menjalankan validasi UAT. |
| **Project Sponsor** | Dosen Pembimbing | Memberikan validasi akademik dan persetujuan akhir kelayakan rilis. |

### 2.2 Quality Gates dalam SDLC
Proses pengembangan dipagari oleh 5 titik pemeriksaan (*Quality Gates*) yang tidak boleh dilewati tanpa persetujuan formal:
* **Gate 1: Requirements Review** (Sebelum Desain): Validasi kelengkapan, konsistensi, dan ambiguitas dokumen SRS (IEEE 830) serta spesifikasi *Use Case*.
* **Gate 2: Design Review** (Sebelum Coding): Validasi arsitektur SAD (IEEE 1016), skema database (3NF), dan spesifikasi API (OpenAPI 3.0) terhadap NFR performa dan keamanan.
* **Gate 3: Code Review + Unit Test** (Tiap Modul Selesai): Evaluasi metrik *Cyclomatic Complexity*, kepatuhan standar linting, dan *passing rate* *Unit Test* lokal.
* **Gate 4: Integration Test** (Sebelum UAT): Validasi komunikasi data asinkron (*WebSockets*) dan alur *end-to-end* via lingkungan *Staging* (*Docker Compose*).
* **Gate 5: UAT Sign-off** (Sebelum Go-Live): Validasi kesesuaian fungsionalitas dengan *user journey* Guru BK, Wali Kelas, dan Orang Tua di lingkungan produksi simulasi.

---

## 3.0 DOKUMENTASI SQA
Audit kualitas memerlukan *baseline* dokumentasi yang tertelusur (*traceable*):

| Kode | Nama Dokumen | Dibuat Oleh | Direview Oleh | Jadwal |
|:---:|--------------|-------------|---------------|--------|
| ZCA-SRS-001 | *Software Requirements Specification* | Azhar Maulana | Diayu Nur Aini | Gate 1 |
| ZCA-SAD-001 | *Software Architecture Document* | Azhar Maulana | Diayu Nur Aini | Gate 2 |
| ZCA-API-001 | *OpenAPI 3.0 Specification* | Azhar Maulana | Diayu Nur Aini | Gate 2 |
| ZCA-MTP-001 | *Master Test Plan* | Azhar Maulana | Dosen Pembimbing | Gate 2 |
| ZCA-TRR-001 | *Test Readiness & Result Report* | Diayu Nur Aini | Azhar Maulana | Gate 4 |

---

## 4.0 STANDAR, PRAKTIK & KONVENSI
Untuk menjaga *maintainability* dari sistem berskala *Enterprise*, batas toleransi teknis berikut wajib dipatuhi secara ketat:
* **Naming Convention:** `snake_case` untuk Python/PostgreSQL dan `camelCase`/`PascalCase` untuk JavaScript/React.
* **Cyclomatic Complexity:** Maksimal skor 10 per fungsi. Fungsi dengan cabang logika lebih dari 10 harus di-refaktor (*Extract Method*).
* **Function Length:** Maksimal 50 baris per fungsi/metode.
* **Code Coverage:** Minimal 80% *line coverage* pada area *Business Logic Layer* (Backend Services).

**Tools Wajib Jaminan Mutu:**

| Kategori | Tool (Backend / Frontend) | Tujuan |
|----------|---------------------------|--------|
| **Unit Testing** | Pytest / Jest | Memvalidasi fungsi skoring dan komponen UI secara terisolasi. |
| **API Testing** | httpx (FastAPI) / Supertest | Menguji kontrak respons *endpoint* REST. |
| **Coverage** | pytest-cov / Istanbul | Menghasilkan laporan metrik *Code Coverage* (Target ≥ 80%). |
| **Linting** | flake8 / ESLint | Menjaga konsistensi gaya penulisan kode (PEP8 standar). |
| **Static Anal.**| mypy / SonarLint | Mendeteksi potensi celah keamanan statik dan inkonsistensi tipe data (*Type Hinting*). |

---

## 5.0 TINJAUAN & AUDIT
* **Peer Code Review:** Diwajibkan sebelum kode di-*merge* ke *branch main*. *Reviewer* akan fokus memeriksa penanganan eksepsi dan optimasi *query* (pencegahan *N+1 query*).
* **Architectural Audit:** Audit periodik pada performa *WebSocket connection pool* untuk memastikan sistem tidak mengalami *memory leak* selama sesi *Phygital* yang panjang.

---

## 6.0 MANAJEMEN DEFECT
Semua temuan *bug* wajib dicatat dan dikelola melalui siklus hidup berikut:
* **Siklus:** `New` $\rightarrow$ `Assigned` (Penugasan) $\rightarrow$ `In Progress` (Perbaikan) $\rightarrow$ `Fixed` (Selesai di *local*) $\rightarrow$ `Verified` (Lulus *re-test* di *staging*) $\rightarrow$ `Closed`.

**Klasifikasi Severity:**
1. **Critical:** Sistem lumpuh (contoh: *Crash* pada *WebSocket*, kebocoran data JWT).
2. **High:** Fitur krusial gagal tanpa *workaround* (contoh: QR gagal di-*decode*, skor tidak tersimpan).
3. **Medium:** Fitur sekunder terganggu (contoh: Ekspor PDF gagal, *Radar Chart* tidak merender animasi).
4. **Low:** Masalah kosmetik UI/UX, *typo*.
5. **Enhancement:** Permintaan fitur baru atau optimasi kode (*non-bug*).

---

## 7.0 RISIKO KUALITAS
Lima mitigasi utama untuk memastikan produk dapat lolos demonstrasi teknis KRENOVA tanpa cela:
1. **Kegagalan Decode QR Frontend:** Risiko keterlambatan *library* `html5-qrcode` dalam kondisi pencahayaan kelas yang minim.
2. **Latensi WebSocket Tinggi:** Risiko penundaan sinkronisasi animasi *Radar Chart* (melebihi batas 500ms) akibat kebuntuan jaringan *client*.
3. **Inkonsistensi State Redux:** Risiko balapan data (*Race Condition*) antara panggilan REST API dan *push update* WebSocket secara bersamaan di *dashboard* React.
4. **Akurasi Algoritma Heuristik:** Risiko *Narrative Insight* mengeluarkan teks teguran/negatif (*labeling*) akibat anomali kalkulasi deviasi skor.
5. **JWT Token Expiry Handling:** Risiko hilangnya data sesi permainan akibat *Access Token* yang kedaluwarsa secara tiba-tiba tanpa mekanisme *silent refresh* via *Refresh Token*.

---

## 8.0 METRIK YANG DIUKUR
Sistem dinyatakan layak rilis ke tahap produksi apabila memenuhi ambang batas metrik kuantitatif berikut:
* **Code Coverage (%):** Target $\geq 80\%$.
* **Defect Density:** Maksimal 0.5 *bug* per 1000 Baris Kode (KLOC) untuk kategori *High/Critical*.
* **Defect Removal Efficiency (DRE) (%):** Target $\geq 95\%$. Mengukur persentase *bug* yang berhasil ditangkap selama *testing* dibandingkan dengan yang lolos ke produksi.
* **Mean Time To Repair (MTTR):** Maksimal 4 jam perbaikan untuk cacat tingkat *Critical*.
* **Test Pass Rate (%):** $100\%$ lulus untuk *Critical Path Test Cases* (Login, QR Scan, WebSocket Sync) pada *Test Plan*.

***

