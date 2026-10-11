import tkinter as tk
from tkinter import ttk

from views.theme import (
    BG, WHITE, NAVY, BLUE, MUTED, PALE_BLUE, PALE_AMBER, PALE_GREEN,
    page_heading, panel, primary_button
)


class StatusView(tk.Frame):
    def __init__(self, master, on_navigate=None):
        super().__init__(master, bg=BG)

        page_heading(
            self,
            "Riwayat layanan",
            "Status pengajuan",
            "Cari nomor permohonan atau tinjau riwayat pengajuan Anda."
        )

        search = panel(self, 15, 13)
        search.pack(fill="x", pady=(0, 16))

        tk.Label(
            search, text="⌕", bg=WHITE, fg=BLUE,
            font=("Segoe UI", 17, "bold")
        ).pack(side="left", padx=(0, 9))

        self.hint = "Cari nomor pengajuan, contoh PGJ-001"
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
            title_area, text="Daftar permohonan", bg=WHITE, fg=NAVY,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")

        tk.Label(
            title_area, text="Data contoh untuk pratinjau tampilan",
            bg=WHITE, fg=MUTED, font=("Segoe UI", 8)
        ).pack(anchor="w", pady=(3, 0))

        ttk.Combobox(
            header,
            state="readonly",
            width=17,
            values=["Semua status", "Menunggu", "Disetujui", "Ditolak"]
        ).pack(side="right")

        columns = ("nomor", "tanggal", "jenis", "status")
        self.table = ttk.Treeview(
            card, columns=columns, show="headings", height=8
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
                col, width=150 if col != "jenis" else 360, anchor="w"
            )

        self.rows = [
            ("PGJ-001", "01 Okt 2026", "Surat Keterangan Aktif Kuliah (SKAK)", "Disetujui"),
            ("PGJ-002", "02 Okt 2026", "Permohonan Keringanan/Penurunan UKT", "Disetujui"),
            ("PGJ-003", "03 Okt 2026", "Surat Permohonan Cuti Akademik", "Ditolak"),
            ("PGJ-004", "04 Okt 2026", "Surat Permohonan Cuti Akademik", "Menunggu")
        ]

        self.populate(self.rows)
        self.table.pack(fill="both", expand=True)

        self.detail = tk.Frame(self, bg=PALE_BLUE, padx=15, pady=12)
        self.detail.pack(fill="x", pady=(14, 0))

        tk.Label(
            self.detail, text="INFORMASI STATUS", bg=PALE_BLUE, fg=BLUE,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")

        tk.Label(
            self.detail,
            text="Pilih salah satu pengajuan untuk melihat statusnya.",
            bg=PALE_BLUE,
            fg="#596D5E",
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(4, 0))

        self.table.bind("<<TreeviewSelect>>", self.pilih_baris)

    def populate(self, rows):
        self.table.delete(*self.table.get_children())
        for row in rows:
            self.table.insert("", "end", values=row)

    def clear_hint(self, _event=None):
        if self.nomor.get() == self.hint:
            self.nomor.delete(0, "end")
            self.nomor.configure(fg=NAVY)

    def restore_hint(self, _event=None):
        if not self.nomor.get().strip():
            self.nomor.insert(0, self.hint)
            self.nomor.configure(fg="#818B80")

    def cari(self):
        query = self.nomor.get().strip().lower()
        if query == self.hint.lower():
            query = ""

        hasil = [
            row for row in self.rows
            if not query or query in row[0].lower()
        ]
        self.populate(hasil)

        if hasil:
            item = self.table.get_children()[0]
            self.table.selection_set(item)
            self.table.focus(item)
            self.table.see(item)
            self.pilih_baris()
        else:
            self.detail.configure(bg=PALE_AMBER)
            labels = self.detail.winfo_children()
            labels[0].configure(bg=PALE_AMBER, fg="#A96335")
            labels[1].configure(
                bg=PALE_AMBER,
                text="Nomor pengajuan tidak ditemukan.",
                fg="#77563D"
            )

    def pilih_baris(self, _event=None):
        selected = self.table.selection()
        if not selected:
            return

        values = self.table.item(selected[0], "values")
        status = values[3]

        if status == "Disetujui":
            color = PALE_GREEN
            label_color = "#477A58"
        elif status == "Menunggu":
            color = PALE_AMBER
            label_color = "#A96335"
        else:
            color = "#F7E8E2"
            label_color = "#B65C54"

        self.detail.configure(bg=color)
        labels = self.detail.winfo_children()
        labels[0].configure(bg=color, fg=label_color)
        labels[1].configure(
            bg=color,
            text=f"{values[0]}  •  {status}  •  {values[2]}",
            fg="#596D5E"
        )