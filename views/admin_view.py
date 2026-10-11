import tkinter as tk
from tkinter import ttk, messagebox

from models.pengajuan_surat_model import PengajuanSuratModel
from models.mahasiswa_model import MahasiswaModel
from models.jenis_surat_model import JenisSuratModel
from views.theme import (
    BG, WHITE, NAVY, BLUE, MUTED, LINE,
    AMBER, GREEN, RED, PALE_BLUE, PALE_AMBER, PALE_GREEN,
    page_heading, panel, primary_button, secondary_button
)


class AdminView(tk.Frame):
    """Halaman admin untuk pengajuan dan data master yang tersedia di database."""

    def __init__(self, master, page="dashboard"):
        super().__init__(master, bg=BG)
        self.page = page
        self.pengajuan = []
        self.mahasiswa = []
        self.jenis_surat = []
        self.error_message = None

        if page in ("dashboard", "queue"):
            self.load_pengajuan()
        elif page == "mahasiswa":
            self.load_mahasiswa()
        elif page == "jenis_surat":
            self.load_jenis_surat()

        if page == "queue":
            self.show_queue()
        elif page == "mahasiswa":
            self.show_mahasiswa()
        elif page == "jenis_surat":
            self.show_jenis_surat()
        else:
            self.show_dashboard()

    @staticmethod
    def format_date(value):
        if value is None:
            return "-"
        if hasattr(value, "strftime"):
            return value.strftime("%d %b %Y")
        return str(value)

    def load_pengajuan(self):
        try:
            records = PengajuanSuratModel().semua_dengan_relasi()
            self.pengajuan = [
                (
                    record.get("nomor_pengajuan", ""),
                    record.get("nama_mahasiswa", ""),
                    record.get("nama_jenis_surat", ""),
                    self.format_date(record.get("tanggal_pengajuan")),
                    record.get("status", "")
                )
                for record in records
            ]
            self.error_message = None
        except Exception as error:
            self.pengajuan = []
            self.error_message = str(error)

    def load_mahasiswa(self):
        try:
            records = MahasiswaModel().semua()
            self.mahasiswa = [
                (
                    record.get("id_mahasiswa"),
                    record.get("nim", ""),
                    record.get("nama_mahasiswa", ""),
                    record.get("program_studi", ""),
                    record.get("email", "") or "-"
                )
                for record in records
            ]
            self.error_message = None
        except Exception as error:
            self.mahasiswa = []
            self.error_message = str(error)

    def load_jenis_surat(self):
        try:
            records = JenisSuratModel().semua()
            self.jenis_surat = [
                (
                    record.get("id_jenis_surat"),
                    record.get("nama_jenis_surat", ""),
                    record.get("deskripsi", "") or "-"
                )
                for record in records
            ]
            self.error_message = None
        except Exception as error:
            self.jenis_surat = []
            self.error_message = str(error)

    def jumlah_status(self, status):
        return sum(
            1 for row in self.pengajuan
            if str(row[4]).strip().lower() == status.lower()
        )

    def show_database_error(self):
        notice = tk.Frame(self, bg=PALE_AMBER, padx=12, pady=9)
        notice.pack(fill="x", pady=(0, 12))
        tk.Label(
            notice,
            text="Data belum dapat dimuat. Periksa koneksi MySQL dan konfigurasi database.",
            bg=PALE_AMBER,
            fg="#805226",
            font=("Segoe UI", 9)
        ).pack(anchor="w")

    def show_dashboard(self):
        page_heading(
            self,
            "Area administrasi",
            "Dashboard admin",
            "Ringkasan permohonan dan data layanan dari database."
        )

        cards = tk.Frame(self, bg=BG)
        cards.pack(fill="x", pady=(0, 18))
        if self.error_message:
            values = [
                ("Total Pengajuan", "—", BLUE),
                ("Menunggu", "—", AMBER),
                ("Disetujui", "—", GREEN),
                ("Ditolak", "—", RED),
            ]
            self.show_database_error()
        else:
            values = [
                ("Total Pengajuan", str(len(self.pengajuan)), BLUE),
                ("Menunggu", str(self.jumlah_status("Menunggu")), AMBER),
                ("Disetujui", str(self.jumlah_status("Disetujui")), GREEN),
                ("Ditolak", str(self.jumlah_status("Ditolak")), RED),
            ]

        for title, value, accent in values:
            self.stat_card(cards, title, value, accent)

        box = panel(self, 20, 17)
        box.pack(fill="both", expand=True)
        tk.Label(
            box, text="Pengajuan terbaru", bg=WHITE, fg=NAVY,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 13))
        self.table = self.make_table(
            box,
            ("nomor", "mahasiswa", "jenis", "tanggal", "status"),
            ("NOMOR", "MAHASISWA", "JENIS SURAT", "TANGGAL", "STATUS")
        )
        self.fill_table(self.pengajuan[:8])

    def show_queue(self):
        page_heading(
            self,
            "Area administrasi",
            "Kelola pengajuan",
            "Tinjau semua permohonan dan tentukan statusnya."
        )
        if self.error_message:
            self.show_database_error()

        box = panel(self, 20, 17)
        box.pack(fill="both", expand=True)
        toolbar = tk.Frame(box, bg=WHITE)
        toolbar.pack(fill="x", pady=(0, 14))
        tk.Label(
            toolbar, text="Daftar permohonan", bg=WHITE, fg=NAVY,
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")
        self.filter = ttk.Combobox(
            toolbar, state="readonly", width=18,
            values=["Semua status", "Menunggu", "Disetujui", "Ditolak"]
        )
        self.filter.set("Semua status")
        self.filter.pack(side="right")
        self.filter.bind("<<ComboboxSelected>>", self.filter_pengajuan)

        self.table = self.make_table(
            box,
            ("nomor", "mahasiswa", "jenis", "tanggal", "status"),
            ("NOMOR", "MAHASISWA", "JENIS SURAT", "TANGGAL", "STATUS")
        )
        self.fill_table(self.pengajuan)

        actions = tk.Frame(box, bg=WHITE)
        actions.pack(fill="x", pady=(15, 0))
        tk.Label(
            actions, text="Status pengajuan terpilih:", bg=WHITE, fg=MUTED,
            font=("Segoe UI", 9)
        ).pack(side="left")
        self.status = ttk.Combobox(
            actions, state="readonly", width=16,
            values=["Menunggu", "Disetujui", "Ditolak"]
        )
        self.status.set("Pilih status")
        self.status.pack(side="left", padx=9)
        primary_button(actions, "Simpan status", self.update_status).pack(side="right")

        self.filter = ttk.Combobox(
            toolbar,
            state="readonly",
            width=18,
            values=["Semua status", "Menunggu", "Disetujui", "Ditolak"]
        )
        self.filter.set("Semua status")
        self.filter.pack(side="right")
        self.filter.bind("<<ComboboxSelected>>", self.filter_pengajuan)

        self.search_hint = "Cari nomor, mahasiswa, atau jenis surat"
        self.search_var = tk.StringVar(value=self.search_hint)

        search_entry = tk.Entry(
            toolbar,
            textvariable=self.search_var,
            font=("Segoe UI", 9),
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground=LINE,
            highlightcolor=BLUE,
            fg="#929B8F"
        )
        search_entry.pack(
            side="right",
            fill="x",
            expand=True,
            padx=12,
            ipady=7
        )
        search_entry.bind("<FocusIn>", self.clear_search_hint)
        search_entry.bind("<FocusOut>", self.restore_search_hint)
        search_entry.bind("<KeyRelease>", self.filter_pengajuan)

    def show_mahasiswa(self):
        page_heading(
            self,
            "Data master",
            "Data mahasiswa",
            "Lihat data pemohon yang tersimpan pada database."
        )
        if self.error_message:
            self.show_database_error()
        box = panel(self, 20, 17)
        box.pack(fill="both", expand=True)
        toolbar = tk.Frame(box, bg=WHITE)
        toolbar.pack(fill="x", pady=(0, 14))
        tk.Label(toolbar, text=f"{len(self.mahasiswa)} mahasiswa", bg=WHITE,
                 fg=NAVY, font=("Segoe UI", 12, "bold")).pack(side="left")
        self.table = self.make_table(
            box,
            ("id", "nim", "nama", "prodi", "email"),
            ("ID", "NIM", "NAMA MAHASISWA", "PROGRAM STUDI", "EMAIL")
        )
        self.fill_table(self.mahasiswa)
        self.master_data_actions(box, "mahasiswa")

    def show_jenis_surat(self):
        page_heading(
            self,
            "Data master",
            "Jenis surat",
            "Lihat daftar jenis surat dan keterangan layanannya."
        )
        if self.error_message:
            self.show_database_error()
        box = panel(self, 20, 17)
        box.pack(fill="both", expand=True)
        toolbar = tk.Frame(box, bg=WHITE)
        toolbar.pack(fill="x", pady=(0, 14))
        tk.Label(toolbar, text=f"{len(self.jenis_surat)} jenis surat", bg=WHITE,
                 fg=NAVY, font=("Segoe UI", 12, "bold")).pack(side="left")
        self.table = self.make_table(
            box,
            ("id", "nama", "deskripsi"),
            ("ID", "NAMA JENIS SURAT", "DESKRIPSI")
        )
        self.fill_table(self.jenis_surat)
        self.master_data_actions(box, "jenis surat")

    @staticmethod
    def stat_card(parent, title, value, accent):
        card = tk.Frame(
            parent, bg=WHITE, padx=16, pady=16,
            highlightbackground=LINE, highlightthickness=1
        )
        card.pack(side="left", fill="x", expand=True, padx=(0, 11))
        tk.Label(card, text=title.upper(), bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        tk.Label(card, text=value, bg=WHITE, fg=accent,
                 font=("Segoe UI", 25, "bold")).pack(anchor="w", pady=(8, 0))

    @staticmethod
    def make_table(parent, columns, headings):
        table = ttk.Treeview(parent, columns=columns, show="headings", height=8)
        for column, heading in zip(columns, headings):
            table.heading(column, text=heading)
            table.column(column, width=140, anchor="w")
        table.pack(fill="both", expand=True)
        return table

    def fill_table(self, rows):
        self.table.delete(*self.table.get_children())
        for row in rows:
            self.table.insert("", "end", values=row)

    def filter_pengajuan(self, _event=None):
        status = self.filter.get()
        rows = self.pengajuan if status == "Semua status" else [
            row for row in self.pengajuan if row[4] == status
        ]
        self.fill_table(rows)

    def master_data_actions(self, parent, nama_data):
        actions = tk.Frame(parent, bg=WHITE)
        actions.pack(fill="x", pady=(14, 0))
        tk.Label(
            actions,
            text=f"Pengelolaan {nama_data} dapat dihubungkan ke controller.",
            bg=WHITE,
            fg=MUTED,
            font=("Segoe UI", 8)
        ).pack(side="left")
        secondary_button(
            actions, "Hapus", lambda: self.show_demo_action("Hapus", nama_data)
        ).pack(side="right", padx=(8, 0))
        secondary_button(
            actions, "Ubah", lambda: self.show_demo_action("Ubah", nama_data)
        ).pack(side="right", padx=(8, 0))
        primary_button(
            actions, "＋ Tambah", lambda: self.show_demo_action("Tambah", nama_data)
        ).pack(side="right")

    @staticmethod
    def show_demo_action(aksi, nama_data):
        messagebox.showinfo(
            "Mode demo",
            f"Aksi {aksi.lower()} {nama_data} masih berupa tampilan. "
            "Hubungkan tombol ini ke controller untuk mengelola database."
        )

    def update_status(self):
        selected = self.table.selection()
        new_status = self.status.get()
        if not selected:
            messagebox.showwarning(
                "Pilih pengajuan",
                "Pilih satu pengajuan pada tabel terlebih dahulu."
            )
            return
        if new_status == "Pilih status":
            messagebox.showwarning("Pilih status", "Pilih status baru terlebih dahulu.")
            return

        nomor = self.table.item(selected[0], "values")[0]
        messagebox.showinfo(
            "Mode demo",
            f"Status {nomor} akan diubah menjadi {new_status}. "
            "Hubungkan tombol ini ke AdminController untuk menyimpan perubahan."
        )

    def clear_search_hint(self, _event=None):
        if self.search_var.get() == self.search_hint:
            self.search_var.set("")


    def restore_search_hint(self, _event=None):
        if not self.search_var.get().strip():
            self.search_var.set(self.search_hint)


    def filter_pengajuan(self, _event=None):
        status = self.filter.get()
        query = self.search_var.get().strip().lower()

        if query == self.search_hint.lower():
            query = ""

        hasil = []

        for row in self.pengajuan:
            cocok_status = status == "Semua status" or row[4] == status
            cocok_kata = (
                not query
                or any(query in str(nilai).lower() for nilai in row[:3])
            )

            if cocok_status and cocok_kata:
                hasil.append(row)

        self.fill_table(hasil)
