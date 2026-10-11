from config.database import Database


class MahasiswaModel:
    def semua(self):
        conn = Database.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id_mahasiswa, nim, nama, prodi, email
                FROM mahasiswa
                ORDER BY id_mahasiswa DESC
            """)
            return cursor.fetchall()
        finally:
            conn.close()

    def berdasarkan_id(self, id_mahasiswa):
        conn = Database.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id_mahasiswa, nim, nama, prodi, email
                FROM mahasiswa
                WHERE id_mahasiswa = %s
            """, (id_mahasiswa,))
            return cursor.fetchone()
        finally:
            conn.close()

    def berdasarkan_nim(self, nim):
        conn = Database.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id_mahasiswa, nim, nama, prodi, email
                FROM mahasiswa
                WHERE nim = %s
            """, (nim,))
            return cursor.fetchone()
        finally:
            conn.close()

    def tambah(self, nim, nama, prodi, email=None):
        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO mahasiswa (nim, nama, prodi, email)
                VALUES (%s, %s, %s, %s)
            """, (nim, nama, prodi, email))
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def perbarui(self, id_mahasiswa, nim, nama, prodi, email=None):
        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE mahasiswa
                SET nim = %s,
                    nama = %s,
                    prodi = %s,
                    email = %s
                WHERE id_mahasiswa = %s
            """, (nim, nama, prodi, email, id_mahasiswa))
            conn.commit()
            return cursor.rowcount
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def hapus(self, id_mahasiswa):
        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM mahasiswa WHERE id_mahasiswa = %s",
                (id_mahasiswa,)
            )
            conn.commit()
            return cursor.rowcount
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()