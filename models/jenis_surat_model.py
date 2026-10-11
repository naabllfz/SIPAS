from config.database import Database


class JenisSuratModel:
    def semua(self):
        conn = Database.get_connection()

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id_jenis_surat, nama_jenis_surat, deskripsi
                FROM jenis_surat
                ORDER BY id_jenis_surat
            """)
            return cursor.fetchall()
        finally:
            conn.close()

    def berdasarkan_id(self, id_jenis_surat):
        conn = Database.get_connection()

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT id_jenis_surat, nama_jenis_surat, deskripsi
                FROM jenis_surat
                WHERE id_jenis_surat = %s
                """,
                (id_jenis_surat,),
            )
            return cursor.fetchone()
        finally:
            conn.close()

    def tambah(self, nama_jenis_surat, deskripsi=None):
        conn = Database.get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO jenis_surat (nama_jenis_surat, deskripsi)
                VALUES (%s, %s)
                """,
                (nama_jenis_surat, deskripsi),
            )
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def perbarui(self, id_jenis_surat, nama_jenis_surat, deskripsi=None):
        conn = Database.get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE jenis_surat
                SET nama_jenis_surat = %s, deskripsi = %s
                WHERE id_jenis_surat = %s
                """,
                (nama_jenis_surat, deskripsi, id_jenis_surat),
            )
            conn.commit()
            return cursor.rowcount
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def hapus(self, id_jenis_surat):
        conn = Database.get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM jenis_surat WHERE id_jenis_surat = %s",
                (id_jenis_surat,),
            )
            conn.commit()
            return cursor.rowcount
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()