from unittest.mock import MagicMock
from controllers.mahasiswa_controller import MahasiswaController
from controllers.dosen_controller import DosenController
from controllers.admin_controller import AdminController
from models.pengajuan_surat_model import PengajuanSuratModel


def test_buat_pengajuan_validasi_kosong():
    ctrl = MahasiswaController(id_mahasiswa=4)
    sukses, pesan = ctrl.buat_pengajuan(
        id_jenis_surat=2,
        id_dosen=4,
        keperluan="   ",
    )
    assert sukses is False
    assert "wajib diisi" in pesan.lower()


def test_buat_pengajuan_berhasil_mock():
    ctrl = MahasiswaController(id_mahasiswa=4)
    ctrl.surat_model.tambah = MagicMock(return_value=14)

    sukses, id_baru = ctrl.buat_pengajuan(
        id_jenis_surat=2,
        id_dosen=4,
        keperluan="Permohonan surat keterangan aktif kuliah",
    )
    assert sukses is True
    assert id_baru == 14
    ctrl.surat_model.tambah.assert_called_once()


def test_hitung_statistik_dosen_sesuai_db():
    ctrl = DosenController(id_dosen=1)
    # Simulasi baris sesuai tabel `pengajuan` (Disetujui, Selesai, Ditolak, Diproses)
    dummy_pengajuan = [
        {"id_pengajuan": 5, "id_mahasiswa": 1, "id_detail_surat": 1, "status": "Disetujui"},
        {"id_pengajuan": 6, "id_mahasiswa": 2, "id_detail_surat": 3, "status": "Disetujui"},
        {"id_pengajuan": 8, "id_mahasiswa": 4, "id_detail_surat": 7, "status": "Selesai"},
        {"id_pengajuan": 10, "id_mahasiswa": 6, "id_detail_surat": 8, "status": "Ditolak"},
        {"id_pengajuan": 14, "id_mahasiswa": 3, "id_detail_surat": 11, "status": "Diproses"},
    ]
    stats = ctrl.hitung_statistik(dummy_pengajuan)
    assert stats["total"] == 5
    assert stats["menunggu"] == 1
    assert stats["disetujui"] == 3
    assert stats["ditolak"] == 1


def test_approve_dosen_menghasilkan_hash_sha256():
    model = PengajuanSuratModel()
    model.conn = MagicMock()
    mock_cursor = MagicMock()
    model.conn.cursor.return_value = mock_cursor

    hasil = model.approve_dosen(
        id_pengajuan=13,
        id_dosen=1,
        catatan_dosen="Disetujui dan ditandatangani oleh dosen kepala jurusan",
    )
    assert "tanda_tangan_digital" in hasil
    assert len(hasil["tanda_tangan_digital"]) == 64


def test_tolak_dosen_memanggil_model():
    ctrl = DosenController(id_dosen=2)
    ctrl.surat_model.tolak_dosen = MagicMock()

    sukses, pesan = ctrl.tolak_surat(
        id_pengajuan=7,
        alasan_penolakan="Proposal belum layak diseminarkan, revisi dari pembimbing belum selesai.",
    )
    assert sukses is True
    assert "ditolak" in pesan.lower()
    ctrl.surat_model.tolak_dosen.assert_called_once()


def test_admin_ubah_status_selesai():
    ctrl = AdminController(id_admin=1)
    ctrl.surat_model.ubah_status = MagicMock()

    sukses, pesan = ctrl.ubah_status_pengajuan(id_pengajuan=8, status_baru="Selesai")
    assert sukses is True
    assert "Selesai" in pesan
    ctrl.surat_model.ubah_status.assert_called_once()