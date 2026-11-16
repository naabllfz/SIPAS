import tkinter as tk
from tkinter import ttk, messagebox

from views.theme import BG, WHITE, NAVY, BLUE, MUTED, LINE, RED
from views.image_loader import load_logo_image


class RegisterView(tk.Frame):
    def __init__(self, master, auth_controller, on_back_to_login):
        super().__init__(master, bg=BG)
        self.auth_controller = auth_controller
        self.on_back_to_login = on_back_to_login

        # Panel Kiri (Visual & Informasi SIPAS — selaras dengan LoginView)
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
            text="Pendaftaran akun mandiri Mahasiswa",
            bg=NAVY,
            fg="#B7CBB7",
            font=("Segoe UI", 11)
        ).pack(anchor="w", padx=56, pady=(5, 30))

        tk.Frame(visual, bg="#2D584A", height=1).pack(fill="x", padx=54, pady=(0, 22))

        langkah = [
            ("01", "Isi identitas akademik", "Masukkan NIM, nama lengkap, dan program studi."),
            ("02", "Buat kredensial akun", "Tentukan username login dan kata sandi aman."),
            ("03", "Masuk ke portal", "Gunakan username atau NIM untuk mengajukan surat.")
        ]

        for nomor, judul, detail in langkah:
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

        # Panel Kanan (Form Registrasi 2 Kolom)
        right = tk.Frame(self, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        card = tk.Frame(
            right,
            bg=WHITE,
            padx=38,
            pady=30,
            highlightbackground=LINE,
            highlightthickness=1
        )
        card.place(relx=0.5, rely=0.5, anchor="center", width=620)

        tk.Label(
            card,
            text="Daftar Akun Mahasiswa",
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="w")

        tk.Label(
            card,
            text="Lengkapi data diri Anda untuk mulai mengajukan surat akademik.",
            bg=WHITE,
            fg=MUTED,
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(3, 18))

        grid = tk.Frame(card, bg=WHITE)
        grid.pack(fill="x")
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        # Kolom Kiri
        col_left = tk.Frame(grid, bg=WHITE)
        col_left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        self.var_nim = tk.StringVar()
        self.entry_nim = self._add_field(col_left, "NIM *", self.var_nim)
        self.entry_nim.focus_set()

        self.var_nama = tk.StringVar()
        self.entry_nama = self._add_field(col_left, "Nama Lengkap *", self.var_nama)

        tk.Label(
            col_left,
            text="Program Studi *",
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(0, 4))

        self.var_prodi = tk.StringVar(value="Sistem Informasi")
        self.cb_prodi = ttk.Combobox(
            col_left,
            textvariable=self.var_prodi,
            values=[
                "Sistem Informasi",
                "Teknik Informatika",
                "Teknik Sipil",
                "Teknik Mesin",
                "Teknik Elektro",
                "Arsitektur",
            ],
            font=("Segoe UI", 10)
        )
        self.cb_prodi.pack(fill="x", pady=(0, 12))

        self.var_email = tk.StringVar()
        self.entry_email = self._add_field(col_left, "Email (Opsional)", self.var_email)

        # Kolom Kanan
        col_right = tk.Frame(grid, bg=WHITE)
        col_right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        self.var_username = tk.StringVar()
        self.entry_username = self._add_field(col_right, "Username Login *", self.var_username)

        self.var_password = tk.StringVar()
        self.entry_password = self._add_field(col_right, "Kata Sandi *", self.var_password, show="•")

        self.var_konfirmasi = tk.StringVar()
        self.entry_konfirmasi = self._add_field(
            col_right, "Konfirmasi Kata Sandi *", self.var_konfirmasi, show="•"
        )

        self.show_pwd = False
        self.btn_toggle_pwd = tk.Button(
            col_right,
            text="Lihat Kata Sandi",
            command=self.toggle_password,
            bg=WHITE,
            fg=MUTED,
            activebackground=WHITE,
            activeforeground=NAVY,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 8, "bold")
        )
        self.btn_toggle_pwd.pack(anchor="w", pady=(0, 8))

        # Label Error Validasi
        self.lbl_error = tk.Label(
            card,
            text="",
            bg=WHITE,
            fg=RED,
            font=("Segoe UI", 8, "bold"),
            wraplength=540,
            justify="left"
        )
        self.lbl_error.pack(anchor="w", pady=(2, 10))

        # Tombol Submit & Kembali
        btn_row = tk.Frame(card, bg=WHITE)
        btn_row.pack(fill="x", pady=(4, 0))

        self.btn_submit = tk.Button(
            btn_row,
            text="Daftar Akun  →",
            command=self.handle_register,
            bg=BLUE,
            fg=WHITE,
            activebackground="#3D6330",
            activeforeground=WHITE,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            padx=22
        )
        self.btn_submit.pack(side="right", ipady=9)

        tk.Button(
            btn_row,
            text="←  Sudah punya akun? Masuk",
            command=self.on_back_to_login,
            bg=WHITE,
            fg=BLUE,
            activebackground=WHITE,
            activeforeground=NAVY,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 9, "bold")
        ).pack(side="left", ipady=9)

        self.entry_konfirmasi.bind("<Return>", lambda _e: self.handle_register())

    def _add_field(self, parent, label_text, variable, show=""):
        tk.Label(
            parent,
            text=label_text,
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(0, 4))

        ent = tk.Entry(
            parent,
            textvariable=variable,
            show=show,
            font=("Segoe UI", 10),
            bg="#F9FAF7",
            fg=NAVY,
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground=LINE,
            highlightcolor=BLUE
        )
        ent.pack(fill="x", ipady=7, pady=(0, 12))
        return ent

    def toggle_password(self):
        self.show_pwd = not self.show_pwd
        char = "" if self.show_pwd else "•"
        self.entry_password.configure(show=char)
        self.entry_konfirmasi.configure(show=char)
        self.btn_toggle_pwd.configure(
            text="Sembunyikan Kata Sandi" if self.show_pwd else "Lihat Kata Sandi"
        )

    def handle_register(self):
        self.lbl_error.configure(text="")
        self.btn_submit.configure(state="disabled", text="Mendaftarkan...")
        self.update_idletasks()

        sukses, hasil = self.auth_controller.proses_registrasi(
            nim=self.var_nim.get(),
            nama=self.var_nama.get(),
            prodi=self.var_prodi.get(),
            username=self.var_username.get(),
            password=self.var_password.get(),
            konfirmasi_password=self.var_konfirmasi.get(),
            email=self.var_email.get(),
        )
        self.btn_submit.configure(state="normal", text="Daftar Akun  →")

        if not sukses:
            self.lbl_error.configure(text=hasil)
            return

        messagebox.showinfo(
            "Registrasi Berhasil",
            f"Akun mahasiswa {hasil['nama']} ({hasil['nim']}) berhasil didaftarkan.\n"
            f"Silakan masuk menggunakan username '{hasil['username']}' atau NIM Anda."
        )
        self.on_back_to_login()