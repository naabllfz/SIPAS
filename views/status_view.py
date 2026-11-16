import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from controllers.mahasiswa_controller import MahasiswaController
from views.surat_preview_dialog import SuratPreviewDialog
from views.theme import (
    BG, WHITE, NAVY, BLUE, MUTED, LINE,
    PALE_BLUE, PALE_AMBER, PALE_GREEN,
    page_heading, panel, primary_button
)


class StatusView(tk.Frame):
    def __init__(self, master, id_mahasiswa=1, on_navigate=None):
        super().__init__(master, bg=BG)

        self.id_mahasiswa = id_mahasiswa
        self.on_navigate = on_navigate
        self.controller = MahasiswaController(self.id_mahasiswa)

        self.rows = []
        self.error_message = None
        self.selected_row_data = None

        page_heading(
            self,
            "Riwayat layanan",
            "Status pengajuan surat",
            "Pantau status persetujuan dan tanda tangan dosen secara langsung dari database."
        )

        search = panel(self, 15, 13)
        search.pack(fill="x", pady=(0, 16))

        tk.Label(
            search,
            text="⌕",
            bg=WHITE,
            fg=BLUE,
            font=("Segoe UI", 17, "bold")
        ).pack(side="left", padx=(0, 9))

        self.hint = "Cari nomor, nama jenis, atau dosen pembimbing"
        self.nomor = tk.Entry(
            search,
            font=("Segoe UI", 10),
            relief="flat",
            bd=0,
            fg="#818B80",
            insertbackground=NAVY
        )
        self.nomor.insert(0, self.hint)
        self.nomor.pack(side="left", fill="x", expand=True, ipady=8)
        self.nomor.bind("<FocusIn>", self.clear_hint)
        self.nomor.bind("<FocusOut>", self.restore_hint)
        self.nomor.bind("<Return>", self.cari)

        primary_button(
            search, "Cari pengajuan", self.cari
        ).pack(side="right")

        card = panel(self, 19, 17)
        card.pack(fill="both", expand=True)

        header = tk.Frame(card, bg=WHITE)
        header.pack(fill="x", pady=(0, 13))

        title_area = tk.Frame(header, bg=WHITE)
        title_area.pack(side="left")

        tk.Label(
            title_area,
            text="Daftar permohonan saya",
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")

        self.info_label = tk.Label(
            title_area,
            text="Memuat data pengajuan...",
            bg=WHITE,
            fg=MUTED,
            font=("Segoe UI", 8)
        )
        self.info_label.pack(anchor="w", pady=(3, 0))

        self.filter_var = tk.StringVar(value="Semua status")
        self.filter_status = ttk.Combobox(
            header,
            textvariable=self.filter_var,
            state="readonly",
            width=20,
            values=["Semua status"]
        )
        self.filter_status.pack(side="right")
        self.filter_status.bind(
            "<<ComboboxSelected>>",
            lambda _event: self.tampilkan_hasil()
        )

        columns = ("nomor", "tanggal", "jenis", "status_umum", "status_dosen", "ttd_digital")
        self.table = ttk.Treeview(
            card,
            columns=columns,
            show="headings",
            height=7
        )

        headings = {
            "nomor": "NO. PENGAJUAN",
            "tanggal": "TANGGAL",
            "jenis": "JENIS SURAT",
            "status_umum": "STATUS",
            "status_dosen": "VERIFIKASI DOSEN",
            "ttd_digital": "TTD DIGITAL"
        }

        col_widths = {
            "nomor": 110,
            "tanggal": 120,
            "jenis": 260,
            "status_umum": 110,
            "status_dosen": 140,
            "ttd_digital": 170
        }

        for col in columns:
            self.table.heading(col, text=headings[col])
            self.table.column(
                col,
                width=col_widths.get(col, 130),
                anchor="w"
            )

        self.table.pack(fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self.pilih_baris)

        # Panel Detail & Tombol Lihat Pratinjau Surat
        self.detail = tk.Frame(self, bg=PALE_BLUE, padx=18, pady=14, highlightbackground=LINE, highlightthickness=1)
        self.detail.pack(fill="x", pady=(14, 0))

        d_header = tk.Frame(self.detail, bg=PALE_BLUE)
        d_header.pack(fill="x")

        self.detail_title = tk.Label(
            d_header,
            text="INFORMASI STATUS & PENGESAHAN DOKUMEN",
            bg=PALE_BLUE,
            fg=BLUE,
            font=("Segoe UI", 9, "bold")
        )
        self.detail_title.pack(side="left")

        # Tombol Pratinjau Surat Resmi di sisi kanan
        self.btn_preview = primary_button(
            d_header,
            "👁 Buka Pratinjau Surat & Unduh PDF",
            self.buka_pratinjau_surat,
            padx=14,
            pady=6
        )
        self.btn_preview.pack(side="right")

        self.detail_text = tk.Label(
            self.detail,
            text="Pilih salah satu pengajuan pada tabel di atas untuk melihat detail verifikasi dan tanda tangan dosen.",
            bg=PALE_BLUE,
            fg="#596D5E",
            font=("Segoe UI", 9),
            justify="left",
            wraplength=950
        )
        self.detail_text.pack(anchor="w", pady=(6, 0))

        self.muat_data()

    def muat_data(self):
        try:
            self.rows = self.controller.get_riwayat_saja()
            self.error_message = None

            status_tersedia = sorted({
                str(row.get("status") or "").strip()
                for row in self.rows
                if str(row.get("status") or "").strip()
            })

            self.filter_status.configure(
                values=["Semua status"] + status_tersedia
            )
            self.info_label.configure(
                text=f"{len(self.rows)} pengajuan milik Anda"
            )
            self.tampilkan_hasil()

        except Exception as error:
            self.rows = []
            self.error_message = str(error)
            self.info_label.configure(
                text="Data pengajuan gagal dimuat."
            )
            self.tabel_pesan(
                "Gagal memuat data",
                "Periksa koneksi database dan nama tabel/kolom. "
                f"Detail: {error}"
            )

    def _get_query_aktif(self):
        query = self.nomor.get().strip()
        return "" if query.lower() == self.hint.lower() else query

    def tampilkan_hasil(self):
        hasil = self.controller.filter_pengajuan(
            self.rows,
            keyword=self._get_query_aktif(),
            filter_status=self.filter_var.get()
        )

        self.table.delete(*self.table.get_children())

        for index, row in enumerate(hasil):
            nomor = row.get("nomor_pengajuan") or "-"
            jenis = row.get("jenis_surat") or row.get("nama_jenis") or row.get("nama_jenis_surat") or "-"
            tanggal = self.format_date(row.get("tanggal_pengajuan"))
            status = str(row.get("status") or "Diajukan")

            st_lower = status.lower()
            if st_lower in ("disetujui", "selesai"):
                dosen_label = "✓ Disetujui Dosen"
            elif st_lower == "ditolak":
                dosen_label = "✕ Ditolak Dosen"
            else:
                dosen_label = "⏳ Menunggu TTD"

            ttd_raw = row.get("tanda_tangan_digital")
            if ttd_raw and st_lower in ("disetujui", "selesai"):
                ttd = f"{ttd_raw[:16]}..."
            else:
                ttd = "—"

            self.table.insert(
                "",
                "end",
                iid=str(index),
                values=(nomor, tanggal, jenis, status, dosen_label, ttd)
            )

        if not hasil:
            pesan = (
                "Tidak ada pengajuan yang cocok dengan pencarian/filter."
                if self.rows
                else "Anda belum memiliki pengajuan surat."
            )
            self.table.insert(
                "",
                "end",
                iid="kosong",
                values=(pesan, "-", "-", "-", "-", "-")
            )

    def tabel_pesan(self, nomor, pesan):
        self.table.delete(*self.table.get_children())
        self.table.insert(
            "",
            "end",
            values=(nomor, "-", "-", "-", "-", "-")
        )
        self.detail_title.configure(text="DATA TIDAK TERSEDIA")
        self.detail_text.configure(text=pesan)

    def clear_hint(self, _event=None):
        if self.nomor.get() == self.hint:
            self.nomor.delete(0, "end")
            self.nomor.configure(fg=NAVY)

    def restore_hint(self, _event=None):
        if not self.nomor.get().strip():
            self.nomor.insert(0, self.hint)
            self.nomor.configure(fg="#818B80")
            self.tampilkan_hasil()

    def cari(self, _event=None):
        self.tampilkan_hasil()

    def pilih_baris(self, _event=None):
        selected = self.table.selection()
        if not selected:
            return

        item_id = selected[0]
        if item_id == "kosong":
            return

        try:
            row = self._hasil_terakhir()[int(item_id)]
            self.selected_row_data = row
        except (ValueError, IndexError):
            return

        status = str(row.get("status") or "Diajukan")
        nomor = row.get("nomor_pengajuan") or "-"
        jenis = row.get("jenis_surat") or row.get("nama_jenis") or row.get("nama_jenis_surat") or "-"
        nama_dosen = row.get("nama_dosen") or "Dosen Pembimbing Akademik"
        nip_dosen = row.get("nip_dosen") or "-"
        ttd = row.get("tanda_tangan_digital")
        tgl_ttd = self.format_date(row.get("tanggal_keputusan_dosen") or row.get("tanggal_disetujui"))
        catatan_dosen = row.get("catatan_dosen") or "Belum ada catatan dosen."
        catatan_admin = row.get("catatan_admin") or "Belum ada catatan admin."

        if status.lower() in ("selesai", "disetujui"):
            warna, warna_teks = PALE_GREEN, "#477A58"
            status_judul = f"STATUS: {status.upper()} — TELAH DITANDATANGANI DOSEN"
        elif status.lower() == "ditolak":
            warna, warna_teks = "#F7E8E2", "#B65C54"
            status_judul = "STATUS: DITOLAK"
        else:
            warna, warna_teks = PALE_AMBER, "#A96335"
            status_judul = f"STATUS: {status.upper()} (MENUNGGU TANDA TANGAN DOSEN)"

        self.detail.configure(bg=warna)
        self.detail_title.configure(
            bg=warna,
            fg=warna_teks,
            text=status_judul
        )

        detail_lines = [
            f"Nomor: #{nomor}  |  Jenis Surat: {jenis}",
            f"Dosen Pembimbing/Wali: {nama_dosen} (NIDN/NIP. {nip_dosen})",
            f"Catatan Dosen: {catatan_dosen}"
        ]

        if ttd and status.lower() in ("selesai", "disetujui"):
            detail_lines.append(f"Hash Verifikasi SHA-256: {ttd[:32]}...  (Disahkan: {tgl_ttd})")

        if catatan_admin != "Belum ada catatan admin.":
            detail_lines.append(f"Catatan Admin: {catatan_admin}")

        self.detail_text.configure(
            bg=warna,
            text="\n".join(detail_lines),
            fg="#2C4037"
        )

    def buka_pratinjau_surat(self):
        """Membuka dokumen surat resmi bertanda tangan asli & digital (khusus status Disetujui/Selesai)."""
        if not self.selected_row_data:
            messagebox.showwarning(
                "Pilih Pengajuan",
                "Pilih satu pengajuan pada tabel terlebih dahulu."
            )
            return

        status = str(self.selected_row_data.get("status") or "Diajukan").strip()
        if status.lower() == "ditolak":
            alasan = (
                self.selected_row_data.get("catatan_dosen")
                or self.selected_row_data.get("catatan_admin")
                or "Tidak ada catatan penolakan."
            )
            messagebox.showerror(
                "Pengajuan Ditolak",
                f"Surat tidak dapat dilihat atau diunduh karena pengajuan berstatus DITOLAK.\n\n"
                f"Catatan / Alasan:\n{alasan}"
            )
            return

        if status.lower() not in ("disetujui", "selesai"):
            messagebox.showinfo(
                "Belum Disetujui",
                f"Surat masih berstatus '{status}' dan menunggu verifikasi serta tanda tangan dosen.\n\n"
                "Dokumen resmi dan unduhan PDF akan tersedia setelah status berubah menjadi Disetujui."
            )
            return

        SuratPreviewDialog(self, self.selected_row_data)

    def _hasil_terakhir(self):
        return self.controller.filter_pengajuan(
            self.rows,
            keyword=self._get_query_aktif(),
            filter_status=self.filter_var.get()
        )

    @staticmethod
    def format_date(value):
        if value is None:
            return "-"
        if hasattr(value, "strftime"):
            return value.strftime("%d %b %Y")
        try:
            return datetime.strptime(str(value)[:19], "%Y-%m-%d %H:%M:%S").strftime("%d %b %Y")
        except ValueError:
            return str(value)