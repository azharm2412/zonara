

# API SPECIFICATION (OPENAPI 3.0)
## Zonara Character Analytics (Enterprise Edition)

| Atribut | Keterangan |
|---------|-----------|
| **Nomor Dokumen** | ZCA-API-2026-001 |
| **Versi** | 1.0 |
| **Tanggal** | 25 Maret 2026 |
| **Klien** | Azhar M |
| **Standar** | REST API / OpenAPI 3.0 |
| **Dokumen Acuan** | ZCA-SAD-2026-001, ZCA-SRS-2026-001 |

---

## BAGIAN 1: INFORMASI UMUM & STRATEGI

### 1.1 Versioning Strategy
Seluruh *endpoint* REST API menggunakan prefiks `/api/v1/`. Strategi *versioning* pada level URI ini (*URI Versioning*) diimplementasikan untuk menjamin *backward compatibility*. Jika di masa depan terdapat perubahan *breaking changes* pada struktur *payload* atau logika bisnis, API versi lama (v1) akan tetap beroperasi secara independen dari versi baru (v2).

### 1.2 Mekanisme Autentikasi JWT
Sistem Zonara menggunakan *JSON Web Token* (JWT) secara *stateless* untuk autentikasi dan otorisasi.
* **Header:** Diwajibkan mengirimkan token pada setiap *request* yang dilindungi melalui HTTP Header: `Authorization: Bearer <access_token>`.
* **Payload JWT:** Token yang di-*issue* akan memuat *claims* berikut:
    * `sub`: Subject (ID pengguna).
    * `role`: Peran RBAC (`admin`, `guru_bk`, `wali_kelas`, `orang_tua`).
    * `school_id`: ID sekolah untuk isolasi data *multi-tenant*.
    * `exp`: Waktu kedaluwarsa token.
* **Kebijakan Expiry:** *Access token* memiliki masa berlaku 30 menit demi keamanan data anak, sedangkan *refresh token* berlaku selama 7 hari untuk kenyamanan UX tanpa mengorbankan sekuritas.

### 1.3 Rate Limiting Policy
Untuk mencegah serangan *Brute Force* dan *Denial of Service* (DoS), kebijakan pembatasan akses (*Rate Limiting*) diberlakukan di level *API Gateway/Middleware*:
* **Auth Endpoints (`/auth/*`):** Maksimal 5 *request* per menit per IP (mencegah *credential stuffing*).
* **General API Endpoints:** Maksimal 120 *request* per menit per IP atau per User ID.
* **Export Endpoints (`/export/*`):** Maksimal 10 *request* per menit (mencegah beban tinggi pada *PDF generator server*).

---

## BAGIAN 2: SPESIFIKASI ENDPOINT (DOKUMENTASI PER RESOURCE)

### 2.1 Autentikasi

#### 2.1.1 Issue JWT (Login)
* **Method:** `POST`
* **Endpoint:** `/api/v1/auth/login`
* **Auth:** None
* **Request Body:**
    ```json
    {
      "username": "guru_demo",
      "password": "securepassword123"
    }
    ```
* **Response 200 OK:**
    ```json
    {
      "status": "success",
      "data": {
        "access_token": "eyJhbG...",
        "refresh_token": "def456...",
        "user": {
          "id": 1,
          "username": "guru_demo",
          "role": "guru_bk",
          "school_id": 1
        }
      },
      "message": "Login berhasil."
    }
    ```
* **Response Error:** `400 Bad Request`, `401 Unauthorized` (Kredensial salah), `500 Internal Error`.
* **Contoh cURL:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/auth/login" \
         -H "Content-Type: application/json" \
         -d '{"username": "guru_demo", "password": "securepassword123"}'
    ```

#### 2.1.2 Logout (Revoke/Blacklist)
* **Method:** `POST`
* **Endpoint:** `/api/v1/auth/logout`
* **Auth:** Bearer Token
* **Request Body:** *None*
* **Response 200 OK:**
    ```json
    {
      "status": "success",
      "data": null,
      "message": "Token berhasil dicabut. Sesi diakhiri."
    }
    ```
* **Response Error:** `401 Unauthorized`, `500 Internal Error`.
* **Contoh cURL:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/auth/logout" \
         -H "Authorization: Bearer eyJhbG..."
    ```

