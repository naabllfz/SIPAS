from config.database import Database


class PengajuanSuratModel:
    def semua_dengan_relasi(self):
        """Daftar pengajuan beserta mahasiswa, jenis surat, dan admin."""
        conn = Database.get_connection()

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    p.id_pengajuan,
                    p.nomor_pengajuan,
                    p.tanggal_pengajuan,
                    p.status,
                    p.id_mahasiswa,
                    m.nim,
                    m.nama_mahasiswa,
                    p.id_jenis_surat,
                    j.nama_jenis_surat,
                    p.id_admin,
                    a.nama_admin,
                    p.updated_at
                FROM pengajuan_surat AS p
                JOIN mahasiswa AS m
                    ON m.id_mahasiswa = p.id_mahasiswa
                JOIN jenis_surat AS j
                    ON j.id_jenis_surat = p.id_jenis_surat
                LEFT JOIN admin AS a
                    ON a.id_admin = p.id_admin
                ORDER BY p.tanggal_pengajuan DESC
            """)
            return cursor.fetchall()
        finally:
            conn.close()

    def berdasarkan_nomor(self, nomor_pengajuan):
        conn = Database.get_connection()

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT
                    p.*,
                    m.nim,
                    m.nama_mahasiswa,
                    j.nama_jenis_surat,
                    a.nama_admin
                FROM pengajuan_surat AS p
                JOIN mahasiswa AS m
                    ON m.id_mahasiswa = p.id_mahasiswa
                JOIN jenis_surat AS j
                    ON j.id_jenis_surat = p.id_jenis_surat
                LEFT JOIN admin AS a
                    ON a.id_admin = p.id_admin
                WHERE p.nomor_pengajuan = %s
                """,
                (nomor_pengajuan,),
            )
            return cursor.fetchone()
        finally:
            conn.close()

    def milik_mahasiswa(self, id_mahasiswa):
        conn = Database.get_connection()

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT
                    p.*,
                    j.nama_jenis_surat,
                    a.nama_admin
                FROM pengajuan_surat AS p
                JOIN jenis_surat AS j
                    ON j.id_jenis_surat = p.id_jenis_surat
                LEFT JOIN admin AS a
                    ON a.id_admin = p.id_admin
                WHERE p.id_mahasiswa = %s
                ORDER BY p.tanggal_pengajuan DESC
                """,
                (id_mahasiswa,),
            )
            return cursor.fetchall()
        finally:
            conn.close()

    def tambah(
        self, nomor_pengajuan, id_mahasiswa,
        id_jenis_surat, status="Menunggu"
    ):
        conn = Database.get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO pengajuan_surat
                    (nomor_pengajuan, tanggal_pengajuan, status,
                     id_mahasiswa, id_jenis_surat)
                VALUES (%s, CURDATE(), %s, %s, %s)
                """,
                (nomor_pengajuan, status, id_mahasiswa, id_jenis_surat),
            )
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def ubah_status(self, id_pengajuan, status, id_admin):
        conn = Database.get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE pengajuan_surat
                SET status = %s, id_admin = %s
                WHERE id_pengajuan = %s
                """,
                (status, id_admin, id_pengajuan),
            )
            conn.commit()
            return cursor.rowcount
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def hapus(self, id_pengajuan):
        conn = Database.get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM pengajuan_surat WHERE id_pengajuan = %s",
                (id_pengajuan,),
            )
            conn.commit()
            return cursor.rowcount
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()