import tkinter as tk

from views.theme import BG, WHITE, NAVY, BLUE, MUTED, LINE, RED
from views.image_loader import load_logo_image


class LoginView(tk.Frame):
    def __init__(self, master, auth_controller, on_login_success, on_open_register=None):
        super().__init__(master, bg=BG)
        self.auth_controller = auth_controller
        self.on_login_success = on_login_success
        self.on_open_register = on_open_register

        # Panel Kiri (Visual & Informasi SIPAS)
        visual = tk.Frame(self, bg=NAVY, width=470)
        visual.pack(side="left", fill="y")
        visual.pack_propagate(False)

        logo_img = load_logo_image((64, 64))
        if logo_img:
            lbl_logo = tk.Label(visual, image=logo_img, bg=NAVY)
            lbl_logo.image = logo_img
            lbl_logo.pack(anchor="w", padx=54, pady=(42, 10))
        else:
            tk.Label(
                visual,
                text="S",
                bg=BLUE,
                fg=WHITE,
                width=2,
                height=1,
                font=("Segoe UI", 19, "bold")
            ).pack(anchor="w", padx=54, pady=(55, 10))

        tk.Label(
            visual,
            text="SIPAS",
            bg=NAVY,
            fg=WHITE,
            font=("Segoe UI", 26, "bold")
        ).pack(anchor="w", padx=54)

        tk.Label(
            visual,
            text="Layanan pengajuan surat akademik",
            bg=NAVY,
            fg="#B7CBB7",
            font=("Segoe UI", 11)
        ).pack(anchor="w", padx=56, pady=(5, 30))

        tk.Frame(visual, bg="#2D584A", height=1).pack(fill="x", padx=54, pady=(0, 22))

        fitur = [
            ("01", "Ajukan surat", "Isi permohonan akademik dengan mudah."),
            ("02", "Pantau proses", "Lihat perkembangan pengajuan kapan saja."),
            ("03", "Verifikasi dosen", "Tanda tangan asli & digital terverifikasi."),
            ("04", "Terima informasi", "Status resmi dan unduh surat PDF di satu tempat.")
        ]

        for nomor, judul, detail in fitur:
            row = tk.Frame(visual, bg=NAVY)
            row.pack(fill="x", padx=54, pady=10)

            tk.Label(
                row,
                text=nomor,
                bg="#2D584A",
                fg="#CFDFC1",
                width=4,
                pady=7,
                font=("Segoe UI", 9, "bold")
            ).pack(side="left", padx=(0, 13))

            text_frame = tk.Frame(row, bg=NAVY)
            text_frame.pack(side="left", fill="x", expand=True)

            tk.Label(
                text_frame,
                text=judul,
                bg=NAVY,
                fg=WHITE,
                font=("Segoe UI", 10, "bold")
            ).pack(anchor="w")

            tk.Label(
                text_frame,
                text=detail,
                bg=NAVY,
                fg="#B6C9B5",
                font=("Segoe UI", 8),
                wraplength=230,
                justify="left"
            ).pack(anchor="w", pady=(3, 0))

        tk.Label(
            visual,
            text="UNIVERSITAS TADULAKO  •  2026",
            bg=NAVY,
            fg="#8FA892",
            font=("Segoe UI", 8, "bold")
        ).pack(side="bottom", anchor="w", padx=54, pady=25)

        # Panel Kanan (Form Login)
        right = tk.Frame(self, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        card = tk.Frame(
            right,
            bg=WHITE,
            padx=42,
            pady=36,
            highlightbackground=LINE,
            highlightthickness=1
        )
        card.place(relx=0.5, rely=0.5, anchor="center", width=430)

        tk.Label(
            card,
            text="Masuk ke SIPAS",
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 22, "bold")
        ).pack(anchor="w")

        tk.Label(
            card,
            text="Gunakan akun Mahasiswa, Dosen, atau Admin yang terdaftar.",
            bg=WHITE,
            fg=MUTED,
            font=("Segoe UI", 9),
            wraplength=340,
            justify="left"
        ).pack(anchor="w", pady=(4, 22))

        # Input Username / NIM / NIDN
        tk.Label(
            card,
            text="Username / NIM / NIDN",
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(0, 5))

        self.var_username = tk.StringVar()
        self.entry_username = tk.Entry(
            card,
            textvariable=self.var_username,
            font=("Segoe UI", 10),
            bg="#F9FAF7",
            fg=NAVY,
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground=LINE,
            highlightcolor=BLUE
        )
        self.entry_username.pack(fill="x", ipady=8, pady=(0, 14))
        self.entry_username.focus_set()

        # Input Password
        tk.Label(
            card,
            text="Kata Sandi",
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(0, 5))

        pwd_wrap = tk.Frame(
            card,
            bg="#F9FAF7",
            highlightbackground=LINE,
            highlightthickness=1
        )
        pwd_wrap.pack(fill="x", pady=(0, 8))

        self.var_password = tk.StringVar()
        self.show_pwd = False
        self.entry_password = tk.Entry(
            pwd_wrap,
            textvariable=self.var_password,
            show="•",
            font=("Segoe UI", 10),
            bg="#F9FAF7",
            fg=NAVY,
            relief="flat",
            bd=0
        )
        self.entry_password.pack(side="left", fill="x", expand=True, padx=(10, 4), ipady=8)

        self.btn_toggle_pwd = tk.Button(
            pwd_wrap,
            text="Lihat",
            command=self.toggle_password,
            bg="#F9FAF7",
            fg=MUTED,
            activebackground="#F9FAF7",
            activeforeground=NAVY,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 8, "bold"),
            padx=10
        )
        self.btn_toggle_pwd.pack(side="right")

        # Label Error Validasi
        self.lbl_error = tk.Label(
            card,
            text="",
            bg=WHITE,
            fg=RED,
            font=("Segoe UI", 8, "bold"),
            wraplength=340,
            justify="left"
        )
        self.lbl_error.pack(anchor="w", pady=(2, 12))

        # Tombol Submit
        self.btn_submit = tk.Button(
            card,
            text="Masuk  →",
            command=self.handle_login,
            bg=BLUE,
            fg=WHITE,
            activebackground="#3D6330",
            activeforeground=WHITE,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 10, "bold")
        )
        self.btn_submit.pack(fill="x", ipady=11)
        if self.on_open_register:
            reg_wrap = tk.Frame(card, bg=WHITE)
            reg_wrap.pack(pady=(14, 0))

        tk.Label(
            reg_wrap,
            text="Belum punya akun mahasiswa?",
            bg=WHITE,
            fg=MUTED,
            font=("Segoe UI", 8)
        ).pack(side="left")

        tk.Button(
            reg_wrap,
            text="Daftar di sini",
            command=self.on_open_register,
            bg=WHITE,
            fg=BLUE,
            activebackground=WHITE,
            activeforeground=NAVY,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 8, "bold")
        ).pack(side="left", padx=(4, 0))

        tk.Label(
            card,
            text="Sistem otomatis mengarahkan ke dashboard sesuai peran akun Anda.",
            bg=WHITE,
            fg="#8F998E",
            font=("Segoe UI", 8),
            wraplength=340,
            justify="center"
        ).pack(pady=(16, 0))

        # Tekan Enter untuk login
        self.entry_username.bind("<Return>", lambda _e: self.entry_password.focus_set())
        self.entry_password.bind("<Return>", lambda _e: self.handle_login())

    def toggle_password(self):
        self.show_pwd = not self.show_pwd
        self.entry_password.configure(show="" if self.show_pwd else "•")
        self.btn_toggle_pwd.configure(text="Tutup" if self.show_pwd else "Lihat")

    def handle_login(self):
        username = self.var_username.get()
        password = self.var_password.get()

        self.lbl_error.configure(text="")
        self.btn_submit.configure(state="disabled", text="Memverifikasi...")
        self.update_idletasks()

        sukses, hasil = self.auth_controller.proses_login(username, password)
        self.btn_submit.configure(state="normal", text="Masuk  →")

        if not sukses:
            self.lbl_error.configure(text=hasil)
            self.entry_password.delete(0, "end")
            self.entry_password.focus_set()
            return

        # Teruskan role & data user ke router utama (main.py)
        self.on_login_success(hasil["role"], hasil["user"])