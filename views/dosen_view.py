import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime
from PIL import Image, ImageTk

from controllers.dosen_controller import DosenController
from views.surat_preview_dialog import SuratPreviewDialog
from views.theme import (
    BG, WHITE, NAVY, BLUE, BLUE_DARK, MUTED, LINE,
    GREEN, PALE_GREEN, AMBER, PALE_AMBER, RED, PALE_RED,
    page_heading, panel, primary_button, secondary_button
)


class DosenView(tk.Frame):
    """
    Halaman Dosen untuk memantau surat masuk dari mahasiswa,
    mengunggah gambar tanda tangan asli, dan mengesahkan surat.
    """

    def __init__(self, master, page="dashboard", id_dosen=1, on_navigate=None):
        super().__init__(master, bg=BG)
        self.page = page
        self.id_dosen = id_dosen
        self.on_navigate = on_navigate
        self.controller = DosenController(self.id_dosen)

        self.dosen = None
        self.daftar_surat = []
        self.surat_terpilih = None
        self.error_message = None
        self.ttd_preview_img = None  # Menjaga referensi PhotoImage agar tidak ter-garbage-collect

        self.muat_profil_dosen()
        self.muat_data_surat()

        if self.page == "surat_masuk":
            self.show_surat_masuk()
        elif self.page == "riwayat":
            self.show_riwayat()
        elif self.page == "profil":
            self.show_profil()
        else:
            self.show_dashboard()

    def muat_profil_dosen(self):
        self.dosen = self.controller.get_profil_dosen()

    def muat_data_surat(self):
        try:
            self.daftar_surat = self.controller.get_daftar_surat()
            self.error_message = None
        except Exception as error:
            self.daftar_surat = []
            self.error_message = str(error)

    @staticmethod
    def format_date(value):
        if value is None:
            return "-"
        if hasattr(value, "strftime"):
            return value.strftime("%d %b %Y")
        try:
            return datetime.strptime(str(value)[:19], "%Y-%m-%d %H:%M:%S").strftime("%d %b %Y")
        except Exception:
            return str(value)

    @staticmethod
    def format_datetime(value):
        if value is None:
            return "-"
        if hasattr(value, "strftime"):
            return value.strftime("%d %b %Y %H:%M")
        try:
            return datetime.strptime(str(value)[:19], "%Y-%m-%d %H:%M:%S").strftime("%d %b %Y %H:%M")
        except Exception:
            return str(value)

    def show_database_error(self):
        notice = tk.Frame(self, bg=PALE_AMBER, padx=14, pady=10)
        notice.pack(fill="x", pady=(0, 14))
        tk.Label(
            notice,
            text=f"Koneksi database terkendala: {self.error_message}.",
            bg=PALE_AMBER,
            fg="#805226",
            font=("Segoe UI", 9)
        ).pack(anchor="w")

    # ==========================================
    # 1. DASHBOARD DOSEN
    # ==========================================
    def show_dashboard(self):
        page_heading(
            self,
            "Area Dosen",
            "Dashboard Dosen",
            "Pantau pengajuan surat mahasiswa dan verifikasi tanda tangan digital & tanda tangan asli."
        )

        if self.error_message:
            self.show_database_error()

        banner = tk.Frame(
            self,
            bg=NAVY,
            padx=22,
            pady=16,
            highlightbackground="#234E43",
            highlightthickness=1
        )
        banner.pack(fill="x", pady=(0, 18))

        b_left = tk.Frame(banner, bg=NAVY)
        b_left.pack(side="left")

        nama = self.dosen.get("nama_dosen", "Dosen Pembimbing")
        jabatan = self.dosen.get("jabatan", "Dosen Wali")
        nidn = self.dosen.get("nidn") or self.dosen.get("nip") or "-"
        ada_ttd = self.controller.cek_specimen_ttd_siap(self.dosen)
        status_ttd_txt = "TERUNGGAH (SIAP PAKAI)" if ada_ttd else "BELUM DIUNGGAH"

        tk.Label(
            b_left,
            text=f"Selamat Datang, {nama}",
            bg=NAVY,
            fg=WHITE,
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w")

        tk.Label(
            b_left,
            text=f"NIDN: {nidn}  •  {jabatan}  •  Speciment TTD Asli: {status_ttd_txt}",
            bg=NAVY,
            fg="#B9CEBC",
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(3, 0))

        if self.on_navigate:
            tk.Button(
                banner,
                text="Tinjau Surat Masuk  →",
                command=lambda: self.on_navigate("dosen_surat_masuk"),
                bg=BLUE,
                fg=WHITE,
                activebackground=BLUE_DARK,
                activeforeground=WHITE,
                relief="flat",
                font=("Segoe UI", 9, "bold"),
                padx=14,
                pady=7,
                cursor="hand2"
            ).pack(side="right")

        # Stat cards
        cards = tk.Frame(self, bg=BG)
        cards.pack(fill="x", pady=(0, 18))

        stats = self.controller.hitung_statistik(self.daftar_surat)
        stat_items = [
            ("Total Surat Masuk", str(stats["total"]), BLUE),
            ("Perlu Persetujuan & TTD", str(stats["menunggu"]), AMBER),
            ("Telah Ditandatangani", str(stats["disetujui"]), GREEN),
            ("Ditolak", str(stats["ditolak"]), RED),
        ]

        for title, val, col in stat_items:
            self.create_stat_card(cards, title, val, col)

        # Tabel Surat Masuk Terbaru
        box = panel(self, 20, 17)
        box.pack(fill="both", expand=True)

        header_box = tk.Frame(box, bg=WHITE)
        header_box.pack(fill="x", pady=(0, 12))

        tk.Label(
            header_box,
            text="Surat Masuk Terbaru",
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")

        if self.on_navigate:
            tk.Button(
                header_box,
                text="Lihat Semua Surat  →",
                command=lambda: self.on_navigate("dosen_surat_masuk"),
                bg=WHITE,
                fg=BLUE,
                relief="flat",
                font=("Segoe UI", 9, "bold"),
                cursor="hand2"
            ).pack(side="right")

        cols = ("nomor", "mahasiswa", "jenis", "tanggal", "status")
        headings = ("NOMOR", "MAHASISWA", "JENIS SURAT", "TANGGAL PENGAJUAN", "STATUS TTD")

        table = ttk.Treeview(box, columns=cols, show="headings", height=7)
        col_widths = {"nomor": 90, "mahasiswa": 180, "jenis": 260, "tanggal": 130, "status": 160}
        for c, h in zip(cols, headings):
            table.heading(c, text=h)
            table.column(c, width=col_widths.get(c, 140), anchor="w")

        table.pack(fill="both", expand=True)

        for row in self.daftar_surat[:7]:
            st = str(row.get("status") or "Diajukan")
            if st in ("Disetujui", "Selesai"):
                st_text = "✓ Ditandatangani"
            elif st == "Ditolak":
                st_text = "✕ Ditolak"
            else:
                st_text = "⏳ Menunggu TTD"

            table.insert("", "end", values=(
                row.get("nomor_pengajuan", "-"),
                row.get("nama", "-"),
                row.get("jenis_surat") or row.get("nama_jenis", "-"),
                self.format_date(row.get("tanggal_pengajuan")),
                st_text
            ))

    def create_stat_card(self, parent, title, value, accent):
        card = tk.Frame(
            parent, bg=WHITE, padx=16, pady=16,
            highlightbackground=LINE, highlightthickness=1
        )
        card.pack(side="left", fill="x", expand=True, padx=(0, 11))
        tk.Label(
            card, text=title.upper(), bg=WHITE, fg=MUTED,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")
        tk.Label(
            card, text=value, bg=WHITE, fg=accent,
            font=("Segoe UI", 25, "bold")
        ).pack(anchor="w", pady=(8, 0))

    # ==========================================
    # 2. KELOLA SURAT MASUK & TTD
    # ==========================================
    def show_surat_masuk(self):
        page_heading(
            self,
            "Verifikasi Akademik",
            "Surat Masuk & Tanda Tangan",
            "Tinjau permohonan surat mahasiswa dan bubuhkan tanda tangan resmi Anda."
        )

        if self.error_message:
            self.show_database_error()

        box = panel(self, 20, 17)
        box.pack(fill="both", expand=True)

        toolbar = tk.Frame(box, bg=WHITE)
        toolbar.pack(fill="x", pady=(0, 12))

        tk.Label(
            toolbar,
            text=f"Daftar Surat Masuk ({len(self.daftar_surat)})",
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")

        self.filter_var = tk.StringVar(value="Semua status")
        self.filter_cb = ttk.Combobox(
            toolbar,
            textvariable=self.filter_var,
            state="readonly",
            width=20,
            values=["Semua status", "Menunggu Persetujuan", "Telah Ditandatangani", "Ditolak"]
        )
        self.filter_cb.pack(side="right", padx=(8, 0))
        self.filter_cb.bind("<<ComboboxSelected>>", self.filter_data)

        self.search_hint = "Cari nomor, mahasiswa, NIM, atau jenis surat..."
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
        search_entry.pack(side="right", fill="x", expand=True, padx=10, ipady=6)
        search_entry.bind("<FocusIn>", self.on_search_focus_in)
        search_entry.bind("<FocusOut>", self.on_search_focus_out)
        search_entry.bind("<KeyRelease>", self.filter_data)

        cols = ("id", "nomor", "mahasiswa", "nim", "jenis", "tanggal", "status", "ttd_digital")
        headings = (
            "ID", "NOMOR", "MAHASISWA", "NIM",
            "JENIS SURAT", "TANGGAL", "STATUS TTD", "KODE VERIFIKASI"
        )

        self.table = ttk.Treeview(box, columns=cols, show="headings", height=6)
        col_widths = {
            "id": 45,
            "nomor": 75,
            "mahasiswa": 150,
            "nim": 110,
            "jenis": 210,
            "tanggal": 105,
            "status": 130,
            "ttd_digital": 170
        }
        for c, h in zip(cols, headings):
            self.table.heading(c, text=h)
            self.table.column(c, width=col_widths.get(c, 120), anchor="w")

        self.table.pack(fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self.pilih_pengajuan)

        self.isi_tabel(self.daftar_surat)

        # Panel Detail
        self.detail_card = tk.Frame(
            box,
            bg="#F9FAF5",
            padx=18,
            pady=14,
            highlightbackground=LINE,
            highlightthickness=1
        )
        self.detail_card.pack(fill="x", pady=(14, 0))

        d_top = tk.Frame(self.detail_card, bg="#F9FAF5")
        d_top.pack(fill="x", pady=(0, 8))

        self.lbl_detail_judul = tk.Label(
            d_top,
            text="DETAIL SURAT TERPILIH",
            bg="#F9FAF5",
            fg=BLUE,
            font=("Segoe UI", 9, "bold")
        )
        self.lbl_detail_judul.pack(side="left")

        self.badge_status = tk.Label(
            d_top,
            text="PILIH SATU SURAT DARI TABEL",
            bg="#EAECE4",
            fg=MUTED,
            font=("Segoe UI", 8, "bold"),
            padx=8,
            pady=3
        )
        self.badge_status.pack(side="right")

        self.info_grid = tk.Frame(self.detail_card, bg="#F9FAF5")
        self.info_grid.pack(fill="x", pady=(0, 8))

        self.lbl_info_mhs = tk.Label(
            self.info_grid,
            text="Silakan klik pada salah satu pengajuan surat di tabel atas untuk meninjau berkas.",
            bg="#F9FAF5",
            fg=NAVY,
            font=("Segoe UI", 9),
            justify="left"
        )
        self.lbl_info_mhs.pack(anchor="w")

        catatan_row = tk.Frame(self.detail_card, bg="#F9FAF5")
        catatan_row.pack(fill="x", pady=(6, 10))

        tk.Label(
            catatan_row,
            text="Catatan Dosen / Rekomendasi:",
            bg="#F9FAF5",
            fg=NAVY,
            font=("Segoe UI", 9, "bold")
        ).pack(side="left", padx=(0, 10))

        self.entry_catatan = tk.Entry(
            catatan_row,
            font=("Segoe UI", 9),
            relief="solid",
            bd=1,
            highlightbackground=LINE,
            highlightcolor=BLUE,
            fg=NAVY
        )
        self.entry_catatan.pack(side="left", fill="x", expand=True, ipady=5)
        self.entry_catatan.insert(
            0,
            "Disetujui dan ditandatangani oleh dosen pembimbing/wali."
        )

        self.action_bar = tk.Frame(self.detail_card, bg="#F9FAF5")
        self.action_bar.pack(fill="x")

        self.btn_preview = secondary_button(
            self.action_bar,
            "👁 Pratinjau Surat & TTD",
            self.buka_pratinjau,
            padx=13,
            pady=8
        )
        self.btn_preview.pack(side="left")

        self.btn_tolak = tk.Button(
            self.action_bar,
            text="✕ Tolak Surat",
            command=self.tolak_surat,
            bg="#FFF2F1",
            fg=RED,
            activebackground="#FADAD8",
            activeforeground=RED,
            relief="solid",
            bd=1,
            font=("Segoe UI", 9, "bold"),
            padx=14,
            pady=8,
            cursor="hand2"
        )
        self.btn_tolak.pack(side="right", padx=(8, 0))

        self.btn_approve = primary_button(
            self.action_bar,
            "✓ Setujui & Bubuhkan Tanda Tangan",
            self.approve_dan_ttd_digital,
            padx=18,
            pady=8
        )
        self.btn_approve.pack(side="right")

    def on_search_focus_in(self, _event=None):
        if self.search_var.get() == self.search_hint:
            self.search_var.set("")

    def on_search_focus_out(self, _event=None):
        if not self.search_var.get().strip():
            self.search_var.set(self.search_hint)
            self.filter_data()

    def filter_data(self, _event=None):
        query = self.search_var.get().strip()
        if query.lower() == self.search_hint.lower():
            query = ""

        hasil = self.controller.filter_surat(
            self.daftar_surat,
            keyword=query,
            status_filter=self.filter_var.get()
        )
        self.isi_tabel(hasil)

    def isi_tabel(self, rows):
        self.table.delete(*self.table.get_children())
        for row in rows:
            st = str(row.get("status") or "Diajukan")
            if st in ("Disetujui", "Selesai"):
                st_text = "✓ Ditandatangani"
            elif st == "Ditolak":
                st_text = "✕ Ditolak"
            else:
                st_text = "⏳ Menunggu TTD"

            ttd = (row.get("tanda_tangan_digital") or "—")[:18]

            self.table.insert("", "end", iid=str(row.get("id_pengajuan")), values=(
                row.get("id_pengajuan"),
                row.get("nomor_pengajuan", "-"),
                row.get("nama", "-"),
                row.get("nim", "-"),
                row.get("jenis_surat") or row.get("nama_jenis", "-"),
                self.format_date(row.get("tanggal_pengajuan")),
                st_text,
                ttd
            ))

    def pilih_pengajuan(self, _event=None):
        selected = self.table.selection()
        if not selected:
            return

        id_pengajuan = selected[0]
        self.surat_terpilih = next(
            (s for s in self.daftar_surat if str(s.get("id_pengajuan")) == str(id_pengajuan)),
            None
        )
        if not self.surat_terpilih:
            return

        s = self.surat_terpilih
        nomor = s.get("nomor_pengajuan", "-")
        nama = s.get("nama", "-")
        nim = s.get("nim", "-")
        prodi = s.get("prodi", "Sistem Informasi")
        jenis = s.get("jenis_surat") or s.get("nama_jenis", "-")
        tgl = self.format_date(s.get("tanggal_pengajuan"))
        keperluan = s.get("keperluan") or "Pengajuan surat akademik"
        st = str(s.get("status") or "Diajukan")
        ttd = s.get("tanda_tangan_digital")
        tgl_disetujui = self.format_datetime(s.get("tanggal_keputusan_dosen") or s.get("tanggal_disetujui"))

        self.lbl_detail_judul.configure(text=f"SURAT #{nomor} — {nama} ({nim})")

        if st in ("Disetujui", "Selesai"):
            self.badge_status.configure(
                text="✓ TELAH DITANDATANGANI",
                bg=PALE_GREEN,
                fg=GREEN
            )
        elif st == "Ditolak":
            self.badge_status.configure(
                text="✕ PENGAJUAN DITOLAK",
                bg=PALE_RED,
                fg=RED
            )
        else:
            self.badge_status.configure(
                text="⏳ MENUNGGU PERSETUJUAN & TTD DOSEN",
                bg=PALE_AMBER,
                fg=AMBER
            )

        info_text = (
            f"Jenis Surat: {jenis}   |   Program Studi: {prodi}   |   Tanggal Masuk: {tgl}\n"
            f"Keperluan: {keperluan}\n"
        )
        if ttd:
            info_text += f"Hash Verifikasi: {ttd[:24]}...   (Disahkan pada: {tgl_disetujui})"

        self.lbl_info_mhs.configure(text=info_text)

        catatan_ada = s.get("catatan_dosen")
        self.entry_catatan.delete(0, "end")
        self.entry_catatan.insert(
            0,
            catatan_ada if catatan_ada else "Disetujui dan ditandatangani oleh dosen pembimbing/wali."
        )

    def approve_dan_ttd_digital(self):
        """
        Menyetujui surat dan membubuhkan gambar tanda tangan asli dosen + hash SHA-256.
        """
        if not self.surat_terpilih:
            messagebox.showwarning(
                "Pilih Surat",
                "Silakan pilih satu permohonan surat pada tabel terlebih dahulu."
            )
            return

        # Cek apakah dosen sudah mengunggah gambar TTD aslinya
        if not self.controller.cek_specimen_ttd_siap(self.dosen):
            jawab = messagebox.askyesno(
                "Gambar Tanda Tangan Belum Diunggah",
                "Anda belum mengunggah gambar tanda tangan asli Anda.\n\n"
                "Apakah Anda ingin mengunggah file tanda tangan (PNG/JPG) sekarang sebelum menandatangani surat?"
            )
            if jawab:
                self.unggah_ttd_dosen()
                if not self.controller.cek_specimen_ttd_siap(self.dosen):
                    return
            else:
                return

        file_ttd_dosen = self.dosen.get("file_ttd")
        s = self.surat_terpilih
        nomor = s.get("nomor_pengajuan")
        nama = s.get("nama")
        id_pengajuan = s.get("id_pengajuan")

        catatan = self.entry_catatan.get().strip() or "Disetujui dan ditandatangani oleh dosen pembimbing/wali."

        tanya = messagebox.askyesno(
            "Konfirmasi Pengesahan & TTD",
            f"Bubuhkan tanda tangan asli Anda pada surat berikut?\n\n"
            f"• Nomor Surat : #{nomor}\n"
            f"• Mahasiswa   : {nama} ({s.get('nim')})\n"
            f"• Jenis Surat : {s.get('jenis_surat') or s.get('nama_jenis')}\n"
            f"• File TTD    : {os.path.basename(file_ttd_dosen)}",
            icon="question"
        )
        if not tanya:
            return

        sukses, hasil = self.controller.setujui_dan_ttd(id_pengajuan, catatan)
        if not sukses:
            messagebox.showerror(
                "Gagal Menandatangani",
                f"Terjadi kesalahan saat memproses tanda tangan: {hasil}"
            )
            return

        self.muat_data_surat()
        self.filter_data()

        self.surat_terpilih = next(
            (item for item in self.daftar_surat if str(item.get("id_pengajuan")) == str(id_pengajuan)),
            None
        )

        messagebox.showinfo(
            "Surat Berhasil Ditandatangani",
            f"Surat #{nomor} telah disetujui dan dibubuhi tanda tangan asli Anda!\n\n"
            f"Kode Verifikasi SHA-256:\n{hasil['tanda_tangan_digital'][:28]}..."
        )

        self.buka_pratinjau()

    def tolak_surat(self):
        if not self.surat_terpilih:
            messagebox.showwarning("Pilih Surat", "Silakan pilih satu permohonan surat pada tabel terlebih dahulu.")
            return

        s = self.surat_terpilih
        nomor = s.get("nomor_pengajuan")
        nama = s.get("nama")
        id_pengajuan = s.get("id_pengajuan")

        alasan = simpledialog.askstring(
            "Alasan Penolakan",
            f"Masukkan alasan/catatan penolakan surat #{nomor} ({nama}):",
            initialvalue="Berkas persyaratan belum lengkap atau tidak sesuai ketentuan."
        )
        if not alasan or not alasan.strip():
            return

        sukses, pesan = self.controller.tolak_surat(id_pengajuan, alasan)
        if not sukses:
            messagebox.showerror("Gagal Memproses", pesan)
            return

        self.muat_data_surat()
        self.filter_data()
        messagebox.showinfo("Surat Ditolak", f"Surat #{nomor} telah ditolak.")

    def buka_pratinjau(self):
        if not self.surat_terpilih:
            messagebox.showwarning("Pilih Surat", "Silakan pilih satu permohonan surat pada tabel terlebih dahulu.")
            return

        data = self.controller.lengkapi_data_preview(self.surat_terpilih, self.dosen)
        SuratPreviewDialog(self, data)

    # ==========================================
    # 3. RIWAYAT TANDA TANGAN
    # ==========================================
    def show_riwayat(self):
        page_heading(
            self,
            "Arsip Digital",
            "Riwayat Tanda Tangan",
            "Daftar seluruh surat yang telah Anda sahkan dan tandatangani."
        )

        if self.error_message:
            self.show_database_error()

        box = panel(self, 20, 17)
        box.pack(fill="both", expand=True)

        surat_sah = [
            s for s in self.daftar_surat
            if str(s.get("status") or "") in ("Disetujui", "Selesai")
        ]

        header = tk.Frame(box, bg=WHITE)
        header.pack(fill="x", pady=(0, 14))

        tk.Label(
            header,
            text=f"{len(surat_sah)} dokumen telah ditandatangani",
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")

        primary_button(
            header,
            "👁 Buka Pratinjau Dokumen Bertanda Tangan",
            self.buka_pratinjau_riwayat
        ).pack(side="right")

        cols = ("nomor", "mahasiswa", "nim", "jenis", "tanggal_ttd", "kode_ttd")
        headings = (
            "NO. PENGAJUAN", "MAHASISWA", "NIM",
            "JENIS SURAT", "WAKTU TTD", "HASH VERIFIKASI"
        )

        self.table_riwayat = ttk.Treeview(box, columns=cols, show="headings", height=8)
        widths = {"nomor": 110, "mahasiswa": 170, "nim": 120, "jenis": 230, "tanggal_ttd": 140, "kode_ttd": 220}
        for c, h in zip(cols, headings):
            self.table_riwayat.heading(c, text=h)
            self.table_riwayat.column(c, width=widths.get(c, 140), anchor="w")

        self.table_riwayat.pack(fill="both", expand=True)

        for row in surat_sah:
            self.table_riwayat.insert("", "end", iid=str(row.get("id_pengajuan")), values=(
                row.get("nomor_pengajuan", "-"),
                row.get("nama", "-"),
                row.get("nim", "-"),
                row.get("jenis_surat") or row.get("nama_jenis", "-"),
                self.format_datetime(row.get("tanggal_keputusan_dosen") or row.get("tanggal_pengajuan")),
                (row.get("tanda_tangan_digital") or "-")[:24]
            ))

    def buka_pratinjau_riwayat(self):
        selected = self.table_riwayat.selection()
        if not selected:
            messagebox.showwarning("Pilih Dokumen", "Pilih satu dokumen pada tabel riwayat.")
            return

        id_pengajuan = selected[0]
        surat = next((s for s in self.daftar_surat if str(s.get("id_pengajuan")) == str(id_pengajuan)), None)
        if surat:
            data = self.controller.lengkapi_data_preview(surat, self.dosen)
            SuratPreviewDialog(self, data)

    # ==========================================
    # 4. PROFIL DOSEN & UPLOAD SPECIMENT TTD ASLI
    # ==========================================
    def unggah_ttd_dosen(self):
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Pilih Gambar Tanda Tangan Asli (Disarankan PNG Transparan)",
            filetypes=[
                ("Gambar Tanda Tangan", "*.png *.jpg *.jpeg *.PNG *.JPG *.JPEG"),
                ("PNG Transparan", "*.png *.PNG"),
                ("JPG", "*.jpg *.jpeg *.JPG *.JPEG")
            ]
        )
        if not file_path:
            return

        sukses, hasil = self.controller.unggah_specimen_ttd(file_path)
        if not sukses:
            messagebox.showerror("Gagal Mengunggah TTD", hasil)
            return

        self.dosen["file_ttd"] = hasil
        messagebox.showinfo(
            "Tanda Tangan Tersimpan",
            "Gambar tanda tangan asli Anda berhasil diunggah dan siap digunakan untuk pengesahan surat."
        )
        if self.page == "profil":
            self.tampilkan_preview_ttd_profil()

    def tampilkan_preview_ttd_profil(self):
        if not hasattr(self, "lbl_gambar_ttd"):
            return

        path_ttd = self.dosen.get("file_ttd")
        if path_ttd and os.path.exists(path_ttd):
            try:
                img = Image.open(path_ttd)
                img.thumbnail((220, 100), Image.Resampling.LANCZOS)
                self.ttd_preview_img = ImageTk.PhotoImage(img)
                self.lbl_gambar_ttd.configure(image=self.ttd_preview_img, text="")
            except Exception as e:
                self.lbl_gambar_ttd.configure(image="", text=f"Gagal memuat gambar: {e}")
        else:
            self.lbl_gambar_ttd.configure(
                image="",
                text="Belum ada gambar TTD.\nKlik tombol di bawah untuk mengunggah."
            )

    def show_profil(self):
        page_heading(
            self,
            "Pengaturan & Pengesahan",
            "Profil & Speciment Tanda Tangan Asli",
            "Unggah gambar tanda tangan asli Anda untuk dibubuhkan secara otomatis pada surat mahasiswa."
        )

        layout = tk.Frame(self, bg=BG)
        layout.pack(fill="both", expand=True)

        # Kartu Kiri: Biodata Dosen
        card_kiri = panel(layout, 24, 22)
        card_kiri.pack(side="left", fill="both", expand=True, padx=(0, 16))

        tk.Label(
            card_kiri,
            text="Identitas Akademik Dosen",
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", pady=(0, 16))

        info_items = [
            ("Nama Lengkap & Gelar", self.dosen.get("nama_dosen", "-")),
            ("NIDN", self.dosen.get("nidn") or self.dosen.get("nip") or "-"),
            ("Jabatan Akademik", self.dosen.get("jabatan", "Dosen Wali")),
            ("Email Resmi", self.dosen.get("email") or "-"),
        ]

        for label, val in info_items:
            row = tk.Frame(card_kiri, bg=WHITE)
            row.pack(fill="x", pady=7)
            tk.Label(row, text=label, bg=WHITE, fg=MUTED, width=22, anchor="w", font=("Segoe UI", 9, "bold")).pack(side="left")
            tk.Label(row, text=f":  {val}", bg=WHITE, fg=NAVY, font=("Segoe UI", 10)).pack(side="left")

        tk.Frame(card_kiri, bg=LINE, height=1).pack(fill="x", pady=20)

        tk.Label(
            card_kiri,
            text="Panduan Penggunaan Tanda Tangan Asli:",
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(0, 8))

        tips = [
            "1. Gunakan gambar tanda tangan berlatar transparan (.PNG) atau putih bersih (.JPG).",
            "2. Gambar TTD akan tersimpan aman di profil Anda dan otomatis ditempel saat Anda menyetujui surat.",
            "3. Setiap surat yang disetujui tetap dilengkapi hash SHA-256 untuk mencegah pemalsuan dokumen."
        ]
        for tip in tips:
            tk.Label(
                card_kiri, text=tip, bg=WHITE, fg="#596D5E",
                font=("Segoe UI", 8), justify="left", wraplength=480
            ).pack(anchor="w", pady=2)

        # Kartu Kanan: Upload & Pratinjau TTD Asli
        card_kanan = panel(layout, 24, 22)
        card_kanan.configure(width=350)
        card_kanan.pack(side="right", fill="y")
        card_kanan.pack_propagate(False)

        tk.Label(
            card_kanan,
            text="SPECIMENT TANDA TANGAN ASLI",
            bg=WHITE,
            fg=BLUE,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")

        tk.Label(
            card_kanan,
            text="Pratinjau Tanda Tangan",
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 15, "bold")
        ).pack(anchor="w", pady=(4, 14))

        preview_box = tk.Frame(
            card_kanan,
            bg="#F8F9F4",
            height=130,
            highlightbackground=LINE,
            highlightthickness=1
        )
        preview_box.pack(fill="x", pady=(0, 14))
        preview_box.pack_propagate(False)

        self.lbl_gambar_ttd = tk.Label(
            preview_box,
            bg="#F8F9F4",
            fg=MUTED,
            font=("Segoe UI", 8),
            justify="center"
        )
        self.lbl_gambar_ttd.pack(expand=True, fill="both")
        self.tampilkan_preview_ttd_profil()

        primary_button(
            card_kanan,
            "📁 Unggah / Ganti Gambar TTD",
            self.unggah_ttd_dosen
        ).pack(fill="x", pady=(0, 10))

        if self.on_navigate:
            secondary_button(
                card_kanan,
                "Buka Surat Masuk  →",
                lambda: self.on_navigate("dosen_surat_masuk")
            ).pack(fill="x")