import tkinter as tk
from tkinter import ttk

from models.mahasiswa_model import MahasiswaModel
from models.pengajuan_surat_model import PengajuanSuratModel
from views.theme import (
    BG, WHITE, NAVY, BLUE, MUTED, LINE,
    GREEN, AMBER, RED, PALE_BLUE, PALE_GREEN,
    PALE_AMBER, PALE_RED,
    page_heading, panel
)


class DashboardView(tk.Frame):
    def __init__(self, master, on_navigate=None):
        super().__init__(master, bg=BG)
        self.on_navigate = on_navigate
        self.error_message = None
        self.pengajuan = []

        self.load_data()
        self.build_view()

        self.load_data()
        self.build_view()

    def load_data(self):
        try:
            self.pengajuan = PengajuanSuratModel().semua_dengan_relasi() or []
            self.error_message = None
        except Exception as error:
            self.error_message = str(error)
            self.pengajuan = []

    def build_view(self):

        page_heading(
            self,
            "Ringkasan",
            "Dashboard Mahasiswa",
            "Ringkasan seluruh pengajuan surat dari database."
        )

        if self.error_message:
            tk.Label(
                self,
                text=f"Data belum dapat dimuat: {self.error_message}",
                bg=PALE_AMBER,
                fg="#805226",
                anchor="w",
                padx=12,
                pady=10,
                wraplength=900,
                justify="left"
            ).pack(fill="x", pady=(0, 12))

        stats = tk.Frame(self, bg=BG)
        stats.pack(fill="x", pady=(0, 18))

        # Kartu jumlah status dibuat dari data yang diterima dari database.
        status_counts = {}
        for row in self.pengajuan:
            status = (row.get("status") or "Tanpa status").strip()
            status_counts[status] = status_counts.get(status, 0) + 1

        self.stat_card(
            stats,
            "Total pengajuan",
            str(len(self.pengajuan)),
            "Semua permohonan",
            BLUE,
            PALE_BLUE
        )

        warna_status = {
            "Diajukan": (AMBER, PALE_AMBER),
            "Menunggu": (AMBER, PALE_AMBER),
            "Diproses": (BLUE, PALE_BLUE),
            "Disetujui": (GREEN, PALE_GREEN),
            "Selesai": (GREEN, PALE_GREEN),
            "Ditolak": (RED, PALE_RED),
        }

        urutan_status = [
            "Diajukan", "Menunggu", "Diproses",
            "Disetujui", "Selesai", "Ditolak"
        ]

        status_tersedia = [
            status for status in urutan_status
            if status in status_counts
        ]
        status_lain = [
            status for status in status_counts
            if status not in urutan_status
        ]
        status_tersedia.extend(sorted(status_lain))

        for status in status_tersedia:
            accent, tint = warna_status.get(status, (BLUE, PALE_BLUE))
            self.stat_card(
                stats,
                status,
                str(status_counts[status]),
                f"Pengajuan berstatus {status.lower()}",
                accent,
                tint
            )

        recent = panel(self, 20, 17)
        recent.pack(fill="both", expand=True)

        heading = tk.Frame(recent, bg=WHITE)
        heading.pack(fill="x", pady=(0, 13))

        tk.Label(
            heading,
            text="Pengajuan terbaru",
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")

        tk.Button(
            heading,
            text="Lihat semua  →",
            bg=WHITE,
            fg=BLUE,
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            command=self.open_status
        ).pack(side="right")

        columns = ("nomor", "jenis", "tanggal", "status")
        table = ttk.Treeview(
            recent,
            columns=columns,
            show="headings",
            height=6
        )

        titles = {
            "nomor": "NOMOR PENGAJUAN",
            "jenis": "JENIS SURAT",
            "tanggal": "TANGGAL",
            "status": "STATUS"
        }

        for col in columns:
            table.heading(col, text=titles[col])
            table.column(
                col,
                width=160 if col != "jenis" else 300,
                anchor="w"
            )

        for row in self.pengajuan[:8]:
            table.insert(
                "",
                "end",
                values=(
                    row.get("nomor_pengajuan", "-"),
                    row.get("nama_jenis_surat") or row.get("nama_jenis") or "-",
                    self.format_date(row.get("tanggal_pengajuan")),
                    row.get("status", "-")
                )
            )

        if not self.pengajuan and not self.error_message:
            table.insert(
                "",
                "end",
                values=("Belum ada pengajuan", "-", "-", "-")
            )

        table.pack(fill="both", expand=True)

        bottom = tk.Frame(self, bg=BG)
        bottom.pack(fill="x", pady=(16, 0))

        note = tk.Frame(bottom, bg="#EEF2E5", padx=14, pady=11)
        note.pack(side="left", fill="x", expand=True)

        tk.Label(
            note,
            text="TIPS",
            bg="#EEF2E5",
            fg=BLUE,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")

        tk.Label(
            note,
            text="Lengkapi persyaratan agar proses surat berjalan lancar.",
            bg="#EEF2E5",
            fg="#596D5E",
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(3, 0))

        tk.Button(
            bottom,
            text="＋  Buat pengajuan",
            bg=BLUE,
            fg=WHITE,
            activebackground="#3D6330",
            activeforeground=WHITE,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=17,
            pady=12,
            font=("Segoe UI", 9, "bold"),
            command=self.open_pengajuan
        ).pack(side="right", padx=(14, 0))

    def open_status(self):
        if self.on_navigate:
            self.on_navigate("status")

    def open_pengajuan(self):
        if self.on_navigate:
            self.on_navigate("pengajuan")

    @staticmethod
    def format_date(value):
        if value is None:
            return "-"
        if hasattr(value, "strftime"):
            return value.strftime("%d %b %Y")
        return str(value)

    @staticmethod
    def stat_card(parent, title, value, note, accent, tint):
        card = tk.Frame(
            parent,
            bg=WHITE,
            padx=16,
            pady=15,
            highlightbackground=LINE,
            highlightthickness=1
        )
        card.pack(side="left", fill="both", expand=True, padx=(0, 11))

        row = tk.Frame(card, bg=WHITE)
        row.pack(fill="x")

        tk.Label(
            row,
            text=title,
            bg=WHITE,
            fg=MUTED,
            font=("Segoe UI", 9, "bold")
        ).pack(side="left")

        tk.Label(
            row,
            text="●",
            bg=WHITE,
            fg=accent,
            font=("Segoe UI", 10)
        ).pack(side="right")

        tk.Label(
            card,
            text=value,
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 25, "bold")
        ).pack(anchor="w", pady=(8, 1))

        tk.Label(
            card,
            text=note,
            bg=WHITE,
            fg=MUTED,
            font=("Segoe UI", 8)
        ).pack(anchor="w")