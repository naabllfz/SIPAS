import os
from models.mahasiswa_model import MahasiswaModel
from models.jenis_surat_model import JenisSuratModel
from models.dosen_model import DosenModel
from models.pengajuan_surat_model import PengajuanSuratModel


class MahasiswaController:
    MAX_LAMPIRAN_BYTES = 5 * 1024 * 1024  # 5 MB

    def __init__(self, id_mahasiswa: int):
        self.id_mahasiswa = id_mahasiswa
        self.mhs_model = MahasiswaModel()
        self.jenis_model = JenisSuratModel()
        self.dosen_model = DosenModel()
        self.surat_model = PengajuanSuratModel()

    def get_data_dashboard(self):
        """Mengambil profil mahasiswa, daftar surat miliknya, dan ringkasan hitungan status."""
        profil = self.mhs_model.berdasarkan_id(self.id_mahasiswa) or {}
        daftar_surat = self.surat_model.milik_mahasiswa(self.id_mahasiswa) or []

        status_counts = {}
        for row in daftar_surat:
            st = (row.get("status") or "Tanpa status").strip()
            status_counts[st] = status_counts.get(st, 0) + 1

        return {
            "profil": profil,
            "pengajuan": daftar_surat,
            "status_counts": status_counts,
        }

    def get_data_form_pengajuan(self):
        """Mengambil data master untuk dropdown form pengajuan dan riwayat surat mahasiswa."""
        return {
            "profil": self.mhs_model.berdasarkan_id(self.id_mahasiswa) or {},
            "jenis_surat": self.jenis_model.aktif_saja() or [],
            "dosen": self.dosen_model.semua() or [],
            "riwayat": self.surat_model.milik_mahasiswa(self.id_mahasiswa) or [],
        }

    def get_riwayat_saja(self):
        """Mengambil daftar riwayat pengajuan milik mahasiswa yang sedang login."""
        return self.surat_model.milik_mahasiswa(self.id_mahasiswa) or []

    def validasi_lampiran(self, file_path: str):
        """Memeriksa keberadaan file lampiran dan batas ukuran maksimal 5 MB."""
        if not file_path or not os.path.exists(file_path):
            return False, "File tidak ditemukan."

        ukuran_byte = os.path.getsize(file_path)
        if ukuran_byte > self.MAX_LAMPIRAN_BYTES:
            return False, "Ukuran file lampiran maksimal 5 MB."

        ukuran_kb = ukuran_byte / 1024
        teks_ukuran = (
            f"{ukuran_kb / 1024:.2f} MB"
            if ukuran_kb >= 1024
            else f"{ukuran_kb:.0f} KB"
        )
        return True, {
            "nama": os.path.basename(file_path),
            "ukuran": teks_ukuran,
        }

    def buat_pengajuan(self, id_jenis_surat: int, id_dosen: int, keperluan: str, path_lampiran: str = None):
        """Memvalidasi dan menyimpan pengajuan surat baru beserta lampirannya ke database."""
        ket = (keperluan or "").strip()
        if not id_jenis_surat:
            return False, "Jenis surat belum tersedia atau belum dipilih."
        if not ket:
            return False, "Keterangan / keperluan wajib diisi."

        try:
            id_baru = self.surat_model.tambah(
                id_mahasiswa=self.id_mahasiswa,
                id_jenis_surat=id_jenis_surat,
                id_dosen=id_dosen,
                keperluan=ket,
            )
            if path_lampiran:
                self.surat_model.simpan_lampiran(id_baru, path_lampiran)
            return True, id_baru
        except Exception as err:
            return False, f"Gagal menyimpan pengajuan: {err}"

    def filter_pengajuan(self, rows: list, keyword: str = "", filter_status: str = "Semua status"):
        """Memfilter daftar pengajuan berdasarkan kata kunci pencarian dan status."""
        q = (keyword or "").strip().lower()
        hasil = []

        for row in rows or []:
            nomor = str(row.get("nomor_pengajuan") or "")
            jenis = str(row.get("jenis_surat") or row.get("nama_jenis") or row.get("nama_jenis_surat") or "")
            nama = str(row.get("nama") or row.get("nama_mahasiswa") or "")
            dosen = str(row.get("nama_dosen") or "")
            status = str(row.get("status") or "")

            cocok_status = (filter_status == "Semua status") or (status == filter_status)
            cocok_cari = (
                not q
                or q in nomor.lower()
                or q in jenis.lower()
                or q in nama.lower()
                or q in dosen.lower()
            )

            if cocok_status and cocok_cari:
                hasil.append(row)

        return hasil