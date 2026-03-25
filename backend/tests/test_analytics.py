"""
@module TestAnalytics
@desc Unit test untuk modul analitik (Radar Chart).
      1 happy path: radar data berhasil.
      1 error case: student not found.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

import pytest
from app.models.user import User
from app.models.school import School
from app.models.student import Student
from app.models.zone import Zone
from app.middleware.auth import hash_password, create_access_token


@pytest.mark.asyncio
async def test_radar_chart_success(client, db_session):
    """
    Test happy path: mendapatkan radar data untuk siswa yang valid
    mengembalikan skor per zona.
    """
    # Arrange: setup school, user, student, zones
    school = School(name="Test School", address="Test Address")
    db_session.add(school)
    await db_session.flush()

    teacher = User(
        username="teacher_test",
        password_hash=hash_password("password123"),
        full_name="Teacher Test",
        role="guru_bk",
        school_id=school.id,
    )
    db_session.add(teacher)
    await db_session.flush()

    student = Student(
        nis="12345", full_name="Siswa Test",
        class_name="5A", school_id=school.id,
    )
    db_session.add(student)

    # Tambahkan zona
    for code, name, hex_color in [
        ("blue", "Self-Awareness", "#3B82F6"),
        ("green", "Relationship Skills", "#22C55E"),
        ("yellow", "Self-Management", "#F59E0B"),
        ("red", "Social Awareness", "#EF4444"),
    ]:
        db_session.add(Zone(
            code=code, name=name, color_hex=hex_color,
            sel_dimension=name, description=f"Zona {name}",
        ))

    await db_session.commit()
    await db_session.refresh(teacher)
    await db_session.refresh(student)

    # Buat access token
    token = create_access_token({
        "sub": str(teacher.id),
        "role": teacher.role,
        "school_id": school.id,
    })

    # Act
    response = await client.get(
        f"/api/v1/analytics/radar/{student.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "radar_data" in data["data"]


@pytest.mark.asyncio
async def test_radar_chart_student_not_found(client, db_session):
    """
    Test error case: siswa tidak ditemukan mengembalikan 404.
    """
    # Arrange: buat user tanpa school
    school = School(name="Test School 2", address="Test")
    db_session.add(school)
    await db_session.flush()

    teacher = User(
        username="teacher_test_2",
        password_hash=hash_password("password123"),
        full_name="Teacher 2",
        role="guru_bk",
        school_id=school.id,
    )
    db_session.add(teacher)
    await db_session.commit()
    await db_session.refresh(teacher)

    token = create_access_token({
        "sub": str(teacher.id),
        "role": teacher.role,
        "school_id": school.id,
    })

    # Act: request radar untuk student ID yang tidak ada
    response = await client.get(
        "/api/v1/analytics/radar/9999",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Assert
    assert response.status_code == 404
