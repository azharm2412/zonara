"""
@module StudentsRouter
@desc Endpoint REST API untuk manajemen data siswa (CRUD).
      Mengacu pada API Spec §2.2.2 dan FR-002.3.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse
from app.middleware.auth import get_current_user, RoleChecker

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("")
async def list_students(
    class_name: str = Query(None, description="Filter berdasarkan kelas"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mengambil daftar siswa per kelas milik sekolah pengguna.
    Mengacu pada API Spec §2.2.2.

    @param class_name: Filter kelas (opsional).
    @param db: AsyncSession database.
    @param current_user: User yang login.
    @return dict: Daftar siswa.
    """
    try:
        query = select(Student).where(Student.school_id == current_user.school_id)

        if class_name:
            query = query.where(Student.class_name == class_name)

        # Orang tua hanya bisa melihat anak sendiri
        if current_user.role == "orang_tua":
            if current_user.child_student_id:
                query = query.where(Student.id == current_user.child_student_id)
            else:
                return {
                    "status": "success",
                    "data": {"students": []},
                    "message": "Belum ada data anak terhubung.",
                }

        result = await db.execute(query.order_by(Student.full_name))
        students = result.scalars().all()

        return {
            "status": "success",
            "data": {
                "students": [
                    {"id": s.id, "nis": s.nis, "full_name": s.full_name, "class_name": s.class_name}
                    for s in students
                ]
            },
            "message": "Data siswa berhasil diambil.",
        }

    except Exception as exc:
        logger.error("List students error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mengambil data siswa.",
        )


@router.post(
    "",
    response_model=dict,
    dependencies=[Depends(RoleChecker(["admin", "guru_bk"]))],
)
async def create_student(
    request: StudentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mendaftarkan siswa baru. Hanya Admin dan Guru BK.
    Mengacu pada FR-002.3.

    @param request: StudentCreate dengan data siswa.
    @param db: AsyncSession database.
    @param current_user: User pembuat.
    @return dict: Data siswa yang baru dibuat.
    """
    try:
        # Cek duplikasi NIS jika diisi
        if request.nis:
            existing = await db.execute(
                select(Student).where(Student.nis == request.nis)
            )
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"NIS '{request.nis}' sudah terdaftar.",
                )

        new_student = Student(
            nis=request.nis,
            full_name=request.full_name,
            class_name=request.class_name,
            school_id=current_user.school_id,
        )
        db.add(new_student)
        await db.commit()
        await db.refresh(new_student)

        logger.info("Student '%s' created by %s", request.full_name, current_user.username)

        return {
            "status": "success",
            "data": StudentResponse.model_validate(new_student).model_dump(),
            "message": "Siswa berhasil didaftarkan.",
        }

    except HTTPException:
        raise
    except Exception as exc:
        await db.rollback()
        logger.error("Create student error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mendaftarkan siswa.",
        )


@router.put(
    "/{student_id}",
    response_model=dict,
    dependencies=[Depends(RoleChecker(["admin", "guru_bk"]))],
)
async def update_student(
    student_id: int,
    request: StudentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Memperbarui data siswa. Hanya Admin dan Guru BK.

    @param student_id: ID siswa.
    @param request: StudentUpdate dengan field opsional.
    @param db: AsyncSession database.
    @param current_user: User yang mengubah.
    @return dict: Data siswa yang diperbarui.
    """
    try:
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

        # Update field yang dikirim
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(student, field, value)

        await db.commit()
        await db.refresh(student)

        return {
            "status": "success",
            "data": StudentResponse.model_validate(student).model_dump(),
            "message": "Data siswa berhasil diperbarui.",
        }

    except HTTPException:
        raise
    except Exception as exc:
        await db.rollback()
        logger.error("Update student error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal memperbarui data siswa.",
        )


@router.delete(
    "/{student_id}",
    dependencies=[Depends(RoleChecker(["admin"]))],
)
async def delete_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Menghapus data siswa. Hanya Admin.

    @param student_id: ID siswa.
    @param db: AsyncSession database.
    @param current_user: Admin user.
    @return dict: Konfirmasi penghapusan.
    """
    try:
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

        await db.delete(student)
        await db.commit()

        logger.info("Student ID %d deleted by %s", student_id, current_user.username)

        return {
            "status": "success",
            "data": None,
            "message": "Siswa berhasil dihapus.",
        }

    except HTTPException:
        raise
    except Exception as exc:
        await db.rollback()
        logger.error("Delete student error: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal menghapus siswa.",
        )
