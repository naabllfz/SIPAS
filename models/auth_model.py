import hashlib
from config.database import Database


class AuthModel:
    @staticmethod
    def _hash_sha256(plain_password: str) -> str:
        return hashlib.sha256(plain_password.encode("utf-8")).hexdigest()

    def login(self, identifier: str, password: str):
        """
        Memeriksa kredensial pada tabel admin, dosen, dan mahasiswa.
        Mengembalikan dict: {"role": str, "user": dict} jika cocok, atau None jika gagal.
        """
        ident = identifier.strip()
        pwd = password.strip()
        pwd_hashed = self._hash_sha256(pwd)

        conn = Database.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)

            # 1. Cek Tabel Admin (kolom password plain)
            cursor.execute(
                """
                SELECT id_admin, username, nama_admin
                FROM admin
                WHERE username = %s AND password = %s
                LIMIT 1
                """,
                (ident, pwd),
            )
            admin = cursor.fetchone()
            if admin:
                return {"role": "admin", "user": admin}

            # 2. Cek Tabel Dosen (username atau nidn, password_hash SHA-256, status aktif)
            cursor.execute(
                """
                SELECT id_dosen, username, nama_dosen, nidn, jabatan, email, file_ttd, status
                FROM dosen
                WHERE (username = %s OR nidn = %s)
                  AND password_hash = %s
                  AND status = 1
                LIMIT 1
                """,
                (ident, ident, pwd_hashed),
            )
            dosen = cursor.fetchone()
            if dosen:
                return {"role": "dosen", "user": dosen}

            # 3. Cek Tabel Mahasiswa (username atau nim, password_hash SHA-256)
            cursor.execute(
                """
                SELECT id_mahasiswa, nim, username, nama, prodi, email
                FROM mahasiswa
                WHERE (username = %s OR nim = %s)
                  AND password_hash = %s
                LIMIT 1
                """,
                (ident, ident, pwd_hashed),
            )
            mahasiswa = cursor.fetchone()
            if mahasiswa:
                return {"role": "mahasiswa", "user": mahasiswa}

            return None
        finally:
            conn.close()