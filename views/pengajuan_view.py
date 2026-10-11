import tkinter as tk
from tkinter import ttk, messagebox
from models.jenis_surat_model import JenisSuratModel

from views.theme import (
    BG, WHITE, NAVY, BLUE, MUTED, LINE, PALE_BLUE,
    page_heading, panel, primary_button, secondary_button, labeled_entry
)


class PengajuanView(tk.Frame):
    def __init__(self, master, on_navigate=None):
        super().__init__(master, bg=BG)

        page_heading(
            self,
            "Layanan mahasiswa",
            "Buat pengajuan surat",
            "Isi informasi berikut untuk memulai permohonan surat Anda."
        )

        layout = tk.Frame(self, bg=BG)
        layout.pack(fill="both", expand=True)

        form = panel(layout, 22, 20)
        form.pack(side="left", fill="both", expand=True, padx=(0, 16))

        side = panel(layout, 18, 18)
        side.configure(width=270)
        side.pack(side="right", fill="y")
        side.pack_propagate(False)

        tk.Label(
            form, text="Informasi pemohon", bg=WHITE, fg=NAVY,
            font=("Segoe UI", 12, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        tk.Label(
            form,
            text="Pastikan data sesuai dengan identitas mahasiswa.",
            bg=WHITE,
            fg=MUTED,
            font=("Segoe UI", 8)
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 17))

        self.jenis_surat_data = []
        self.jenis_surat_by_nama = {}

        self.entries = {}
        self.add_input(form, "NIM *", "nim", "Contoh: F52125100", 2, 0)
        self.add_input(form, "Nama mahasiswa *", "nama", "Nama lengkap", 2, 1)
        self.add_input(form, "Program studi *", "prodi", "Program studi", 4, 0)
        self.add_input(form, "Email", "email", "nama@email.com", 4, 1)

        tk.Label(
            form, text="Jenis surat *", bg=WHITE, fg="#2C4037",
            font=("Segoe UI", 9, "bold")
        ).grid(row=6, column=0, sticky="w", pady=(4, 7))

        self.jenis = ttk.Combobox(
                form,
                state="readonly",
                font=("Segoe UI", 10),
                values=[]
            )
        
        self.jenis.grid(
            row=7,
            column=0,
            columnspan=2,
            sticky="ew",
            ipady=4
        )
        self.jenis.set("Pilih jenis surat")

        self.info_jenis = tk.Label(
            form,
            text="Memuat jenis surat dari database...",
            bg=WHITE,
            fg=MUTED,
            font=("Segoe UI", 8)
        )
        self.info_jenis.grid(
            row=7,
            column=0,
            columnspan=2,
            sticky="e",
            pady=(35, 0)
        )

        self.load_jenis_surat()
        self.jenis.grid(row=7, column=0, columnspan=2, sticky="ew", ipady=4)
        self.jenis.set("Pilih jenis surat")

        tk.Label(
            form, text="Keterangan / keperluan *", bg=WHITE, fg="#2C4037",
            font=("Segoe UI", 9, "bold")
        ).grid(row=8, column=0, sticky="w", pady=(16, 7))

        self.keterangan = tk.Text(
            form, height=4, font=("Segoe UI", 10), relief="solid",
            bd=1, wrap="word", highlightthickness=1,
            highlightbackground=LINE, highlightcolor=BLUE
        )
        self.keterangan.grid(row=9, column=0, columnspan=2, sticky="ew")

        attach = tk.Frame(
            form, bg="#F8F8F0", padx=13, pady=11,
            highlightbackground=LINE, highlightthickness=1
        )
        attach.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(14, 0))

        tk.Label(
            attach, text="＋  Tambahkan lampiran", bg="#F8F8F0", fg=BLUE,
            font=("Segoe UI", 9, "bold")
        ).pack(side="left")

        tk.Label(
            attach, text="PDF / JPG · maks. 5 MB", bg="#F8F8F0", fg=MUTED,
            font=("Segoe UI", 8)
        ).pack(side="right")

        actions = tk.Frame(form, bg=WHITE)
        actions.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(17, 0))

        secondary_button(
            actions, "Batal", lambda: on_navigate("dashboard")
        ).pack(side="right", padx=(8, 0))

        primary_button(
            actions, "Kirim pengajuan  →", self.kirim
        ).pack(side="right")

        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        tk.Label(
            side, text="PANDUAN", bg=WHITE, fg=BLUE,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")

        tk.Label(
            side, text="Sebelum mengirim", bg=WHITE, fg=NAVY,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=(5, 15))

        panduan = [
            "Gunakan data mahasiswa yang aktif.",
            "Pilih jenis surat yang sesuai kebutuhan.",
            "Jelaskan keperluan secara singkat dan jelas.",
            "Siapkan dokumen pendukung jika dibutuhkan."
        ]

        for nomor, teks in enumerate(panduan, start=1):
            row = tk.Frame(side, bg=WHITE)
            row.pack(fill="x", pady=8)

            tk.Label(
                row, text=str(nomor), bg=PALE_BLUE, fg=BLUE,
                width=2, pady=4, font=("Segoe UI", 8, "bold")
            ).pack(side="left", padx=(0, 9))

            tk.Label(
                row, text=teks, bg=WHITE, fg="#596D5E",
                wraplength=190, justify="left", font=("Segoe UI", 8)
            ).pack(side="left", fill="x")

        tk.Frame(side, bg=LINE, height=1).pack(fill="x", pady=15)

        tk.Label(
            side, text="ESTIMASI PEMROSESAN", bg=WHITE, fg=MUTED,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")

        tk.Label(
            side, text="1–3 hari kerja", bg=WHITE, fg="#477A58",
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", pady=(5, 0))

    def add_input(self, parent, label, key, hint, row, column):
        wrap, entry = labeled_entry(parent, label, hint)
        wrap.grid(
            row=row,
            column=column,
            sticky="ew",
            padx=(0, 9) if column == 0 else (9, 0),
            pady=(0, 14)
        )
        self.entries[key] = (entry, hint)

    def kirim(self):
        nama_jenis = self.jenis.get()
        jenis_terpilih = self.jenis_surat_by_nama.get(nama_jenis)

        if not jenis_terpilih:
            messagebox.showwarning(
                "Jenis surat tidak tersedia",
                "Pilih jenis surat aktif dari daftar."
            )
            return

        id_jenis_surat = jenis_terpilih["id_jenis_surat"]

        if not self.keterangan.get("1.0", "end").strip():
            messagebox.showwarning(
                "Form belum lengkap",
                "Isi keterangan atau keperluan surat."
            )
            return

        messagebox.showinfo(
            "Pengajuan siap",
            "Tampilan formulir sudah siap. Sambungkan tombol ini ke "
            "PengajuanController untuk menyimpan ke database."
        )

    def load_jenis_surat(self):
        try:
            # Mengambil hanya jenis surat yang aktif dari database.
            self.jenis_surat_data = JenisSuratModel().aktif_saja() or []

            self.jenis_surat_by_nama = {}
            nama_jenis = []

            for row in self.jenis_surat_data:
                nama = (
                    row.get("nama_jenis")
                    or row.get("nama_jenis_surat")
                )

                if nama:
                    nama_jenis.append(nama)
                    self.jenis_surat_by_nama[nama] = row

            self.jenis.configure(values=nama_jenis)

            if nama_jenis:
                self.jenis.set("Pilih jenis surat")
                self.info_jenis.configure(
                    text=f"{len(nama_jenis)} jenis surat tersedia",
                    fg=MUTED
                )
            else:
                self.jenis.set("Tidak ada jenis surat aktif")
                self.info_jenis.configure(
                    text="Periksa data jenis surat di database.",
                    fg="#A96335"
                )

        except Exception as error:
            self.jenis.configure(values=[])
            self.jenis.set("Gagal memuat jenis surat")
            self.info_jenis.configure(
                text=f"Kesalahan database: {error}",
                fg="#B65C54"
            )