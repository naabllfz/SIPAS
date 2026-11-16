import os
from models.dosen_model import DosenModel
from models.pengajuan_surat_model import PengajuanSuratModel


class DosenController:
    def __init__(self, id_dosen: int):
        self.id_dosen = id_dosen
        self.dosen_model = DosenModel()
        self.surat_model = PengajuanSuratModel()

    def get_profil_dosen(self):
        """Mengambil data profil dosen atau fallback default jika tidak ditemukan."""
        profil = None
        try:
            profil = self.dosen_model.berdasarkan_id(self.id_dosen)
        except Exception:
            profil = None

        if not profil:
            profil = {
                "id_dosen": self.id_dosen,
                "nidn": "198204122008121001",
                "nama_dosen": "Dr. Lukman Syafie, S.Kom., M.Kom.",
                "jabatan": "Dosen Wali",
                "email": "dosen@untad.ac.id",
                "file_ttd": None,
            }
        return profil

    def get_daftar_surat(self):
        """Mengambil seluruh daftar surat yang ditujukan kepada dosen ini."""
        return self.surat_model.untuk_dosen(self.id_dosen) or []

    def hitung_statistik(self, daftar_surat: list):
        """Menghitung total surat masuk, menunggu TTD, telah ditandatangani, dan ditolak."""
        total = len(daftar_surat)
        menunggu = sum(
            1 for s in daftar_surat
            if str(s.get("status") or "").lower() in ("diajukan", "diproses", "menunggu")
        )
        disetujui = sum(
            1 for s in daftar_surat
            if str(s.get("status") or "").lower() in ("disetujui", "selesai")
        )
        ditolak = sum(
            1 for s in daftar_surat
            if str(s.get("status") or "").lower() == "ditolak"
        )
        return {
            "total": total,
            "menunggu": menunggu,
            "disetujui": disetujui,
            "ditolak": ditolak,
        }

    def filter_surat(self, daftar_surat: list, keyword: str = "", status_filter: str = "Semua status"):
        """Memfilter daftar surat masuk berdasarkan kata kunci pencarian dan kategori status."""
        q = (keyword or "").strip().lower()
        hasil = []

        for row in daftar_surat or []:
            st = str(row.get("status") or "Diajukan").strip().lower()

            cocok_status = True
            if status_filter == "Menunggu Persetujuan":
                cocok_status = st in ("diajukan", "diproses", "menunggu")
            elif status_filter == "Telah Ditandatangani":
                cocok_status = st in ("disetujui", "selesai")
            elif status_filter == "Ditolak":
                cocok_status = st == "ditolak"

            nomor = str(row.get("nomor_pengajuan") or "").lower()
            nama = str(row.get("nama") or "").lower()
            nim = str(row.get("nim") or "").lower()
            jenis = str(row.get("jenis_surat") or row.get("nama_jenis") or "").lower()

            if cocok_status and (not q or q in nomor or q in nama or q in nim or q in jenis):
                hasil.append(row)

        return hasil

    def cek_specimen_ttd_siap(self, profil_dosen: dict):
        """Memeriksa apakah file gambar tanda tangan asli dosen sudah tersedia."""
        file_ttd = (profil_dosen or {}).get("file_ttd")
        return bool(file_ttd and os.path.exists(file_ttd))

    def unggah_specimen_ttd(self, file_path: str):
        """Menyimpan gambar specimen tanda tangan asli dosen ke storage & database."""
        if not file_path or not os.path.exists(file_path):
            return False, "File gambar tanda tangan tidak ditemukan."
        try:
            saved_path = self.dosen_model.simpan_file_ttd(self.id_dosen, file_path)
            return True, saved_path
        except Exception as err:
            return False, str(err)

    def setujui_dan_ttd(self, id_pengajuan: int, catatan_dosen: str):
        """Menyetujui pengajuan surat dan membuat tanda tangan digital SHA-256."""
        catatan = (catatan_dosen or "").strip() or "Disetujui dan ditandatangani oleh dosen pembimbing/wali."
        try:
            hasil = self.surat_model.approve_dosen(
                id_pengajuan=id_pengajuan,
                id_dosen=self.id_dosen,
                catatan_dosen=catatan,
            )
            return True, hasil
        except Exception as err:
            return False, str(err)

    def tolak_surat(self, id_pengajuan: int, alasan_penolakan: str):
        """Menolak pengajuan surat dengan catatan alasan penolakan."""
        alasan = (alasan_penolakan or "").strip()
        if not alasan:
            return False, "Alasan penolakan wajib diisi."
        try:
            self.surat_model.tolak_dosen(
                id_pengajuan=id_pengajuan,
                id_dosen=self.id_dosen,
                catatan_dosen=alasan,
            )
            return True, "Surat berhasil ditolak."
        except Exception as err:
            return False, str(err)

    @staticmethod
    def lengkapi_data_preview(surat: dict, profil_dosen: dict):
        """Melengkapi dictionary surat dengan identitas & file TTD dosen untuk pratinjau/PDF."""
        data = dict(surat or {})
        if profil_dosen:
            data["nama_dosen"] = data.get("nama_dosen") or profil_dosen.get("nama_dosen")
            data["nip_dosen"] = data.get("nip_dosen") or profil_dosen.get("nidn")
            data["jabatan_dosen"] = data.get("jabatan_dosen") or profil_dosen.get("jabatan")
            data["file_ttd_dosen"] = data.get("file_ttd_dosen") or profil_dosen.get("file_ttd")
        return data