import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

from controllers.mahasiswa_controller import MahasiswaController
from views.theme import (
    BG, WHITE, NAVY, BLUE, MUTED, LINE,
    page_heading, panel, primary_button, secondary_button
)


class PengajuanView(tk.Frame):
    def __init__(self, master, id_mahasiswa=1, on_navigate=None):
        super().__init__(master, bg=BG)
        self.id_mahasiswa = id_mahasiswa
        self.on_navigate = on_navigate
        self.controller = MahasiswaController(self.id_mahasiswa)

        self.mahasiswa = None
        self.list_jenis = []
        self.list_dosen = []
        self.riwayat_saya = []
        self.path_lampiran = None

        self.muat_data_master()
        self.setup_ui()

    def muat_data_master(self):
        try:
            data = self.controller.get_data_form_pengajuan()
            self.mahasiswa = data["profil"]
            self.list_jenis = data["jenis_surat"]
            self.list_dosen = data["dosen"]
            self.riwayat_saya = data["riwayat"]
        except Exception:
            self.mahasiswa = None
            self.list_jenis = []
            self.list_dosen = []
            self.riwayat_saya = []

    def muat_riwayat_saya(self):
        try:
            self.riwayat_saya = self.controller.get_riwayat_saja()
        except Exception:
            self.riwayat_saya = []

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

    def setup_ui(self):
        page_heading(
            self,
            "Layanan Akademik",
            "Buat Pengajuan Surat Baru",
            "Lengkapi formulir permohonan surat akademik dan lampirkan dokumen pendukung jika diperlukan."
        )

        layout = tk.Frame(self, bg=BG)
        layout.pack(fill="both", expand=True)

        # Panel Kiri: Form Pengajuan
        form_box = panel(layout, 22, 20)
        form_box.pack(side="left", fill="both", expand=True, padx=(0, 16))

        tk.Label(
            form_box,
            text="Formulir Permohonan Surat",
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 12))

        # Identitas Pemohon (Readonly sesuai akun login)
        nama_mhs = (self.mahasiswa or {}).get("nama", "Mahasiswa")
        nim_mhs = (self.mahasiswa or {}).get("nim", "-")
        prodi_mhs = (self.mahasiswa or {}).get("prodi", "Sistem Informasi")

        info_box = tk.Frame(form_box, bg="#F8FAF5", padx=12, pady=10, highlightbackground=LINE, highlightthickness=1)
        info_box.pack(fill="x", pady=(0, 14))

        tk.Label(
            info_box,
            text=f"Pemohon: {nama_mhs} ({nim_mhs})  •  Prodi {prodi_mhs}",
            bg="#F8FAF5",
            fg=NAVY,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w")

        # Pilih Jenis Surat
        tk.Label(form_box, text="Jenis Surat *", bg=WHITE, fg=NAVY, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))
        self.jenis_map = {
            (j.get("jenis_surat") or j.get("nama_jenis")): j
            for j in self.list_jenis
        }
        self.cb_jenis = ttk.Combobox(
            form_box,
            state="readonly",
            values=list(self.jenis_map.keys()),
            font=("Segoe UI", 9)
        )
        self.cb_jenis.pack(fill="x", ipady=4, pady=(0, 12))
        if self.jenis_map:
            self.cb_jenis.current(0)

        # Pilih Dosen Tujuan
        tk.Label(form_box, text="Dosen Pembimbing / Penandatangan *", bg=WHITE, fg=NAVY, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))
        self.dosen_map = {
            f"{d['nama_dosen']} — {d.get('jabatan') or 'Dosen'}": d
            for d in self.list_dosen
        }
        self.cb_dosen = ttk.Combobox(
            form_box,
            state="readonly",
            values=list(self.dosen_map.keys()),
            font=("Segoe UI", 9)
        )
        self.cb_dosen.pack(fill="x", ipady=4, pady=(0, 12))
        if self.dosen_map:
            self.cb_dosen.current(0)

        # Keterangan / Keperluan
        tk.Label(form_box, text="Keterangan / Keperluan *", bg=WHITE, fg=NAVY, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))
        self.txt_keperluan = tk.Text(
            form_box,
            height=4,
            font=("Segoe UI", 9),
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground=LINE
        )
        self.txt_keperluan.pack(fill="x", pady=(0, 12))

        # Lampiran Dokumen (Opsional)
        attach_box = tk.Frame(form_box, bg="#F8F8F0", padx=10, pady=8, highlightbackground=LINE, highlightthickness=1)
        attach_box.pack(fill="x", pady=(0, 16))

        self.btn_pilih_file = tk.Button(
            attach_box,
            text="＋  Tambahkan lampiran (Opsional)",
            command=self.pilih_lampiran,
            bg="#F8F8F0",
            fg=BLUE,
            activebackground="#EFEFE5",
            activeforeground=BLUE,
            font=("Segoe UI", 9, "bold"),
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            anchor="w"
        )
        self.btn_pilih_file.pack(side="left", fill="x", expand=True)

        self.btn_hapus_file = tk.Button(
            attach_box,
            text="✕ Hapus",
            command=self.hapus_lampiran,
            bg="#F8F8F0",
            fg="#B65C54",
            activebackground="#EFEFE5",
            activeforeground="#B65C54",
            font=("Segoe UI", 8, "bold"),
            bd=0,
            highlightthickness=0,
            cursor="hand2"
        )

        self.lbl_info_file = tk.Label(
            attach_box,
            text="PDF / JPG · maks. 5 MB",
            bg="#F8F8F0",
            fg=MUTED,
            font=("Segoe UI", 8)
        )
        self.lbl_info_file.pack(side="right", padx=(0, 4))

        # Tombol Aksi Form
        btn_row = tk.Frame(form_box, bg=WHITE)
        btn_row.pack(fill="x")

        primary_button(
            btn_row,
            "Kirim Pengajuan Surat  →",
            self.kirim_pengajuan,
            padx=18,
            pady=9
        ).pack(side="right")

        secondary_button(
            btn_row,
            "Reset Form",
            self.reset_form,
            padx=14,
            pady=9
        ).pack(side="right", padx=(0, 8))

        # Panel Kanan: Riwayat Pengajuan Milik Mahasiswa Login
        side_box = panel(layout, 20, 20)
        side_box.configure(width=380)
        side_box.pack(side="right", fill="y")
        side_box.pack_propagate(False)

        tk.Label(
            side_box,
            text="Riwayat Pengajuan Saya",
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            side_box,
            text="Daftar permohonan yang pernah Anda kirimkan.",
            bg=WHITE,
            fg=MUTED,
            font=("Segoe UI", 8)
        ).pack(anchor="w", pady=(0, 12))

        cols = ("nomor", "jenis", "status")
        self.table_riwayat = ttk.Treeview(side_box, columns=cols, show="headings", height=12)
        self.table_riwayat.heading("nomor", text="NO")
        self.table_riwayat.column("nomor", width=55, anchor="w")
        self.table_riwayat.heading("jenis", text="JENIS SURAT")
        self.table_riwayat.column("jenis", width=185, anchor="w")
        self.table_riwayat.heading("status", text="STATUS")
        self.table_riwayat.column("status", width=95, anchor="w")
        self.table_riwayat.pack(fill="both", expand=True, pady=(0, 12))

        self.isi_tabel_riwayat()

        if self.on_navigate:
            secondary_button(
                side_box,
                "Lihat Detail & Unduh Surat  →",
                lambda: self.on_navigate("status")
            ).pack(fill="x")

    def isi_tabel_riwayat(self):
        self.table_riwayat.delete(*self.table_riwayat.get_children())
        for row in self.riwayat_saya:
            self.table_riwayat.insert("", "end", values=(
                f"#{row.get('nomor_pengajuan', '-')}",
                row.get("jenis_surat") or row.get("nama_jenis", "-"),
                row.get("status") or "Diajukan"
            ))

    def pilih_lampiran(self):
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Pilih Dokumen Lampiran",
            filetypes=[
                ("Semua Dokumen", "*.pdf *.jpg *.jpeg *.png *.PDF *.JPG *.JPEG *.PNG"),
                ("File PDF", "*.pdf *.PDF"),
                ("Gambar", "*.jpg *.jpeg *.png *.JPG *.JPEG *.PNG")
            ]
        )
        if not file_path:
            return

        valid, hasil = self.controller.validasi_lampiran(file_path)
        if not valid:
            messagebox.showwarning("Lampiran Tidak Valid", hasil)
            return

        self.path_lampiran = file_path
        self.btn_pilih_file.configure(text=f"📄  {hasil['nama']}", fg="#2C4037")
        self.lbl_info_file.configure(text=hasil["ukuran"])
        self.btn_hapus_file.pack(side="right", padx=(6, 4))

    def hapus_lampiran(self):
        self.path_lampiran = None
        self.btn_pilih_file.configure(text="＋  Tambahkan lampiran (Opsional)", fg=BLUE)
        self.lbl_info_file.configure(text="PDF / JPG · maks. 5 MB")
        self.btn_hapus_file.pack_forget()

    def reset_form(self):
        if self.jenis_map:
            self.cb_jenis.current(0)
        if self.dosen_map:
            self.cb_dosen.current(0)
        self.txt_keperluan.delete("1.0", "end")
        self.hapus_lampiran()

    def kirim_pengajuan(self):
        jenis_obj = self.jenis_map.get(self.cb_jenis.get())
        dosen_obj = self.dosen_map.get(self.cb_dosen.get())
        keperluan = self.txt_keperluan.get("1.0", "end")

        sukses, hasil = self.controller.buat_pengajuan(
            id_jenis_surat=jenis_obj["id_jenis_surat"] if jenis_obj else None,
            id_dosen=dosen_obj["id_dosen"] if dosen_obj else None,
            keperluan=keperluan,
            path_lampiran=self.path_lampiran
        )

        if not sukses:
            messagebox.showwarning("Validasi Pengajuan", hasil)
            return

        self.reset_form()
        self.muat_riwayat_saya()
        self.isi_tabel_riwayat()

        messagebox.showinfo(
            "Pengajuan Terkirim",
            f"Permohonan surat #{hasil:03d} berhasil diajukan!\nAnda dapat memantau progresnya di halaman Status Pengajuan."
        )