from models.auth_model import AuthModel
from models.mahasiswa_model import MahasiswaModel
from models.dosen_model import DosenModel


class AuthController:
    def __init__(self):
        self.auth_model = AuthModel()
        self.current_role = None
        self.current_user = None

    def proses_login(self, identifier: str, password: str):
        """
        Memvalidasi input dan memverifikasi akun ke database.
        Mengembalikan tuple: (sukses: bool, pesan_atau_hasil: str | dict)
        """
        ident = (identifier or "").strip()
        pwd = (password or "").strip()

        if not ident or not pwd:
            return False, "Username/NIM/NIDN dan kata sandi wajib diisi."

        try:
            hasil = self.auth_model.login(ident, pwd)
        except Exception as err:
            return False, f"Gagal terhubung ke database: {err}"

        if not hasil:
            return False, "Akun tidak ditemukan atau kata sandi salah."

        role = hasil["role"]
        user = hasil["user"]

        # Segarkan profil lengkap sesuai role
        if role == "mahasiswa":
            fresh = MahasiswaModel().berdasarkan_id(user["id_mahasiswa"])
            if fresh:
                user = fresh
        elif role == "dosen":
            fresh = DosenModel().berdasarkan_id(user["id_dosen"])
            if fresh:
                user = fresh

        self.current_role = role
        self.current_user = user
        return True, {"role": role, "user": user}

    def logout(self):
        self.current_role = None
        self.current_user = None