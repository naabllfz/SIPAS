import tkinter as tk
from tkinter import messagebox

from views.theme import BG, WHITE, NAVY, BLUE, MUTED, LINE, labeled_entry


class LoginView(tk.Frame):
    def __init__(self, master, on_login):
        super().__init__(master, bg=BG)
        self.on_login = on_login

        visual = tk.Frame(self, bg=NAVY, width=470)
        visual.pack(side="left", fill="y")
        visual.pack_propagate(False)

        tk.Label(
            visual, text="S", bg=BLUE, fg=WHITE, width=2, height=1,
            font=("Segoe UI", 19, "bold")
        ).pack(anchor="w", padx=54, pady=(65, 10))

        tk.Label(
            visual, text="SIPAS", bg=NAVY, fg=WHITE,
            font=("Segoe UI", 26, "bold")
        ).pack(anchor="w", padx=54)

        tk.Label(
            visual,
            text="Layanan pengajuan surat akademik",
            bg=NAVY,
            fg="#B7CBB7",
            font=("Segoe UI", 11)
        ).pack(anchor="w", padx=56, pady=(5, 40))

        tk.Frame(
            visual, bg="#2D584A", height=1
        ).pack(fill="x", padx=54, pady=(0, 28))

        fitur = [
            ("01", "Ajukan surat", "Isi permohonan akademik dengan mudah."),
            ("02", "Pantau proses", "Lihat perkembangan pengajuan kapan saja."),
            ("03", "Terima informasi", "Status dan catatan tersedia di satu tempat.")
        ]

        for nomor, judul, detail in fitur:
            row = tk.Frame(visual, bg=NAVY)
            row.pack(fill="x", padx=54, pady=13)

            tk.Label(
                row, text=nomor, bg="#2D584A", fg="#CFDFC1",
                width=4, pady=8, font=("Segoe UI", 9, "bold")
            ).pack(side="left", padx=(0, 13))

            text = tk.Frame(row, bg=NAVY)
            text.pack(side="left", fill="x", expand=True)

            tk.Label(
                text, text=judul, bg=NAVY, fg=WHITE,
                font=("Segoe UI", 10, "bold")
            ).pack(anchor="w")

            tk.Label(
                text, text=detail, bg=NAVY, fg="#B6C9B5",
                font=("Segoe UI", 8), wraplength=230, justify="left"
            ).pack(anchor="w", pady=(4, 0))

        tk.Label(
            visual, text="PORTAL LAYANAN MAHASISWA  •  2026",
            bg=NAVY, fg="#8FA892", font=("Segoe UI", 8, "bold")
        ).pack(side="bottom", anchor="w", padx=54, pady=28)

        right = tk.Frame(self, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        card = tk.Frame(
            right, bg=WHITE, padx=42, pady=38,
            highlightbackground=LINE, highlightthickness=1
        )
        card.place(relx=0.5, rely=0.5, anchor="center", width=420, height=440)

        tk.Label(
            card, text="Selamat datang", bg=WHITE, fg=NAVY,
            font=("Segoe UI", 22, "bold")
        ).pack(anchor="w")

        tk.Label(
            card,
            text="Masuk untuk melanjutkan ke layanan surat.",
            bg=WHITE,
            fg=MUTED,
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(6, 25))

        wrap, self.username = labeled_entry(
            card, "Username atau NIM", "Masukkan username atau NIM"
        )
        wrap.pack(fill="x", pady=(0, 16))

        wrap, self.password = labeled_entry(
            card, "Kata sandi", "Masukkan kata sandi", show="•"
        )
        wrap.pack(fill="x")

        self.remember = tk.BooleanVar(value=True)
        tk.Checkbutton(
            card,
            text="Ingat saya di perangkat ini",
            variable=self.remember,
            bg=WHITE,
            fg=MUTED,
            activebackground=WHITE,
            selectcolor=WHITE,
            font=("Segoe UI", 8)
        ).pack(anchor="w", pady=(12, 18))

        tk.Button(
            card,
            text="Lanjutkan ke aplikasi  →",
            command=self.login,
            bg=BLUE,
            fg=WHITE,
            activebackground="#3D6330",
            activeforeground=WHITE,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 10, "bold")
        ).pack(fill="x", ipady=11)

        tk.Label(
            card,
            text="Mode demo • login belum terhubung ke Controller",
            bg=WHITE,
            fg="#8F998E",
            font=("Segoe UI", 8)
        ).pack(pady=(17, 0))

    def login(self):
        """Mode demo: lanjut tanpa memeriksa username atau password."""
        self.on_login()