#### 2.1.3 Refresh Token
* **Method:** `POST`
* **Endpoint:** `/api/v1/auth/refresh`
* **Auth:** Bearer Token (menggunakan Refresh Token)
* **Request Body:** *None*
* **Response 200 OK:**
    ```json
    {
      "status": "success",
      "data": {
        "access_token": "eyJhbG...new"
      },
      "message": "Access token berhasil diperbarui."
    }
    ```
* **Response Error:** `401 Unauthorized` (Refresh token invalid/expired).
* **Contoh cURL:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
         -H "Authorization: Bearer def456..."
    ```

---

### 2.2 Manajemen Sesi & Siswa (Domain Resource)

#### 2.2.1 Inisiasi Sesi Bermain Baru
* **Method:** `POST`
* **Endpoint:** `/api/v1/sessions`
* **Auth:** Bearer Token (Guru BK / Admin)
* **Request Body:**
    ```json
    {
      "class_name": "5A",
      "student_ids": [1, 2, 3]
    }
    ```
* **Response 200 OK:**
    ```json
    {
      "status": "success",
      "data": {
        "session_id": 12,
        "session_code": "ABC123",
        "status": "active"
      },
      "message": "Sesi permainan berhasil dibuat."
    }
    ```
* **Response Error:** `400 Bad Request`, `401 Unauthorized`, `403 Forbidden` (Wali Kelas/Orang tua), `422 Unprocessable`.
* **Contoh cURL:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/sessions" \
         -H "Authorization: Bearer eyJhbG..." \
         -H "Content-Type: application/json" \
         -d '{"class_name": "5A", "student_ids": [1, 2, 3]}'
    ```

#### 2.2.2 Fetch List Siswa Per Kelas
* **Method:** `GET`
* **Endpoint:** `/api/v1/students?class_name={class_name}`
* **Auth:** Bearer Token
* **Response 200 OK:**
    ```json
    {
      "status": "success",
      "data": {
        "students": [
          { "id": 1, "nis": "12345", "full_name": "Andi Pratama" },
          { "id": 2, "nis": "12346", "full_name": "Budi Santoso" }
        ]
      },
      "message": "Data siswa berhasil diambil."
    }
    ```
* **Response Error:** `401 Unauthorized`, `403 Forbidden` (Orang tua tidak berhak melihat *list*), `404 Not Found`.
* **Contoh cURL:**
    ```bash
    curl -X GET "http://localhost:8000/api/v1/students?class_name=5A" \
         -H "Authorization: Bearer eyJhbG..."
    ```

#### 2.2.3 Proses Scan & Input Skor Phygital
* **Method:** `POST`
* **Endpoint:** `/api/v1/scan`
* **Auth:** Bearer Token (Guru BK)
* **Request Body:**
    ```json
    {
      "session_id": 12,
      "student_id": 1,
      "qr_code": "ZCA-G-001",
      "result": 1
    }
    ```
* *(Catatan: Endpoint ini menggabungkan pemrosesan ID kartu dan pencatatan hasil penilaian 0/1)*
* **Response 200 OK:**
    ```json
    {
      "status": "success",
      "data": {
        "score_id": 150,
        "zone_id": 2,
        "zone_name": "Relationship Skills"
      },
      "message": "Skor berhasil dicatat dan di-broadcast ke dashboard."
    }
    ```
