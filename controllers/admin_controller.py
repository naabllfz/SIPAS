import os
from datetime import datetime

from models.pengajuan_surat_model import PengajuanSuratModel
from models.mahasiswa_model import MahasiswaModel
from models.jenis_surat_model import JenisSuratModel
from models.dosen_model import DosenModel


class AdminController:
    MAX_LAMPIRAN_BYTES = 5 * 1024 * 1024  # 5 MB

    def __init__(self, id_admin: int = 1):
        self.id_admin = id_admin
        self.surat_model = PengajuanSuratModel()
        self.mhs_model = MahasiswaModel()
        self.dosen_model = DosenModel()
        self.jenis_model = JenisSuratModel()

    @staticmethod
    def format_date(value):
        if value is None:
            return "-"
        if hasattr(value, "strftime"):
            return value.strftime("%d %b %Y")
        try:
            return datetime.strptime(str(value)[:19], "%Y-%m-%d %H:%M:%S").strftime("%d %b %Y")
        except Exception:
            return str(value)

    # =========================================================================
    # PENGAJUAN SURAT
    # =========================================================================
    def get_daftar_pengajuan(self):
        """Mengambil seluruh pengajuan surat beserta relasi dan format baris tabel."""
        records = self.surat_model.semua_dengan_relasi() or []
        formatted_rows = [
            (
                record.get("nomor_pengajuan", ""),
                record.get("nama", ""),
                record.get("jenis_surat") or record.get("nama_jenis", ""),
                self.format_date(record.get("tanggal_pengajuan")),
                record.get("status", ""),
                "✓ Disetujui" if record.get("status") in ("Disetujui", "Selesai") else "⏳ Menunggu",
                (record.get("tanda_tangan_digital") or "—")[:18]
                + ("..." if record.get("tanda_tangan_digital") else ""),
            )
            for record in records
        ]
        return records, formatted_rows

    def hitung_statistik_pengajuan(self, rows: list):
        """Menghitung statistik dashboard admin dari daftar pengajuan."""
        def count_by(*statuses):
            target = {s.lower() for s in statuses}
            return sum(1 for r in rows if str(r[4]).strip().lower() in target)

        return {
            "total": len(rows),
            "menunggu": count_by("Diproses", "Diajukan", "Menunggu"),
            "disetujui": count_by("Selesai", "Disetujui"),
            "ditolak": count_by("Ditolak"),
        }

    def filter_pengajuan(self, rows: list, keyword: str = "", filter_status: str = "Semua status"):
        """Memfilter baris pengajuan berdasarkan status dan kata kunci."""
        q = (keyword or "").strip().lower()
        hasil = []
        for row in rows or []:
            cocok_status = (filter_status == "Semua status") or (row[4] == filter_status)
            cocok_kata = (not q) or any(q in str(nilai).lower() for nilai in row[:4])
            if cocok_status and cocok_kata:
                hasil.append(row)
        return hasil

    def get_master_untuk_pengajuan(self):
        """Mengambil data master mahasiswa, jenis surat aktif, dan dosen untuk form input admin."""
        return {
            "mahasiswa": self.mhs_model.semua() or [],
            "jenis_surat": self.jenis_model.aktif_saja() or [],
            "dosen": self.dosen_model.semua() or [],
        }

    def validasi_lampiran(self, file_path: str):
        if not file_path or not os.path.exists(file_path):
            return False, "File tidak ditemukan."
        ukuran_byte = os.path.getsize(file_path)
        if ukuran_byte > self.MAX_LAMPIRAN_BYTES:
            return False, "Ukuran file lampiran maksimal 5 MB."
        ukuran_kb = ukuran_byte / 1024
        teks_ukuran = f"{ukuran_kb / 1024:.2f} MB" if ukuran_kb >= 1024 else f"{ukuran_kb:.0f} KB"
        return True, {"nama": os.path.basename(file_path), "ukuran": teks_ukuran}

    def tambah_pengajuan_admin(
        self,
        id_mahasiswa: int,
        id_jenis_surat: int,
        id_dosen: int,
        keperluan: str,
        path_lampiran: str = None,
    ):
        """Validasi dan simpan pengajuan surat baru yang diinput oleh Admin."""
        ket = (keperluan or "").strip()
        if not id_mahasiswa or not id_jenis_surat:
            return False, "Mahasiswa dan Jenis Surat wajib dipilih."
        if not ket:
            return False, "Keterangan / keperluan wajib diisi."

        try:
            id_baru = self.surat_model.tambah(
                id_mahasiswa=id_mahasiswa,
                id_jenis_surat=id_jenis_surat,
                id_dosen=id_dosen,
                keperluan=ket,
            )
            info_lampiran = "Tidak ada"
            if path_lampiran:
                self.surat_model.simpan_lampiran(id_baru, path_lampiran)
                info_lampiran = os.path.basename(path_lampiran)

            return True, {"id_pengajuan": id_baru, "info_lampiran": info_lampiran}
        except Exception as err:
            return False, str(err)

    def ubah_status_pengajuan(self, id_pengajuan: int, status_baru: str):
        """Memperbarui status pengajuan surat oleh Admin."""
        if not status_baru or status_baru == "Pilih status":
            return False, "Pilih status baru terlebih dahulu."
        try:
            self.surat_model.ubah_status(
                id_pengajuan=id_pengajuan,
                status=status_baru,
                id_admin=self.id_admin,
                catatan_admin=f"Status diperbarui oleh Admin menjadi {status_baru}.",
            )
            return True, f"Status berhasil diubah menjadi '{status_baru}'."
        except Exception as err:
            return False, str(err)

    # =========================================================================
    # CRUD MAHASISWA
    # =========================================================================
    def get_daftar_mahasiswa(self):
        records = self.mhs_model.semua() or []
        rows = [
            (
                r.get("id_mahasiswa"),
                r.get("nim", ""),
                r.get("nama", ""),
                r.get("prodi", ""),
                r.get("email", "") or "-",
            )
            for r in records
        ]
        return records, rows

    def simpan_mahasiswa(self, nim: str, nama: str, prodi: str, email: str = None, id_mahasiswa: int = None):
        nim_clean = (nim or "").strip()
        nama_clean = (nama or "").strip()
        prodi_clean = (prodi or "").strip()
        email_clean = (email or "").strip() or None

        if not nim_clean or not nama_clean or not prodi_clean:
            return False, "NIM, Nama, dan Program Studi wajib diisi."

        try:
            if id_mahasiswa is not None:
                self.mhs_model.perbarui(id_mahasiswa, nim_clean, nama_clean, prodi_clean, email_clean)
            else:
                self.mhs_model.tambah(nim_clean, nama_clean, prodi_clean, email_clean)
            return True, "Data mahasiswa berhasil disimpan."
        except Exception as err:
            return False, str(err)

    def hapus_mahasiswa(self, id_mahasiswa: int):
        try:
            self.mhs_model.hapus(id_mahasiswa)
            return True, "Data mahasiswa berhasil dihapus."
        except Exception as err:
            return False, f"Data tidak dapat dihapus (kemungkinan masih terhubung dengan pengajuan).\n\nDetail: {err}"

    # =========================================================================
    # CRUD DOSEN
    # =========================================================================
    def get_daftar_dosen(self):
        records = self.dosen_model.semua() or []
        rows = [
            (
                r.get("id_dosen"),
                r.get("nidn") or r.get("nip") or "-",
                r.get("nama_dosen", ""),
                r.get("jabatan", ""),
                r.get("email", "") or "-",
                "Aktif" if r.get("status", 1) == 1 else "Nonaktif",
            )
            for r in records
        ]
        return records, rows

    def simpan_dosen(self, nidn: str, nama_dosen: str, jabatan: str, email: str = None, id_dosen: int = None):
        nidn_clean = (nidn or "").strip()
        nama_clean = (nama_dosen or "").strip()
        email_clean = (email or "").strip() or None

        if not nidn_clean or not nama_clean:
            return False, "NIDN dan Nama Dosen wajib diisi."

        try:
            if id_dosen is not None:
                self.dosen_model.perbarui(id_dosen, nidn_clean, nama_clean, jabatan, email_clean)
            else:
                self.dosen_model.tambah(nidn=nidn_clean, nama_dosen=nama_clean, email=email_clean, jabatan=jabatan)
            return True, "Data dosen berhasil disimpan."
        except Exception as err:
            return False, str(err)

    def hapus_dosen(self, id_dosen: int):
        try:
            self.dosen_model.hapus(id_dosen)
            return True, "Data dosen berhasil dihapus."
        except Exception as err:
            return False, f"Data tidak dapat dihapus (kemungkinan masih terhubung dengan pengajuan).\n\nDetail: {err}"

    # =========================================================================
    # CRUD JENIS SURAT
    # =========================================================================
    def get_daftar_jenis_surat(self):
        records = self.jenis_model.semua() or []
        rows = [
            (
                r.get("id_jenis_surat"),
                r.get("jenis_surat") or r.get("nama_jenis", ""),
                "Aktif" if r.get("aktif", 1) == 1 else "Nonaktif",
            )
            for r in records
        ]
        return records, rows

    def perbarui_jenis_surat(self, id_jenis_surat: int, nama_jenis: str, aktif: int):
        nama_clean = (nama_jenis or "").strip()
        if not nama_clean:
            return False, "Nama jenis surat tidak boleh kosong."
        try:
            self.jenis_model.perbarui(id_jenis_surat, nama_clean, aktif)
            return True, "Jenis surat berhasil diperbarui."
        except Exception as err:
            return False, str(err)

    def hapus_jenis_surat(self, id_jenis_surat: int):
        try:
            self.jenis_model.hapus(id_jenis_surat)
            return True, "Jenis surat berhasil dihapus."
        except Exception as err:
            return False, f"Data tidak dapat dihapus (kemungkinan masih terhubung dengan pengajuan).\n\nDetail: {err}"