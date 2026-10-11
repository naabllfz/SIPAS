import tkinter as tk
from tkinter import ttk

from views.theme import (
    BG, WHITE, NAVY, BLUE, MUTED, LINE,
    GREEN, AMBER, RED, PALE_BLUE, PALE_GREEN, PALE_AMBER, PALE_RED,
    page_heading, panel
)


class DashboardView(tk.Frame):
    def __init__(self, master, on_navigate=None):
        super().__init__(master, bg=BG)
        page_heading(
            self,
            "Ringkasan",
            "Halo, Nabila 👋",
            "Berikut ringkasan pengajuan surat akademik Anda."
        )

        stats = tk.Frame(self, bg=BG)
        stats.pack(fill="x", pady=(0, 18))

        self.stat_card(stats, "Total pengajuan", "04", "Semua permohonan", BLUE, PALE_BLUE)
        self.stat_card(stats, "Menunggu", "01", "Dalam antrean", AMBER, PALE_AMBER)
        self.stat_card(stats, "Disetujui", "02", "Siap ditindaklanjuti", GREEN, PALE_GREEN)
        self.stat_card(stats, "Ditolak", "01", "Lihat keterangan", RED, PALE_RED)

        recent = panel(self, 20, 17)
        recent.pack(fill="both", expand=True)

        heading = tk.Frame(recent, bg=WHITE)
        heading.pack(fill="x", pady=(0, 13))

        tk.Label(
            heading, text="Pengajuan terbaru", bg=WHITE, fg=NAVY,
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")

        tk.Button(
            heading, text="Lihat semua  →", bg=WHITE, fg=BLUE,
            relief="flat", cursor="hand2", font=("Segoe UI", 9, "bold"),
            command=lambda: on_navigate("status")
        ).pack(side="right")

        columns = ("nomor", "jenis", "tanggal", "status")
        table = ttk.Treeview(recent, columns=columns, show="headings", height=6)

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

        data = [
            ("PGJ-001", "Surat Keterangan Aktif Kuliah (SKAK)", "01 Okt 2026", "Disetujui"),
            ("PGJ-002", "Permohonan Keringanan/Penurunan UKT", "02 Okt 2026", "Disetujui"),
            ("PGJ-003", "Surat Permohonan Cuti Akademik", "03 Okt 2026", "Ditolak"),
            ("PGJ-004", "Surat Permohonan Cuti Akademik", "04 Okt 2026", "Menunggu")
        ]

        for row in data:
            table.insert("", "end", values=row)

        table.pack(fill="both", expand=True)

        bottom = tk.Frame(self, bg=BG)
        bottom.pack(fill="x", pady=(16, 0))

        note = tk.Frame(bottom, bg="#EEF2E5", padx=14, pady=11)
        note.pack(side="left", fill="x", expand=True)

        tk.Label(
            note, text="TIPS", bg="#EEF2E5", fg=BLUE,
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
            command=lambda: on_navigate("pengajuan")
        ).pack(side="right", padx=(14, 0))

    @staticmethod
    def stat_card(parent, title, value, note, accent, tint):
        card = tk.Frame(
            parent, bg=WHITE, padx=16, pady=15,
            highlightbackground=LINE, highlightthickness=1
        )
        card.pack(side="left", fill="both", expand=True, padx=(0, 11))

        row = tk.Frame(card, bg=WHITE)
        row.pack(fill="x")

        tk.Label(
            row, text=title, bg=WHITE, fg=MUTED,
            font=("Segoe UI", 9, "bold")
        ).pack(side="left")

        tk.Label(
            row, text="●", bg=WHITE, fg=accent,
            font=("Segoe UI", 10)
        ).pack(side="right")

        tk.Label(
            card, text=value, bg=WHITE, fg=NAVY,
            font=("Segoe UI", 25, "bold")
        ).pack(anchor="w", pady=(8, 1))

        tk.Label(
            card, text=note, bg=WHITE, fg=MUTED,
            font=("Segoe UI", 8)
        ).pack(anchor="w")