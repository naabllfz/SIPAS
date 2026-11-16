import re
from models.auth_model import AuthModel
from models.mahasiswa_model import MahasiswaModel


class AuthController:
    def __init__(self):
        self.auth_model = AuthModel()
        self.current_user = None
        self.current_role = None

    def proses_login(self, identifier: str, password: str):
        if not identifier or not identifier.strip() or not password or not password.strip():
            return False, "Username/NIM/NIDN dan kata sandi wajib diisi."

        hasil = self.auth_model.login(identifier.strip(), password.strip())
        if not hasil:
            return False, "Akun tidak ditemukan atau kata sandi salah."

        role = hasil["role"]
        user = hasil["user"]

        if role == "mahasiswa" and user.get("id_mahasiswa"):
            fresh = MahasiswaModel().berdasarkan_id(user["id_mahasiswa"])
            if fresh:
                user = fresh

        self.current_role = role
        self.current_user = user
        return True, {"role": role, "user": user}

    def proses_registrasi(
        self,
        nim: str,
        nama: str,
        prodi: str,
        username: str,
        password: str,
        konfirmasi_password: str,
        email: str = "",
    ):
        nim_clean = (nim or "").strip().upper()
        nama_clean = (nama or "").strip()
        prodi_clean = (prodi or "").strip()
        username_clean = (username or "").strip()
        pwd_clean = (password or "").strip()
        konf_clean = (konfirmasi_password or "").strip()
        email_clean = (email or "").strip() or None

        if not nim_clean or not nama_clean or not prodi_clean or not username_clean or not pwd_clean:
            return False, "NIM, Nama Lengkap, Program Studi, Username, dan Kata Sandi wajib diisi."

        if len(nim_clean) < 6 or not nim_clean.isalnum():
            return False, "Format NIM tidak valid (contoh: F5212520061)."

        if len(username_clean) < 4 or " " in username_clean:
            return False, "Username minimal 4 karakter dan tidak boleh mengandung spasi."

        if len(pwd_clean) < 6:
            return False, "Kata sandi minimal 6 karakter."

        if pwd_clean != konf_clean:
            return False, "Konfirmasi kata sandi tidak cocok."

        if email_clean and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email_clean):
            return False, "Format email tidak valid."

        mhs_model = MahasiswaModel()
        if mhs_model.berdasarkan_nim(nim_clean):
            return False, f"NIM '{nim_clean}' sudah terdaftar."

        if mhs_model.berdasarkan_username(username_clean):
            return False, f"Username '{username_clean}' sudah digunakan."

        try:
            id_baru = mhs_model.registrasi(
                nim=nim_clean,
                username=username_clean,
                password=pwd_clean,
                nama=nama_clean,
                prodi=prodi_clean,
                email=email_clean,
            )
            return True, {
                "id_mahasiswa": id_baru,
                "nim": nim_clean,
                "username": username_clean,
                "nama": nama_clean,
                "prodi": prodi_clean,
                "email": email_clean,
            }
        except Exception as e:
            return False, f"Gagal menyimpan registrasi: {e}"

    def logout(self):
        self.current_user = None
        self.current_role = None