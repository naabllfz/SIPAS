"""Aplikasi desktop pengajuan surat dengan navigasi antar-View."""
import tkinter as tk
from tkinter import ttk

from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.pengajuan_view import PengajuanView
from views.status_view import StatusView
from views.theme import BG, BLUE, NAVY, WHITE


class AplikasiPengajuanSurat(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SIPAS | Pengajuan Surat Mahasiswa")
        self.geometry("1240x790")
        self.minsize(980, 660)
        self.configure(bg=BG)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", rowheight=38, font=("Segoe UI", 9),
                        background=WHITE, fieldbackground=WHITE, foreground=NAVY,
                        borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", 8, "bold"),
                        background="#EBEDE4", foreground="#69786D",
                        relief="flat", padding=(10, 11))
        style.map("Treeview", background=[("selected", "#E6EDD9")],
                  foreground=[("selected", NAVY)])
        style.configure("TCombobox", padding=9, fieldbackground=WHITE,
                        background=WHITE, foreground=NAVY)
        self.content = None
        self.nav_buttons = {}
        self.show_login()

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear()
        LoginView(self, on_login=self.show_main).pack(fill="both", expand=True)

    def show_main(self):
        self.clear()
        shell = tk.Frame(self, bg=BG)
        shell.pack(fill="both", expand=True)

        sidebar = tk.Frame(shell, bg=NAVY, width=244)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        brand = tk.Frame(sidebar, bg=NAVY)
        brand.pack(fill="x", padx=22, pady=(27, 30))
        tk.Label(brand, text="S", bg=BLUE, fg=WHITE, width=2, height=1,
                 font=("Segoe UI", 16, "bold")).pack(side="left", padx=(0, 11))
        brand_text = tk.Frame(brand, bg=NAVY)
        brand_text.pack(side="left")
        tk.Label(brand_text, text="SIPAS", bg=NAVY, fg=WHITE,
                 font=("Segoe UI", 15, "bold")).pack(anchor="w")
        tk.Label(brand_text, text="LAYANAN AKADEMIK", bg=NAVY, fg="#A5B9A7",
                 font=("Segoe UI", 7, "bold")).pack(anchor="w", pady=(2, 0))

        tk.Label(sidebar, text="MENU UTAMA", bg=NAVY, fg="#93AA98",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=24, pady=(0, 9))
        for page, label in [
            ("dashboard", "⌂   Ringkasan"),
            ("pengajuan", "＋   Buat Pengajuan"),
            ("status", "◷   Status Pengajuan"),
        ]:
            button = tk.Button(
                sidebar, text=label, anchor="w", padx=16, pady=12,
                bg="#E5EBDD", fg="#173B35", activebackground="#D8E5CA",
                activeforeground="#173B35", relief="flat", bd=0,
                font=("Segoe UI", 10, "bold"), cursor="hand2",
                command=lambda p=page: self.navigate(p),
            )
            button.pack(fill="x", padx=12, pady=3)
            self.nav_buttons[page] = button

        foot = tk.Frame(sidebar, bg="#21483D", padx=13, pady=12)
        foot.pack(side="bottom", fill="x", padx=14, pady=17)
        tk.Label(foot, text="BUTUH BANTUAN?", bg="#21483D", fg="#D9E6D8",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        tk.Label(foot, text="Hubungi bagian administrasi akademik.",
                 bg="#21483D", fg="#A5B9A7", font=("Segoe UI",  8),
                 wraplength=185, justify="left").pack(anchor="w", pady=(5, 0))

        body = tk.Frame(shell, bg=BG)
        body.pack(side="left", fill="both", expand=True)
        topbar = tk.Frame(body, bg=WHITE, height=66,
                          highlightbackground="#E6E7DC", highlightthickness=1)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        tk.Label(topbar, text="Portal Mahasiswa  /  Pengajuan Surat", bg=WHITE,
                 fg="#78857A", font=("Segoe UI", 9)).pack(side="left", padx=27)
        account = tk.Frame(topbar, bg=WHITE)
        account.pack(side="right", padx=24)
        tk.Label(account, text="NP", bg="#E8EFDF", fg=BLUE, width=2, height=1,
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 9))
        identity = tk.Frame(account, bg=WHITE)
        identity.pack(side="left")
        tk.Label(identity, text="Nabila Putri", bg=WHITE, fg=NAVY,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(identity, text="Mahasiswa", bg=WHITE, fg="#879187",
                 font=("Segoe UI", 8)).pack(anchor="w")
        tk.Button(account, text="⌄", command=self.show_login, bg=WHITE, fg="#78857A",
                  relief="flat", font=("Segoe UI", 12), cursor="hand2").pack(side="left", padx=(12, 0))

        self.content = tk.Frame(body, bg=BG)
        self.content.pack(fill="both", expand=True, padx=30, pady=25)
        self.navigate("dashboard")

    def navigate(self, page):
        if self.content is None:
            return
        for key, button in self.nav_buttons.items():
            selected = key == page
            button.configure(
                bg="#C8E879" if selected else "#E5EBDD",
                fg="#173B35",
                activebackground="#B8D966" if selected else "#D8E5CA",
                activeforeground="#173B35",
            )
        for child in self.content.winfo_children():
            child.destroy()
        pages = {
            "dashboard": DashboardView,
            "pengajuan": PengajuanView,
            "status": StatusView,
        }
        pages[page](self.content, on_navigate=self.navigate).pack(fill="both", expand=True)


if __name__ == "__main__":
    AplikasiPengajuanSurat().mainloop()
