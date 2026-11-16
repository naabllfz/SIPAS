import os
import shutil
import hashlib
from datetime import datetime
from config.database import Database


class PengajuanSuratModel:
    def semua_dengan_relasi(self):
        """Daftar seluruh pengajuan beserta relasi lengkap (untuk Admin)."""
        conn = Database.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    p.id_pengajuan,
                    LPAD(p.id_pengajuan, 3, '0') AS nomor_pengajuan,
                    p.tanggal_pengajuan,
                    p.status,
                    p.catatan_dosen,
                    p.catatan_admin,
                    p.updated_at,
                    p.tanggal_verifikasi_admin,
                    p.tanggal_keputusan_dosen,
                    p.id_mahasiswa,
                    m.nim,
                    m.nama,
                    m.prodi,
                    m.email AS email_mahasiswa,
                    p.id_jenis_surat,
                    j.jenis_surat,
                    j.jenis_surat AS nama_jenis,
                    p.id_detail_surat,
                    ds.nama_surat,
                    ds.deskripsi AS keperluan,
                    p.id_admin,
                    a.nama_admin,
                    p.id_dosen,
                    d.nama_dosen,
                    d.nidn AS nip_dosen,
                    d.jabatan AS jabatan_dosen,
                    d.file_ttd AS file_ttd_dosen,
                    dok.hash_sha256 AS tanda_tangan_digital,
                    dok.waktu_tanda_tangan AS tanggal_disetujui,
                    dok.nama_file,
                    dok.path_file
                FROM pengajuan AS p
                JOIN mahasiswa AS m
                    ON m.id_mahasiswa = p.id_mahasiswa
                JOIN jenis_surat AS j
                    ON j.id_jenis_surat = p.id_jenis_surat
                LEFT JOIN detail_surat AS ds
                    ON ds.id_detail_surat = p.id_detail_surat
                LEFT JOIN admin AS a
                    ON a.id_admin = p.id_admin
                LEFT JOIN dosen AS d
                    ON d.id_dosen = p.id_dosen
                LEFT JOIN dokumen_surat AS dok
                    ON dok.id_pengajuan = p.id_pengajuan
                ORDER BY p.tanggal_pengajuan DESC, p.id_pengajuan DESC
            """)
            return cursor.fetchall()
        finally:
            conn.close()

    def untuk_dosen(self, id_dosen=None):
        """Daftar pengajuan surat yang masuk untuk ditinjau oleh dosen."""
        conn = Database.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            base_query = """
                SELECT
                    p.id_pengajuan,
                    LPAD(p.id_pengajuan, 3, '0') AS nomor_pengajuan,
                    p.tanggal_pengajuan,
                    p.status,
                    p.catatan_dosen,
                    p.catatan_admin,
                    p.updated_at,
                    p.tanggal_keputusan_dosen,
                    p.id_mahasiswa,
                    m.nim,
                    m.nama,
                    m.prodi,
                    m.email AS email_mahasiswa,
                    p.id_jenis_surat,
                    j.jenis_surat,
                    j.jenis_surat AS nama_jenis,
                    ds.nama_surat,
                    ds.deskripsi AS keperluan,
                    p.id_dosen,
                    d.nama_dosen,
                    d.nidn AS nip_dosen,
                    d.jabatan AS jabatan_dosen,
                    d.file_ttd AS file_ttd_dosen,
                    dok.hash_sha256 AS tanda_tangan_digital,
                    dok.waktu_tanda_tangan AS tanggal_disetujui,
                    dok.nama_file,
                    dok.path_file
                FROM pengajuan AS p
                JOIN mahasiswa AS m
                    ON m.id_mahasiswa = p.id_mahasiswa
                JOIN jenis_surat AS j
                    ON j.id_jenis_surat = p.id_jenis_surat
                LEFT JOIN detail_surat AS ds
                    ON ds.id_detail_surat = p.id_detail_surat
                LEFT JOIN dosen AS d
                    ON d.id_dosen = p.id_dosen
                LEFT JOIN dokumen_surat AS dok
                    ON dok.id_pengajuan = p.id_pengajuan
            """
            if id_dosen:
                cursor.execute(
                    base_query + " WHERE p.id_dosen = %s OR p.id_dosen IS NULL ORDER BY p.tanggal_pengajuan DESC, p.id_pengajuan DESC",
                    (id_dosen,)
                )
            else:
                cursor.execute(
                    base_query + " ORDER BY p.tanggal_pengajuan DESC, p.id_pengajuan DESC"
                )
            return cursor.fetchall()
        finally:
            conn.close()

    def milik_mahasiswa(self, id_mahasiswa):
        """Daftar pengajuan khusus milik mahasiswa yang sedang login."""
        conn = Database.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    p.*,
                    LPAD(p.id_pengajuan, 3, '0') AS nomor_pengajuan,
                    m.nim,
                    m.nama,
                    m.prodi,
                    m.email AS email_mahasiswa,
                    j.jenis_surat,
                    j.jenis_surat AS nama_jenis,
                    ds.nama_surat,
                    ds.deskripsi AS keperluan,
                    a.nama_admin,
                    d.nama_dosen,
                    d.nidn AS nip_dosen,
                    d.jabatan AS jabatan_dosen,
                    d.file_ttd AS file_ttd_dosen,
                    dok.hash_sha256 AS tanda_tangan_digital,
                    dok.waktu_tanda_tangan AS tanggal_disetujui,
                    dok.nama_file,
                    dok.path_file
                FROM pengajuan AS p
                JOIN mahasiswa AS m
                    ON m.id_mahasiswa = p.id_mahasiswa
                JOIN jenis_surat AS j
                    ON j.id_jenis_surat = p.id_jenis_surat
                LEFT JOIN detail_surat AS ds
                    ON ds.id_detail_surat = p.id_detail_surat
                LEFT JOIN admin AS a
                    ON a.id_admin = p.id_admin
                LEFT JOIN dosen AS d
                    ON d.id_dosen = p.id_dosen
                LEFT JOIN dokumen_surat AS dok
                    ON dok.id_pengajuan = p.id_pengajuan
                WHERE p.id_mahasiswa = %s
                ORDER BY p.tanggal_pengajuan DESC, p.id_pengajuan DESC
            """, (id_mahasiswa,))
            return cursor.fetchall()
        finally:
            conn.close()

    def tambah(self, id_mahasiswa, id_jenis_surat, id_dosen=None, keperluan=None, nama_surat=None):
        """Menyimpan detail keperluan ke detail_surat dan pengajuan baru ke tabel pengajuan."""
        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            id_detail_surat = None

            if keperluan:
                kode_unik = datetime.now().strftime("%Y%m%d%H%M%S%f")[:18]
                judul_detail = (nama_surat or f"Pengajuan-{id_mahasiswa}-{kode_unik}")[:80]
                deskripsi_detail = keperluan[:250]

                cursor.execute("""
                    INSERT INTO detail_surat (id_jenis_surat, nama_surat, deskripsi)
                    VALUES (%s, %s, %s)
                """, (id_jenis_surat, judul_detail, deskripsi_detail))
                id_detail_surat = cursor.lastrowid

            cursor.execute("""
                INSERT INTO pengajuan
                    (id_mahasiswa, id_jenis_surat, id_detail_surat, id_dosen)
                VALUES (%s, %s, %s, %s)
            """, (id_mahasiswa, id_jenis_surat, id_detail_surat, id_dosen))
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def simpan_lampiran(self, id_pengajuan, sumber_file_path):
        """Menyalin file lampiran ke folder storage/lampiran dan mencatatnya ke dokumen_surat."""
        folder_tujuan = os.path.join("storage", "lampiran")
        os.makedirs(folder_tujuan, exist_ok=True)

        ekstensi = os.path.splitext(sumber_file_path)[1]
        nama_file_baru = f"lampiran_pengajuan_{id_pengajuan:03d}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ekstensi}"
        path_tujuan = os.path.join(folder_tujuan, nama_file_baru)

        shutil.copy2(sumber_file_path, path_tujuan)

        sha256 = hashlib.sha256()
        with open(path_tujuan, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        file_hash = sha256.hexdigest()

        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO dokumen_surat
                    (id_pengajuan, nama_file, path_file, hash_sha256)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    nama_file = VALUES(nama_file),
                    path_file = VALUES(path_file),
                    hash_sha256 = VALUES(hash_sha256)
            """, (id_pengajuan, nama_file_baru, path_tujuan, file_hash))
            conn.commit()
            return path_tujuan
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def approve_dosen(self, id_pengajuan, id_dosen, catatan_dosen=None, nama_file=None, path_file=None):
        """Dosen menyetujui pengajuan dan mencatat pengesahan tanda tangan ke dokumen_surat."""
        conn = Database.get_connection()
        try:
            now = datetime.now()
            raw_payload = f"{id_pengajuan}_{id_dosen}_{now.strftime('%Y%m%d%H%M%S%f')}_SIPAS_SIGNATURE"
            hash_sha256 = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()

            if not catatan_dosen or not catatan_dosen.strip():
                catatan_dosen = "Disetujui dan ditandatangani oleh dosen pembimbing/wali."

            cursor = conn.cursor()
            cursor.execute("""
                UPDATE pengajuan
                SET status = 'Disetujui',
                    id_dosen = %s,
                    catatan_dosen = %s,
                    tanggal_keputusan_dosen = %s
                WHERE id_pengajuan = %s
            """, (id_dosen, catatan_dosen, now, id_pengajuan))

            file_name = nama_file or f"surat_pengajuan_{id_pengajuan:03d}.pdf"
            file_path = path_file or f"storage/surat/{file_name}"

            cursor.execute("""
                INSERT INTO dokumen_surat
                    (id_pengajuan, nama_file, path_file, hash_sha256, ditandatangani_oleh, waktu_tanda_tangan)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    hash_sha256 = VALUES(hash_sha256),
                    ditandatangani_oleh = VALUES(ditandatangani_oleh),
                    waktu_tanda_tangan = VALUES(waktu_tanda_tangan)
            """, (id_pengajuan, file_name, file_path, hash_sha256, id_dosen, now))

            conn.commit()
            return {
                "id_pengajuan": id_pengajuan,
                "status": "Disetujui",
                "tanda_tangan_digital": hash_sha256,
                "tanggal_disetujui": now,
                "catatan_dosen": catatan_dosen
            }
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def tolak_dosen(self, id_pengajuan, id_dosen, catatan_dosen):
        """Dosen menolak pengajuan surat dengan memberikan alasan/catatan."""
        conn = Database.get_connection()
        try:
            now = datetime.now()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE pengajuan
                SET status = 'Ditolak',
                    id_dosen = %s,
                    catatan_dosen = %s,
                    tanggal_keputusan_dosen = %s
                WHERE id_pengajuan = %s
            """, (id_dosen, catatan_dosen, now, id_pengajuan))
            conn.commit()
            return cursor.rowcount
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def ubah_status(self, id_pengajuan, status, id_admin=None, catatan_admin=None):
        conn = Database.get_connection()
        try:
            now = datetime.now()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE pengajuan
                SET status = %s,
                    id_admin = %s,
                    catatan_admin = %s,
                    tanggal_verifikasi_admin = %s
                WHERE id_pengajuan = %s
            """, (status, id_admin, catatan_admin, now, id_pengajuan))
            conn.commit()
            return cursor.rowcount
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()