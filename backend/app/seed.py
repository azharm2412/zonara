"""
@module Seed
@desc Skrip penyemaian data awal (seeder) untuk tabel referensi dan demo.
      Membuat: 4 zona, 40 kartu (10 per zona), 1 sekolah demo, 1 admin, 1 guru, dan 5 siswa.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.1
"""

import asyncio
import logging
from sqlalchemy import select
from app.database import async_session_factory
from app.models import School, User, Zone, Card, Student
from app.middleware.auth import hash_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data Referensi Zona Karakter CASEL
# ---------------------------------------------------------------------------
ZONES_DATA = [
    {
        "code": "blue",
        "name": "Self-Awareness",
        "color_hex": "#3B82F6",
        "sel_dimension": "Kesadaran Diri",
        "description": "Kemampuan mengenali emosi, pikiran, dan nilai diri sendiri serta pengaruhnya terhadap perilaku.",
    },
    {
        "code": "green",
        "name": "Relationship Skills",
        "color_hex": "#22C55E",
        "sel_dimension": "Keterampilan Relasi",
        "description": "Kemampuan membangun dan memelihara hubungan sehat dengan individu dan kelompok yang beragam.",
    },
    {
        "code": "yellow",
        "name": "Self-Management",
        "color_hex": "#F59E0B",
        "sel_dimension": "Pengelolaan Diri",
        "description": "Kemampuan mengatur emosi, pikiran, dan perilaku secara efektif dalam berbagai situasi.",
    },
    {
        "code": "red",
        "name": "Social Awareness",
        "color_hex": "#EF4444",
        "sel_dimension": "Kesadaran Sosial",
        "description": "Kemampuan mengambil perspektif dan berempati dengan orang lain dari latar belakang yang beragam.",
    },
]

# ---------------------------------------------------------------------------
# Template Kartu Tantangan (10 per zona = 40 total)
# ---------------------------------------------------------------------------
CARDS_TEMPLATE = {
    "blue": [
        ("Cermin Emosi", "Ceritakan satu emosi yang kamu rasakan hari ini dan mengapa.", "easy"),
        ("Jurnal Hati", "Tuliskan tiga hal yang membuatmu bangga pada diri sendiri.", "easy"),
        ("Detektif Perasaan", "Identifikasi perasaan temanmu dari ekspresi wajahnya.", "normal"),
        ("Peta Kekuatan", "Sebutkan tiga kekuatan utama yang kamu miliki.", "easy"),
        ("Jendela Emosi", "Gambarkan wajah yang menunjukkan perasaanmu saat ini.", "easy"),
        ("Refleksi Hari Ini", "Apa pelajaran terpenting yang kamu dapat hari ini?", "normal"),
        ("Puzzle Diri", "Ceritakan tentang satu kebiasaan baikmu yang ingin kamu pertahankan.", "normal"),
        ("Bintang dalam Diri", "Apa mimpi terbesarmu dan langkah pertama untuk meraihnya?", "hard"),
        ("Kompas Moral", "Jelaskan mengapa kejujuran itu penting menurutmu.", "hard"),
        ("Suara Hati", "Ceritakan saat kamu merasa bangga karena melakukan hal yang benar.", "normal"),
    ],
    "green": [
        ("Jembatan Persahabatan", "Ajak satu teman baru untuk bermain bersama.", "easy"),
        ("Pesan Positif", "Tuliskan satu pujian tulus untuk teman di sebelahmu.", "easy"),
        ("Kerja Tim", "Selesaikan satu tugas bersama teman dengan pembagian tugas.", "normal"),
        ("Pendengar Aktif", "Dengarkan cerita temanmu tanpa menyela selama 2 menit.", "normal"),
        ("Duta Perdamaian", "Bantu dua teman yang sedang berselisih untuk berdamai.", "hard"),
        ("Surat Terima Kasih", "Tulis pesan terima kasih untuk guru atau orang tua.", "easy"),
        ("Lingkaran Cerita", "Ceritakan pengalaman menyenangkan bersama keluarga.", "easy"),
        ("Gotong Royong", "Bantu teman membersihkan area bermain.", "normal"),
        ("Mentor Kecil", "Ajarkan satu hal yang kamu kuasai kepada teman.", "hard"),
        ("Teman Setia", "Ceritakan saat kamu membantu teman yang kesulitan.", "normal"),
    ],
    "yellow": [
        ("Napas Tenang", "Lakukan teknik pernapasan dalam 5 kali saat merasa kesal.", "easy"),
        ("Sabar Menunggu", "Tunggu giliranmu tanpa protes selama permainan.", "easy"),
        ("Bos Emosi", "Ceritakan caramu mengendalikan marah tanpa menyakiti orang lain.", "normal"),
        ("Perencana Hebat", "Buat rencana sederhana untuk menyelesaikan PR tepat waktu.", "normal"),
        ("Fokus 5 Menit", "Kerjakan satu tugas tanpa terdistraksi selama 5 menit.", "easy"),
        ("Pantang Menyerah", "Ceritakan saat kamu tidak menyerah meskipun sulit.", "normal"),
        ("Pengatur Waktu", "Buat jadwal kegiatan dari bangun sampai tidur.", "hard"),
        ("Zen Master", "Duduk tenang dan fokus pada pernapasan selama 3 menit.", "easy"),
        ("Strategi Cerdas", "Pikirkan dua cara berbeda untuk menyelesaikan masalah.", "hard"),
        ("Kapten Diri", "Tentukan satu target kecil untuk minggu ini.", "normal"),
    ],
    "red": [
        ("Mata Empati", "Ceritakan bagaimana perasaan temanmu yang sedang sedih.", "easy"),
        ("Pemerhati Baik", "Perhatikan satu teman yang terlihat sendiri dan ajak bicara.", "easy"),
        ("Pahlawan Harian", "Lakukan satu kebaikan tanpa diminta untuk orang lain.", "normal"),
        ("Sudut Pandang", "Coba lihat masalah dari sisi temanmu, bukan sisimu.", "normal"),
        ("Penjaga Teman", "Lindungi teman yang sedang diolok-olok.", "hard"),
        ("Relawan Kecil", "Bantu guru membagikan buku atau alat tulis.", "easy"),
        ("Jembatan Budaya", "Ceritakan satu hal menarik tentang budaya teman.", "normal"),
        ("Pemimpin Adil", "Pastikan semua teman mendapat giliran yang sama.", "normal"),
        ("Advokat Mini", "Sampaikan pendapat temanmu yang tidak berani bicara.", "hard"),
        ("Hati Emas", "Sisihkan sebagian bekalmu untuk teman yang tidak bawa bekal.", "hard"),
    ],
}

