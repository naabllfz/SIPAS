from unittest.mock import MagicMock, patch
from controllers.auth_controller import AuthController


def test_login_input_kosong():
    auth = AuthController()
    sukses, pesan = auth.proses_login("", "")
    assert sukses is False
    assert isinstance(pesan, str) and len(pesan) > 0


@patch("controllers.auth_controller.MahasiswaModel.berdasarkan_id")
def test_login_mahasiswa_berhasil_mock(mock_berdasarkan_id):
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
    mock_berdasarkan_id.return_value = data_mhs

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


@patch("controllers.auth_controller.MahasiswaModel")
def test_registrasi_mahasiswa_berhasil_mock(mock_mhs_cls):
    mock_instance = MagicMock()
    mock_instance.berdasarkan_nim.return_value = None
    mock_instance.berdasarkan_username.return_value = None
    mock_instance.registrasi.return_value = 7
    mock_mhs_cls.return_value = mock_instance

    auth = AuthController()
    sukses, hasil = auth.proses_registrasi(
        nim="F5212520099",
        nama="Mahasiswa Baru",
        prodi="Sistem Informasi",
        username="mhsbaru99",
        password="password123",
        konfirmasi_password="password123",
        email="mhsbaru@gmail.com",
    )
    assert sukses is True
    assert hasil["id_mahasiswa"] == 7
    assert hasil["nim"] == "F5212520099"
    assert hasil["username"] == "mhsbaru99"
    mock_instance.registrasi.assert_called_once()


@patch("controllers.auth_controller.MahasiswaModel")
def test_registrasi_nim_sudah_terdaftar(mock_mhs_cls):
    mock_instance = MagicMock()
    mock_instance.berdasarkan_nim.return_value = {"id_mahasiswa": 4, "nim": "F5212520061"}
    mock_mhs_cls.return_value = mock_instance

    auth = AuthController()
    sukses, pesan = auth.proses_registrasi(
        nim="F5212520061",
        nama="Nabil Afzaal",
        prodi="Sistem Informasi",
        username="nabilbaru",
        password="password123",
        konfirmasi_password="password123",
    )
    assert sukses is False
    assert "sudah terdaftar" in pesan.lower()


def test_registrasi_password_tidak_cocok():
    auth = AuthController()
    sukses, pesan = auth.proses_registrasi(
        nim="F5212520099",
        nama="Mahasiswa Baru",
        prodi="Sistem Informasi",
        username="mhsbaru99",
        password="password123",
        konfirmasi_password="password456",
    )
    assert sukses is False
    assert "tidak cocok" in pesan.lower()