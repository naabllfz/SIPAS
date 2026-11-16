import inspect
import tkinter as tk
from tkinter import ttk
from controllers.auth_controller import AuthController
from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.pengajuan_view import PengajuanView
from views.status_view import StatusView
from views.register_view import RegisterView
from views.admin_view import AdminView
from views.dosen_view import DosenView
from views.theme import BG, BLUE, NAVY, WHITE
from views.image_loader import set_window_icon, load_logo_image
from splash_sipas import show_splash


class AplikasiPengajuanSurat(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("SIPAS | Pengajuan Surat Mahasiswa & Verifikasi Dosen")
        self.geometry("1240x790")
        self.minsize(980, 660)
        self.configure(bg=BG)

        set_window_icon(self)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Treeview",
            rowheight=38,
            font=("Segoe UI", 9),
            background=WHITE,
            fieldbackground=WHITE,
            foreground=NAVY,
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 8, "bold"),
            background="#EBEDE4",
            foreground="#69786D",
            relief="flat",
            padding=(10, 11)
        )
        style.map(
            "Treeview",
            background=[("selected", "#E6EDD9")],
            foreground=[("selected", NAVY)]
        )
        style.configure(
            "TCombobox",
            padding=9,
            fieldbackground=WHITE,
            background=WHITE,
            foreground=NAVY
        )

        # Inisialisasi Controller Autentikasi
        self.auth_controller = AuthController()

        self.content = None
        self.nav_buttons = {}
        self.role = None

        # Data sesi akun yang sedang login
        self.id_mahasiswa = None
        self.mahasiswa = None

        self.id_dosen = None
        self.dosen = None

        self.id_admin = None
        self.admin = None

        self.show_login()

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear()

        self.auth_controller.logout()
        self.content = None
        self.nav_buttons = {}
        self.role = None
        self.id_mahasiswa = None
        self.mahasiswa = None
        self.id_dosen = None
        self.dosen = None
        self.id_admin = None
        self.admin = None

        LoginView(
            self,
            auth_controller=self.auth_controller,
            on_login_success=self.show_main,
            on_open_register=self.show_register
        ).pack(fill="both", expand=True)

    def show_register(self):
        self.clear()
        RegisterView(
            self,
            auth_controller=self.auth_controller,
            on_back_to_login=self.show_login
        ).pack(fill="both", expand=True)

    def show_main(self, role="mahasiswa", user_data=None):
        self.clear()

        self.content = None
        self.nav_buttons = {}
        self.role = role
        user_data = user_data or self.auth_controller.current_user or {}

        self.mahasiswa = None
        self.dosen = None
        self.admin = None

        # Data profil sudah disegarkan oleh AuthController saat login
        if self.role == "mahasiswa":
            self.id_mahasiswa = user_data.get("id_mahasiswa", 1)
            self.mahasiswa = user_data
        elif self.role == "dosen":
            self.id_dosen = user_data.get("id_dosen", 1)
            self.dosen = user_data
        elif self.role == "admin":
            self.id_admin = user_data.get("id_admin", 1)
            self.admin = user_data

        shell = tk.Frame(self, bg=BG)
        shell.pack(fill="both", expand=True)

        sidebar = tk.Frame(shell, bg=NAVY, width=244)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        brand = tk.Frame(sidebar, bg=NAVY)
        brand.pack(fill="x", padx=22, pady=(27, 30))

        sidebar_logo = load_logo_image((36, 36))
        if sidebar_logo:
            lbl_logo = tk.Label(brand, image=sidebar_logo, bg=NAVY)
            lbl_logo.image = sidebar_logo
            lbl_logo.pack(side="left", padx=(0, 11))
        else:
            tk.Label(
                brand,
                text="S",
                bg=BLUE,
                fg=WHITE,
                width=2,
                height=1,
                font=("Segoe UI", 16, "bold")
            ).pack(side="left", padx=(0, 11))

        brand_text = tk.Frame(brand, bg=NAVY)
        brand_text.pack(side="left")

        tk.Label(
            brand_text,
            text="SIPAS",
            bg=NAVY,
            fg=WHITE,
            font=("Segoe UI", 15, "bold")
        ).pack(anchor="w")

        tk.Label(
            brand_text,
            text="LAYANAN AKADEMIK",
            bg=NAVY,
            fg="#A5B9A7",
            font=("Segoe UI", 7, "bold")
        ).pack(anchor="w", pady=(2, 0))

        tk.Label(
            sidebar,
            text="MENU UTAMA",
            bg=NAVY,
            fg="#93AA98",
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", padx=24, pady=(0, 9))

        if self.role == "admin":
            menu = [
                ("admin_dashboard", "⌂   Dashboard Admin"),
                ("admin_queue", "▤   Kelola Pengajuan"),
                ("admin_mahasiswa", "♙   Data Mahasiswa"),
                ("admin_dosen", "🎓   Data Dosen"),
                ("admin_jenis_surat", "✉   Jenis Surat")
            ]
            nama_pengguna = (self.admin or {}).get("nama_admin", "Admin Jurusan")
            label_peran = "Administrator"
            inisial = "".join(
                bagian[0].upper()
                for bagian in nama_pengguna.split()[:2]
                if bagian
            ) or "AD"
            teks_portal = "Portal Admin  /  Pengajuan Surat"

        elif self.role == "dosen":
            menu = [
                ("dosen_dashboard", "⌂   Dashboard Dosen"),
                ("dosen_surat_masuk", "✉   Surat Masuk & TTD"),
                ("dosen_riwayat", "✓   Riwayat TTD Digital"),
                ("dosen_profil", "👤  Profil & Speciment TTD")
            ]
            if self.dosen:
                nama_pengguna = self.dosen.get("nama_dosen", "Dosen")
                label_peran = self.dosen.get("jabatan", "Dosen Wali / Pembimbing")
            else:
                nama_pengguna = "Dosen"
                label_peran = "Dosen Wali / Pembimbing"

            inisial = "".join(
                bagian[0].upper()
                for bagian in nama_pengguna.replace("Dr.", "").replace("Prof.", "").strip().split()[:2]
                if bagian
            ) or "DS"
            teks_portal = "Portal Dosen  /  Verifikasi & Tanda Tangan"

        else:
            menu = [
                ("dashboard", "⌂   Ringkasan"),
                ("pengajuan", "＋   Buat Pengajuan"),
                ("status", "◷   Status Pengajuan")
            ]

            if self.mahasiswa:
                nama_pengguna = self.mahasiswa.get(
                    "nama",
                    self.mahasiswa.get("nama_mahasiswa", "Mahasiswa")
                )
                nim_mhs = self.mahasiswa.get("nim", "")
                label_peran = f"Mahasiswa • {nim_mhs}" if nim_mhs else "Mahasiswa"
            else:
                nama_pengguna = "Mahasiswa"
                label_peran = "Mahasiswa"

            inisial = "".join(
                bagian[0].upper()
                for bagian in nama_pengguna.split()[:2]
                if bagian
            ) or "M"
            teks_portal = "Portal Mahasiswa  /  Pengajuan Surat"

        for page, label in menu:
            button = tk.Button(
                sidebar,
                text=label,
                anchor="w",
                padx=16,
                pady=12,
                bg="#E5EBDD",
                fg="#173B35",
                activebackground="#D8E5CA",
                activeforeground="#173B35",
                relief="flat",
                bd=0,
                font=("Segoe UI", 10, "bold"),
                cursor="hand2",
                command=lambda p=page: self.navigate(p)
            )
            button.pack(fill="x", padx=12, pady=3)
            self.nav_buttons[page] = button

        foot = tk.Frame(sidebar, bg="#21483D", padx=13, pady=12)
        foot.pack(side="bottom", fill="x", padx=14, pady=17)

        tk.Label(
            foot,
            text="UNIVERSITAS TADULAKO",
            bg="#21483D",
            fg="#D9E6D8",
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")

        tk.Label(
            foot,
            text="Sistem Informasi Pengajuan Surat & Verifikasi Tanda Tangan Dosen.",
            bg="#21483D",
            fg="#A5B9A7",
            font=("Segoe UI", 8),
            wraplength=185,
            justify="left"
        ).pack(anchor="w", pady=(5, 0))

        body = tk.Frame(shell, bg=BG)
        body.pack(side="left", fill="both", expand=True)

        topbar = tk.Frame(
            body,
            bg=WHITE,
            height=66,
            highlightbackground="#E6E7DC",
            highlightthickness=1
        )
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        tk.Label(
            topbar,
            text=teks_portal,
            bg=WHITE,
            fg="#78857A",
            font=("Segoe UI", 9)
        ).pack(side="left", padx=27)

        account = tk.Frame(topbar, bg=WHITE)
        account.pack(side="right", padx=24)

        tk.Label(
            account,
            text=inisial,
            bg="#E8EFDF",
            fg=BLUE,
            width=2,
            height=1,
            font=("Segoe UI", 9, "bold")
        ).pack(side="left", padx=(0, 9))

        identity = tk.Frame(account, bg=WHITE)
        identity.pack(side="left")

        tk.Label(
            identity,
            text=nama_pengguna,
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w")

        tk.Label(
            identity,
            text=label_peran,
            bg=WHITE,
            fg="#879187",
            font=("Segoe UI", 8)
        ).pack(anchor="w")

        tk.Button(
            account,
            text="Keluar",
            command=self.show_login,
            bg=WHITE,
            fg="#78857A",
            relief="flat",
            font=("Segoe UI", 9),
            cursor="hand2"
        ).pack(side="left", padx=(12, 0))

        self.content = tk.Frame(body, bg=BG)
        self.content.pack(fill="both", expand=True, padx=30, pady=25)

        if self.role == "admin":
            halaman_awal = "admin_dashboard"
        elif self.role == "dosen":
            halaman_awal = "dosen_dashboard"
        else:
            halaman_awal = "dashboard"

        self.navigate(halaman_awal)

    def _buat_view_mahasiswa(self, view_cls):
        """Meneruskan id_mahasiswa jika constructor view mendukungnya."""
        params = inspect.signature(view_cls.__init__).parameters
        kwargs = {"on_navigate": self.navigate}
        if "id_mahasiswa" in params:
            kwargs["id_mahasiswa"] = self.id_mahasiswa
        return view_cls(self.content, **kwargs)

    def navigate(self, page):
        if self.content is None:
            return

        for key, button in self.nav_buttons.items():
            if not button.winfo_exists():
                continue

            selected = key == page
            button.configure(
                bg="#C8E879" if selected else "#E5EBDD",
                fg="#173B35",
                activebackground="#B8D966" if selected else "#D8E5CA",
                activeforeground="#173B35",
                font=("Segoe UI", 10, "bold")
            )

        for child in self.content.winfo_children():
            child.destroy()

        if page.startswith("admin_"):
            mode = page[len("admin_"):]
            params = inspect.signature(AdminView.__init__).parameters
            kwargs = {"page": mode}
            if "id_admin" in params:
                kwargs["id_admin"] = self.id_admin
            AdminView(self.content, **kwargs).pack(
                fill="both",
                expand=True
            )
            return

        if page.startswith("dosen_"):
            mode = page[len("dosen_"):]
            DosenView(
                self.content,
                page=mode,
                id_dosen=self.id_dosen,
                on_navigate=self.navigate
            ).pack(fill="both", expand=True)
            return

        if page == "dashboard":
            self._buat_view_mahasiswa(DashboardView).pack(fill="both", expand=True)
            return

        if page == "pengajuan":
            self._buat_view_mahasiswa(PengajuanView).pack(fill="both", expand=True)
            return

        if page == "status":
            self._buat_view_mahasiswa(StatusView).pack(fill="both", expand=True)


if __name__ == "__main__":
    app = AplikasiPengajuanSurat()
    app.withdraw()  # Sembunyikan jendela utama selama splash screen berjalan

    def on_splash_finish():
        app.deiconify()
        app.lift()
        try:
            app.focus_force()
        except Exception:
            pass

    show_splash(app, on_done=on_splash_finish)
    app.mainloop()