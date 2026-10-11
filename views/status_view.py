import tkinter as tk
from tkinter import ttk
from datetime import datetime

from models.pengajuan_surat_model import PengajuanSuratModel
from views.theme import (
    BG, WHITE, NAVY, BLUE, MUTED,
    PALE_BLUE, PALE_AMBER, PALE_GREEN,
    page_heading, panel, primary_button
)


class StatusView(tk.Frame):
    def __init__(self, master, on_navigate=None):
        super().__init__(master, bg=BG)

        self.on_navigate = on_navigate
        self.rows = []
        self.error_message = None

        page_heading(
            self,
            "Riwayat layanan",
            "Status pengajuan",
            "Cari dan tinjau status pengajuan surat dari database."
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

        self.hint = "Cari nomor atau jenis surat"
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
            text="Daftar permohonan",
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

        columns = ("nomor", "tanggal", "jenis", "status")
        self.table = ttk.Treeview(
            card,
            columns=columns,
            show="headings",
            height=8
        )

        headings = {
            "nomor": "NOMOR PENGAJUAN",
            "tanggal": "TANGGAL",
            "jenis": "JENIS SURAT",
            "status": "STATUS"
        }

        for col in columns:
            self.table.heading(col, text=headings[col])
            self.table.column(
                col,
                width=170 if col != "jenis" else 360,
                anchor="w"
            )

        self.table.pack(fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self.pilih_baris)

        self.detail = tk.Frame(self, bg=PALE_BLUE, padx=15, pady=12)
        self.detail.pack(fill="x", pady=(14, 0))

        self.detail_title = tk.Label(
            self.detail,
            text="INFORMASI STATUS",
            bg=PALE_BLUE,
            fg=BLUE,
            font=("Segoe UI", 8, "bold")
        )
        self.detail_title.pack(anchor="w")

        self.detail_text = tk.Label(
            self.detail,
            text="Pilih salah satu pengajuan untuk melihat detailnya.",
            bg=PALE_BLUE,
            fg="#596D5E",
            font=("Segoe UI", 9),
            justify="left",
            wraplength=1000
        )
        self.detail_text.pack(anchor="w", pady=(4, 0))

        self.muat_data()

    def muat_data(self):
        try:
            # Login belum tersambung, jadi muat seluruh pengajuan.
            self.rows = PengajuanSuratModel().semua_dengan_relasi() or []
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
                text=f"{len(self.rows)} pengajuan dari database"
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

    def tampilkan_hasil(self):
        query = self.nomor.get().strip().lower()
        if query == self.hint.lower():
            query = ""

        status_pilihan = self.filter_var.get()
        hasil = []

        for row in self.rows:
            nomor = str(row.get("nomor_pengajuan") or "")
            jenis = str(
                row.get("nama_jenis_surat")
                or row.get("nama_jenis")
                or ""
            )
            nama = str(
                row.get("nama_mahasiswa")
                or row.get("nama")
                or ""
            )
            status = str(row.get("status") or "")

            cocok_status = (
                status_pilihan == "Semua status"
                or status == status_pilihan
            )
            cocok_cari = (
                not query
                or query in nomor.lower()
                or query in jenis.lower()
                or query in nama.lower()
            )

            if cocok_status and cocok_cari:
                hasil.append(row)

        self.table.delete(*self.table.get_children())

        for index, row in enumerate(hasil):
            nomor = row.get("nomor_pengajuan") or "-"
            jenis = (
                row.get("nama_jenis_surat")
                or row.get("nama_jenis")
                or "-"
            )
            tanggal = self.format_date(row.get("tanggal_pengajuan"))
            status = row.get("status") or "-"

            self.table.insert(
                "",
                "end",
                iid=str(index),
                values=(nomor, tanggal, jenis, status)
            )

        if not hasil:
            pesan = (
                "Tidak ada pengajuan yang cocok dengan pencarian/filter."
                if self.rows
                else "Belum ada data pengajuan di database."
            )
            self.table.insert(
                "",
                "end",
                iid="kosong",
                values=(pesan, "-", "-", "-")
            )

    def tabel_pesan(self, nomor, pesan):
        self.table.delete(*self.table.get_children())
        self.table.insert(
            "",
            "end",
            values=(nomor, "-", "-", "-")
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
        except (ValueError, IndexError):
            return

        status = str(row.get("status") or "Tanpa status")
        nomor = row.get("nomor_pengajuan") or "-"
        jenis = (
            row.get("nama_jenis_surat")
            or row.get("nama_jenis")
            or "-"
        )
        catatan = row.get("catatan_admin") or "Belum ada catatan admin."

        if status.lower() in ("selesai", "disetujui"):
            warna, warna_teks = PALE_GREEN, "#477A58"
        elif status.lower() in ("diajukan", "menunggu", "diproses"):
            warna, warna_teks = PALE_AMBER, "#A96335"
        else:
            warna, warna_teks = "#F7E8E2", "#B65C54"

        self.detail.configure(bg=warna)
        self.detail_title.configure(
            bg=warna,
            fg=warna_teks,
            text=f"STATUS: {status.upper()}"
        )
        self.detail_text.configure(
            bg=warna,
            text=f"{nomor}  •  {jenis}\nCatatan admin: {catatan}",
            fg="#596D5E"
        )

    def _hasil_terakhir(self):
        """Kembalikan data sesuai baris yang sedang tampil di tabel."""
        query = self.nomor.get().strip().lower()
        if query == self.hint.lower():
            query = ""

        status_pilihan = self.filter_var.get()
        return [
            row for row in self.rows
            if (
                status_pilihan == "Semua status"
                or str(row.get("status") or "") == status_pilihan
            )
            and (
                not query
                or query in str(row.get("nomor_pengajuan") or "").lower()
                or query in str(
                    row.get("nama_jenis_surat")
                    or row.get("nama_jenis")
                    or ""
                ).lower()
                or query in str(
                    row.get("nama_mahasiswa")
                    or row.get("nama")
                    or ""
                ).lower()
            )
        ]

    @staticmethod
    def format_date(value):
        if value is None:
            return "-"

        if hasattr(value, "strftime"):
            return value.strftime("%d %b %Y")

        try:
            return datetime.strptime(
                str(value)[:19],
                "%Y-%m-%d %H:%M:%S"
            ).strftime("%d %b %Y")
        except ValueError:
            return str(value)