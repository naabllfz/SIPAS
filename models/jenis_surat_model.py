from config.database import Database


class JenisSuratModel:
    def semua(self):
        conn = Database.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id_jenis_surat, nama_jenis, deskripsi, aktif
                FROM jenis_surat
                ORDER BY id_jenis_surat
            """)
            return cursor.fetchall()
        finally:
            conn.close()

    def aktif_saja(self):
        conn = Database.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id_jenis_surat, nama_jenis, deskripsi, aktif
                FROM jenis_surat
                WHERE aktif = 1
                ORDER BY id_jenis_surat
            """)
            return cursor.fetchall()
        finally:
            conn.close()

    def berdasarkan_id(self, id_jenis_surat):
        conn = Database.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id_jenis_surat, nama_jenis, deskripsi, aktif
                FROM jenis_surat
                WHERE id_jenis_surat = %s
            """, (id_jenis_surat,))
            return cursor.fetchone()
        finally:
            conn.close()

    def tambah(self, nama_jenis, deskripsi=None, aktif=True):
        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO jenis_surat (nama_jenis, deskripsi, aktif)
                VALUES (%s, %s, %s)
            """, (nama_jenis, deskripsi, aktif))
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def perbarui(self, id_jenis_surat, nama_jenis, deskripsi=None, aktif=True):
        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE jenis_surat
                SET nama_jenis = %s,
                    deskripsi = %s,
                    aktif = %s
                WHERE id_jenis_surat = %s
            """, (nama_jenis, deskripsi, aktif, id_jenis_surat))
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
                (id_jenis_surat,)
            )
            conn.commit()
            return cursor.rowcount
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()