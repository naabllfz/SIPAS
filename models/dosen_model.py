import os
import shutil
import hashlib
from config.database import Database


class DosenModel:
    def semua(self):
        conn = Database.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id_dosen, username, nidn, nidn AS nip, nama_dosen, email, file_ttd, jabatan, status
                FROM dosen
                WHERE status = 1
                ORDER BY id_dosen ASC
            """)
            return cursor.fetchall()
        finally:
            conn.close()

    def berdasarkan_id(self, id_dosen):
        conn = Database.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id_dosen, username, nidn, nidn AS nip, nama_dosen, email, file_ttd, jabatan, status
                FROM dosen
                WHERE id_dosen = %s
            """, (id_dosen,))
            return cursor.fetchone()
        finally:
            conn.close()

    def tambah(self, nidn, nama_dosen, email=None, jabatan="Dosen Wali", username=None, password_default="dosen123"):
        conn = Database.get_connection()
        try:
            uname = username or nidn
            pwd_hash = hashlib.sha256(password_default.encode("utf-8")).hexdigest()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO dosen (username, password_hash, nama_dosen, nidn, jabatan, email, status)
                VALUES (%s, %s, %s, %s, %s, %s, 1)
            """, (uname, pwd_hash, nama_dosen, nidn, jabatan, email))
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def perbarui(self, id_dosen, nidn, nama_dosen, jabatan, email=None):
        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE dosen
                SET nidn = %s,
                    nama_dosen = %s,
                    jabatan = %s,
                    email = %s
                WHERE id_dosen = %s
            """, (nidn, nama_dosen, jabatan, email, id_dosen))
            conn.commit()
            return cursor.rowcount
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def simpan_file_ttd(self, id_dosen, sumber_file_path):
        """Menyalin gambar TTD asli dosen ke storage/ttd_dosen dan menyimpan path-nya ke DB."""
        folder_tujuan = os.path.join("storage", "ttd_dosen")
        os.makedirs(folder_tujuan, exist_ok=True)

        ekstensi = os.path.splitext(sumber_file_path)[1].lower()
        nama_file = f"ttd_dosen_{id_dosen}{ekstensi}"
        path_tujuan = os.path.join(folder_tujuan, nama_file)

        shutil.copy2(sumber_file_path, path_tujuan)

        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE dosen
                SET file_ttd = %s
                WHERE id_dosen = %s
            """, (path_tujuan, id_dosen))
            conn.commit()
            return path_tujuan
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def hapus(self, id_dosen):
        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM dosen WHERE id_dosen = %s", (id_dosen,))
            conn.commit()
            return cursor.rowcount
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()