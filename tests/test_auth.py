from unittest.mock import MagicMock
from controllers.auth_controller import AuthController


def test_login_input_kosong():
    auth = AuthController()
    sukses, pesan = auth.proses_login("", "")
    assert sukses is False
    assert isinstance(pesan, str) and len(pesan) > 0


def test_login_mahasiswa_berhasil_mock():
    auth = AuthController()
    data_mhs = {
        "id_mahasiswa": 4,
        "nim": "F5212520061",
        "username": "nabil123",
        "nama": "Nabil Afzaal",
        "prodi": "Sistem Informasi",
        "email": "nabil@gmail.com",
    }

    auth.auth_model.login = MagicMock(return_value={
        "role": "mahasiswa",
        "user": data_mhs,
    })

    sukses, hasil = auth.proses_login("nabil123", "password123")
    assert sukses is True
    assert hasil["role"] == "mahasiswa"
    assert hasil["user"]["username"] == "nabil123"
    assert hasil["user"]["nim"] == "F5212520061"
    assert hasil["user"]["nama"] == "Nabil Afzaal"
    assert auth.current_role == "mahasiswa"


def test_logout_membersihkan_sesi():
    auth = AuthController()
    auth.current_user = {"id_admin": 1, "nama_admin": "Admin"}
    auth.current_role = "admin"

    auth.logout()
    assert auth.current_user is None
    assert auth.current_role is None