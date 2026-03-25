"""
@module TestAuth
@desc Unit test untuk modul autentikasi (login).
      1 happy path: login berhasil.
      1 error case: password salah.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

import pytest
from app.models.user import User
from app.middleware.auth import hash_password


@pytest.mark.asyncio
async def test_login_success(client, db_session):
    """
    Test happy path: login dengan kredensial yang valid mengembalikan
    access_token dan data user.
    """
    # Arrange: buat user test di database
    test_user = User(
        username="test_guru",
        password_hash=hash_password("password123"),
        full_name="Test Guru BK",
        role="guru_bk",
        school_id=None,
    )
    db_session.add(test_user)
    await db_session.commit()

    # Act: kirim request login
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "test_guru", "password": "password123"},
    )

    # Assert: validasi response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Login berhasil."
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    assert data["data"]["user"]["username"] == "test_guru"
    assert data["data"]["user"]["role"] == "guru_bk"


@pytest.mark.asyncio
async def test_login_wrong_password(client, db_session):
    """
    Test error case: login dengan password salah mengembalikan
    401 Unauthorized.
    """
    # Arrange: buat user test
    test_user = User(
        username="test_guru_2",
        password_hash=hash_password("correctpassword"),
        full_name="Test Guru 2",
        role="guru_bk",
        school_id=None,
    )
    db_session.add(test_user)
    await db_session.commit()

    # Act: kirim request login dengan password salah
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "test_guru_2", "password": "wrongpassword"},
    )

    # Assert: validasi error response
    assert response.status_code == 401
    data = response.json()
    assert "Password salah" in data["detail"]
