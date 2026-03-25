"""
@module ExportRouter
@desc Endpoint REST API untuk ekspor laporan PDF dan QR code.
      Mengacu pada API Spec §2.4 dan FR-005.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

import io
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.card import Card
from app.models.zone import Zone
from app.services.analytics_service import AnalyticsService
from app.middleware.auth import get_current_user, RoleChecker

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/report/{student_id}")
async def export_student_report(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Menghasilkan laporan PDF diagnosa karakter siswa.
    Mengacu pada API Spec §2.4.1.

    @param student_id: ID siswa target.
    @param db: AsyncSession database.
    @param current_user: User yang login.
    @return StreamingResponse: PDF binary stream.
    """
    try:
        # Validasi akses orang tua
        if current_user.role == "orang_tua":
            if current_user.child_student_id != student_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Anda hanya dapat mengunduh laporan anak Anda.",
                )

        # Ambil data siswa
        result = await db.execute(
            select(Student).where(
                Student.id == student_id,
                Student.school_id == current_user.school_id,
            )
        )
        student = result.scalar_one_or_none()
        if student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Siswa tidak ditemukan.",
            )

        # Ambil radar data
        radar_data = await AnalyticsService.get_radar_data(
            db, student_id, current_user.school_id
        )

        # Generate PDF menggunakan ReportLab
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Header
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width / 2, height - 50, "Laporan Diagnosa Karakter")
        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2, height - 70, "Zonara Character Analytics")

        # Data siswa
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 120, f"Nama: {student.full_name}")
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 145, f"NIS: {student.nis or 'N/A'}")
        c.drawString(50, height - 165, f"Kelas: {student.class_name}")

        # Skor per zona
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 210, "Profil Karakter (Skor Per Dimensi):")
        y_pos = height - 240
        c.setFont("Helvetica", 12)
        zone_labels = {
            "blue": "Self-Awareness (Biru)",
            "green": "Relationship Skills (Hijau)",
            "yellow": "Self-Management (Kuning)",
            "red": "Social Awareness (Merah)",
        }
        for code, label in zone_labels.items():
            score = radar_data.get(code, 0)
            c.drawString(70, y_pos, f"• {label}: {score}")
            y_pos -= 25

        # Footer
        c.setFont("Helvetica-Oblique", 9)
        c.drawCentredString(width / 2, 30, "Dokumen ini dihasilkan secara otomatis oleh Zonara Character Analytics.")

        c.showPage()
        c.save()
        buffer.seek(0)

        filename = f"Laporan_Karakter_{student.full_name.replace(' ', '_')}.pdf"
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Export report error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal menghasilkan laporan PDF.",
        )


@router.get(
    "/cards",
    dependencies=[Depends(RoleChecker(["admin", "guru_bk"]))],
)
async def export_qr_cards(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Menghasilkan PDF print-ready berisi grid QR code seluruh kartu.
    Mengacu pada API Spec §2.4.2 dan FR-005.5.

    @param db: AsyncSession database.
    @param current_user: Admin / Guru BK.
    @return StreamingResponse: PDF binary stream.
    """
    try:
        import qrcode
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader

        # Ambil semua kartu + zona
        result = await db.execute(
            select(Card, Zone).join(Zone, Card.zone_id == Zone.id).order_by(Zone.code, Card.id)
        )
        card_zones = result.all()

        if not card_zones:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tidak ada kartu ditemukan.",
            )

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Grid layout: 3 kolom x 5 baris per halaman
        cols, rows = 3, 5
        cell_w = (width - 80) / cols
        cell_h = (height - 100) / rows
        qr_size = min(cell_w, cell_h) - 40

        for idx, (card, zone) in enumerate(card_zones):
            page_idx = idx % (cols * rows)
            if page_idx == 0 and idx > 0:
                c.showPage()

            col = page_idx % cols
            row = page_idx // cols

            x = 40 + col * cell_w
            y = height - 60 - (row + 1) * cell_h

            # Generate QR code image
            qr = qrcode.make(card.qr_code)
            qr_buffer = io.BytesIO()
            qr.save(qr_buffer, format="PNG")
            qr_buffer.seek(0)

            # Draw QR
            c.drawImage(ImageReader(qr_buffer), x + 10, y + 30, width=qr_size, height=qr_size)

            # Draw label
            c.setFont("Helvetica-Bold", 7)
            c.drawString(x + 5, y + 18, card.qr_code)
            c.setFont("Helvetica", 6)
            c.drawString(x + 5, y + 8, f"{zone.name} ({zone.code})")

        c.showPage()
        c.save()
        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="Zonara_Printable_QRs.pdf"'},
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Export QR cards error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal menghasilkan PDF QR code.",
        )