# ---------------------------------------------------------------------------
# Data Demo Siswa (5 Siswa untuk Simulasi)
# ---------------------------------------------------------------------------
STUDENTS_DEMO_DATA = [
    {"full_name": "Budi Santoso", "nis": "10001", "class_name": "5A"},
    {"full_name": "Siti Aminah", "nis": "10002", "class_name": "5A"},
    {"full_name": "Rian Hidayat", "nis": "10003", "class_name": "5B"},
    {"full_name": "Lani Cahyani", "nis": "10004", "class_name": "5B"},
    {"full_name": "Dedi Kurniawan", "nis": "10005", "class_name": "6A"},
]


async def seed_database():
    """
    Menjalankan proses seeding data awal ke database.
    Idempoten — tidak akan menduplikasi data jika sudah ada.

    @raises Exception: Jika terjadi error database selama proses seeding.
    """
    
    async with async_session_factory() as session:
        try:
            # --- Seed Zones ---
            for zone_data in ZONES_DATA:
                existing = await session.execute(
                    select(Zone).where(Zone.code == zone_data["code"])
                )
                if existing.scalar_one_or_none() is None:
                    session.add(Zone(**zone_data))
                    logger.info("Zone '%s' seeded.", zone_data["code"])

            await session.commit()

            # --- Seed Cards (40 total) ---
            zones_result = await session.execute(select(Zone))
            zones = {z.code: z for z in zones_result.scalars().all()}

            for zone_code, cards_list in CARDS_TEMPLATE.items():
                zone = zones.get(zone_code)
                if zone is None:
                    continue

                for idx, (title, description, difficulty) in enumerate(cards_list, start=1):
                    prefix = zone_code[0].upper()
                    qr_code = f"ZCA-{prefix}-{idx:03d}"

                    existing = await session.execute(
                        select(Card).where(Card.qr_code == qr_code)
                    )
                    if existing.scalar_one_or_none() is None:
                        session.add(Card(
                            qr_code=qr_code,
                            zone_id=zone.id,
                            title=title,
                            description=description,
                            difficulty=difficulty,
                        ))

            await session.commit()
            logger.info("40 cards seeded across 4 zones.")

            # --- Seed Demo School ---
            existing_school = await session.execute(
                select(School).where(School.name == "SDN 1 Kebumen (Demo)")
            )
            school = existing_school.scalar_one_or_none()
            if school is None:
                school = School(
                    name="SDN 1 Kebumen (Demo)",
                    address="Jl. Pendidikan No. 1, Kebumen, Jawa Tengah",
                )
                session.add(school)
                await session.commit()
                await session.refresh(school)
                logger.info("Demo school seeded: '%s'", school.name)

            # --- Seed Admin User ---
            existing_admin = await session.execute(
                select(User).where(User.username == "admin_zonara")
            )
            if existing_admin.scalar_one_or_none() is None:
                admin = User(
                    username="admin_zonara",
                    password_hash=hash_password("admin123"),
                    full_name="Administrator Zonara",
                    role="admin",
                    school_id=school.id,
                )
                session.add(admin)
                await session.commit()
                logger.info("Admin user seeded: 'admin_zonara' (password: admin123)")

            # --- Seed Demo Guru BK ---
            existing_guru = await session.execute(
                select(User).where(User.username == "guru_demo")
            )
            if existing_guru.scalar_one_or_none() is None:
                guru = User(
                    username="guru_demo",
                    password_hash=hash_password("guru123"),
                    full_name="Guru BK Demo",
                    role="guru_bk",
                    school_id=school.id,
                )
                session.add(guru)
                await session.commit()
                logger.info("Demo guru BK seeded: 'guru_demo' (password: guru123)")

            # --- Seed Demo Students ---
            for student_data in STUDENTS_DEMO_DATA:
                existing_student = await session.execute(
                    select(Student).where(Student.nis == student_data["nis"])
                )
                if existing_student.scalar_one_or_none() is None:
                    session.add(Student(
                        **student_data,
                        school_id=school.id
                    ))
            await session.commit()
            logger.info("✅ 5 Demo students seeded.")

            logger.info("✅ Seeding complete!")

        except Exception as exc:
            await session.rollback()
            logger.error("❌ Seeding failed: %s", str(exc))
            raise


if __name__ == "__main__":
    asyncio.run(seed_database())