* **Response Error:** `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found` (QR tidak valid), `422 Unprocessable`.
* **Contoh cURL:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/scan" \
         -H "Authorization: Bearer eyJhbG..." \
         -H "Content-Type: application/json" \
         -d '{"session_id": 12, "student_id": 1, "qr_code": "ZCA-G-001", "result": 1}'
    ```

---

### 2.3 Analitik & Diagnostik

#### 2.3.1 Mengambil Koordinat Radar Chart Siswa
* **Method:** `GET`
* **Endpoint:** `/api/v1/analytics/radar/{student_id}`
* **Auth:** Bearer Token
* **Response 200 OK:**
    ```json
    {
      "status": "success",
      "data": {
        "student_id": 1,
        "radar_data": {
          "blue": 3,
          "green": 2,
          "yellow": 3,
          "red": 1
        }
      },
      "message": "Data radar chart individu berhasil di-generate."
    }
    ```
* **Response Error:** `401 Unauthorized`, `403 Forbidden` (Jika orang tua mengakses ID anak lain), `404 Not Found`.
* **Contoh cURL:**
    ```bash
    curl -X GET "http://localhost:8000/api/v1/analytics/radar/1" \
         -H "Authorization: Bearer eyJhbG..."
    ```

#### 2.3.2 Perbandingan Data Individu vs Rata-rata Kelas (Class Summary)
* **Method:** `GET`
* **Endpoint:** `/api/v1/analytics/class-summary?class_name={class_name}`
* **Auth:** Bearer Token (Admin / Guru BK / Wali Kelas)
* **Response 200 OK:**
    ```json
    {
      "status": "success",
      "data": {
        "class_average": {
          "blue": 2.67,
          "green": 2.67,
          "yellow": 2.67,
          "red": 2.0
        },
        "flagged_students": [
          {
            "student_id": 1,
            "name": "Andi Pratama",
            "flags": ["red"]
          }
        ]
      },
      "message": "Summary kelas beserta flag intervensi berhasil diambil."
    }
    ```
* **Response Error:** `401 Unauthorized`, `403 Forbidden` (Orang Tua dilarang mengakses), `404 Not Found`.
* **Contoh cURL:**
    ```bash
    curl -X GET "http://localhost:8000/api/v1/analytics/class-summary?class_name=5A" \
         -H "Authorization: Bearer eyJhbG..."
    ```

---

### 2.4 Laporan & Export

#### 2.4.1 Download PDF Hasil Diagnosa Karakter
* **Method:** `GET`
* **Endpoint:** `/api/v1/export/report/{student_id}`
* **Auth:** Bearer Token
* **Response 200 OK:**
    * *Headers:* `Content-Type: application/pdf`, `Content-Disposition: attachment; filename="Laporan_Karakter_Andi.pdf"`
    * *Body:* *Binary PDF Stream*
* **Response Error:** `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `500 Internal Error`.
* **Contoh cURL:**
    ```bash
    curl -X GET "http://localhost:8000/api/v1/export/report/1" \
         -H "Authorization: Bearer eyJhbG..." \
         -o Laporan_Karakter_1.pdf
    ```

#### 2.4.2 Generate PDF Kumpulan QR Code Kartu
* **Method:** `GET`
* **Endpoint:** `/api/v1/export/cards`
* **Auth:** Bearer Token (Hanya Guru BK / Admin)
* **Response 200 OK:**
    * *Headers:* `Content-Type: application/pdf`, `Content-Disposition: attachment; filename="Zonara_Printable_QRs.pdf"`
    * *Body:* *Binary PDF Stream (Grid Print-Ready)*
* **Response Error:** `401 Unauthorized`, `403 Forbidden` (Akses ditolak selain Admin/Guru), `500 Internal Error`.
* **Contoh cURL:**
    ```bash
    curl -X GET "http://localhost:8000/api/v1/export/cards" \
         -H "Authorization: Bearer eyJhbG..." \
         -o Zonara_QRs.pdf
    ```

---

## BAGIAN 3: REAL-TIME COMMUNICATION (WEBSOCKET)

### 3.1 Endpoint & Protokol
* **Protocol:** `ws://` atau `wss://` (Production)
* **Endpoint URL:** `/ws/analytics/{session_id}`
* **Fungsi:** Mengirimkan (*push*) pembaruan data secara langsung (*real-time*) ke dashboard proyektor (Focus Mode) setiap kali guru melakukan input hasil pemindaian di aplikasi mobile.

### 3.2 Kontrak Data Payload (Server to Client)
Setiap kali ada pembaruan skor di database, *backend* (FastAPI) akan mem-*broadcast* pesan JSON berikut ke seluruh klien yang mendengarkan di `session_id` tersebut:

```json
{
  "event": "score_update",
  "timestamp": "2026-03-25T10:15:30Z",
  "data": {
    "student_id": 1,
    "radar_data": {
      "blue": 4,
      "green": 2,
      "yellow": 3,
      "red": 1
    },
    "class_average": {
      "blue": 2.8,
      "green": 2.6,
      "yellow": 2.6,
      "red": 2.0
    },
    "flags": ["red"]
  }
}
```
*Detail Kontrak Data:*
* `event`: Identifikasi jenis pembaruan.
* `radar_data`: Agregasi terbaru skor siswa per dimensi (digunakan React Recharts untuk merender transisi yang halus).
* `flags`: Daftar zona di mana skor siswa < 80% dari `class_average`. Memicu munculnya *alert* merah secara otomatis.

