import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from controllers.admin_controller import AdminController
from views.surat_preview_dialog import SuratPreviewDialog
from views.theme import (
    BG, WHITE, NAVY, BLUE, MUTED, LINE,
    AMBER, GREEN, RED, PALE_AMBER,
    page_heading, panel, primary_button, secondary_button
)


class AdminView(tk.Frame):
    """Halaman admin untuk pengelolaan pengajuan dan data master."""

    def __init__(self, master, page="dashboard", id_admin=1):
        super().__init__(master, bg=BG)
        self.page = page
        self.id_admin = id_admin
        self.controller = AdminController(self.id_admin)

        self.raw_pengajuan = []
        self.pengajuan = []
        self.raw_mahasiswa = []
        self.mahasiswa = []
        self.raw_dosen = []
        self.dosen = []
        self.raw_jenis_surat = []
        self.jenis_surat = []
        self.error_message = None

        if page in ("dashboard", "queue"):
            self.load_pengajuan()
        elif page == "mahasiswa":
            self.load_mahasiswa()
        elif page == "dosen":
            self.load_dosen()
        elif page == "jenis_surat":
            self.load_jenis_surat()

        if page == "queue":
            self.show_queue()
        elif page == "mahasiswa":
            self.show_mahasiswa()
        elif page == "dosen":
            self.show_dosen()
        elif page == "jenis_surat":
            self.show_jenis_surat()
        else:
            self.show_dashboard()

    # =========================================================================
    # LOAD DATA MELALUI CONTROLLER
    # =========================================================================
    def load_pengajuan(self):
        try:
            self.raw_pengajuan, self.pengajuan = self.controller.get_daftar_pengajuan()
            self.error_message = None
        except Exception as error:
            self.raw_pengajuan = []
            self.pengajuan = []
            self.error_message = str(error)

    def load_mahasiswa(self):
        try:
            self.raw_mahasiswa, self.mahasiswa = self.controller.get_daftar_mahasiswa()
            self.error_message = None
        except Exception as error:
            self.raw_mahasiswa = []
            self.mahasiswa = []
            self.error_message = str(error)

    def load_dosen(self):
        try:
            self.raw_dosen, self.dosen = self.controller.get_daftar_dosen()
            self.error_message = None
        except Exception as error:
            self.raw_dosen = []
            self.dosen = []
            self.error_message = str(error)

    def load_jenis_surat(self):
        try:
            self.raw_jenis_surat, self.jenis_surat = self.controller.get_daftar_jenis_surat()
            self.error_message = None
        except Exception as error:
            self.raw_jenis_surat = []
            self.jenis_surat = []
            self.error_message = str(error)

    def show_database_error(self):
        notice = tk.Frame(self, bg=PALE_AMBER, padx=12, pady=9)
        notice.pack(fill="x", pady=(0, 12))
        tk.Label(
            notice,
            text=f"Data belum dapat dimuat: {self.error_message}",
            bg=PALE_AMBER,
            fg="#805226",
            font=("Segoe UI", 9)
        ).pack(anchor="w")

    # =========================================================================
    # TAMPILAN HALAMAN
    # =========================================================================
    def show_dashboard(self):
        page_heading(
            self,
            "Area administrasi",
            "Dashboard admin",
            "Ringkasan permohonan surat dan verifikasi tanda tangan digital dari database."
        )

        cards = tk.Frame(self, bg=BG)
        cards.pack(fill="x", pady=(0, 18))
        if self.error_message:
            values = [
                ("Total Pengajuan", "—", BLUE),
                ("Menunggu", "—", AMBER),
                ("Disetujui", "—", GREEN),
                ("Ditolak", "—", RED),
            ]
            self.show_database_error()
        else:
            stats = self.controller.hitung_statistik_pengajuan(self.pengajuan)
            values = [
                ("Total Pengajuan", str(stats["total"]), BLUE),
                ("Menunggu", str(stats["menunggu"]), AMBER),
                ("Disetujui", str(stats["disetujui"]), GREEN),
                ("Ditolak", str(stats["ditolak"]), RED),
            ]

        for title, value, accent in values:
            self.stat_card(cards, title, value, accent)

        box = panel(self, 20, 17)
        box.pack(fill="both", expand=True)
        tk.Label(
            box, text="Pengajuan terbaru", bg=WHITE, fg=NAVY,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 13))

        self.table = self.make_table(
            box,
            ("nomor", "mahasiswa", "jenis", "tanggal", "status", "status_dosen", "ttd"),
            ("NOMOR", "MAHASISWA", "JENIS SURAT", "TANGGAL", "STATUS", "TTD DOSEN", "KODE TTD")
        )
        self.fill_table(self.pengajuan[:8])

    def show_queue(self):
        page_heading(
            self,
            "Area administrasi",
            "Kelola pengajuan",
            "Tambah, tinjau permohonan, perbarui status persetujuan, dan pratinjau dokumen."
        )
        if self.error_message:
            self.show_database_error()

        box = panel(self, 20, 17)
        box.pack(fill="both", expand=True)
        toolbar = tk.Frame(box, bg=WHITE)
        toolbar.pack(fill="x", pady=(0, 14))

        tk.Label(
            toolbar, text="Daftar permohonan", bg=WHITE, fg=NAVY,
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")

        primary_button(
            toolbar, "＋ Tambah Pengajuan", self.buka_dialog_tambah_pengajuan
        ).pack(side="right", padx=(10, 0))

        self.filter = ttk.Combobox(
            toolbar, state="readonly", width=18,
            values=["Semua status", "Diajukan", "Diproses", "Disetujui", "Selesai", "Ditolak"]
        )
        self.filter.set("Semua status")
        self.filter.pack(side="right")
        self.filter.bind("<<ComboboxSelected>>", self.filter_pengajuan)

        self.search_hint = "Cari nomor, mahasiswa, atau jenis surat"
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
        search_entry.pack(
            side="right",
            fill="x",
            expand=True,
            padx=12,
            ipady=7
        )
        search_entry.bind("<FocusIn>", self.clear_search_hint)
        search_entry.bind("<FocusOut>", self.restore_search_hint)
        search_entry.bind("<KeyRelease>", self.filter_pengajuan)

        self.table = self.make_table(
            box,
            ("nomor", "mahasiswa", "jenis", "tanggal", "status", "status_dosen", "ttd"),
            ("NOMOR", "MAHASISWA", "JENIS SURAT", "TANGGAL", "STATUS", "TTD DOSEN", "KODE TTD")
        )
        self.fill_table(self.pengajuan)

        actions = tk.Frame(box, bg=WHITE)
        actions.pack(fill="x", pady=(15, 0))

        tk.Label(
            actions, text="Status pengajuan terpilih:", bg=WHITE, fg=MUTED,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.status = ttk.Combobox(
            actions, state="readonly", width=16,
            values=["Diajukan", "Diproses", "Disetujui", "Selesai", "Ditolak"]
        )
        self.status.set("Pilih status")
        self.status.pack(side="left", padx=9)

        primary_button(actions, "Simpan status", self.update_status).pack(side="left")

        secondary_button(
            actions,
            "👁 Pratinjau Surat & TTD Digital",
            self.buka_pratinjau_admin
        ).pack(side="right")

    def show_mahasiswa(self):
        page_heading(
            self,
            "Data master",
            "Data mahasiswa",
            "Kelola data mahasiswa pemohon yang tersimpan pada database."
        )
        if self.error_message:
            self.show_database_error()
        box = panel(self, 20, 17)
        box.pack(fill="both", expand=True)
        toolbar = tk.Frame(box, bg=WHITE)
        toolbar.pack(fill="x", pady=(0, 14))
        self.lbl_count_mhs = tk.Label(
            toolbar, text=f"{len(self.mahasiswa)} mahasiswa", bg=WHITE,
            fg=NAVY, font=("Segoe UI", 12, "bold")
        )
        self.lbl_count_mhs.pack(side="left")
        self.table = self.make_table(
            box,
            ("id", "nim", "nama", "prodi", "email"),
            ("ID", "NIM", "NAMA MAHASISWA", "PROGRAM STUDI", "EMAIL")
        )
        self.fill_table(self.mahasiswa)
        self.master_data_actions(box, "mahasiswa", allow_add=True)

    def show_dosen(self):
        page_heading(
            self,
            "Data master",
            "Data dosen pembimbing",
            "Kelola data dosen pembimbing dan status akun aktif."
        )
        if self.error_message:
            self.show_database_error()
        box = panel(self, 20, 17)
        box.pack(fill="both", expand=True)
        toolbar = tk.Frame(box, bg=WHITE)
        toolbar.pack(fill="x", pady=(0, 14))
        self.lbl_count_dosen = tk.Label(
            toolbar, text=f"{len(self.dosen)} dosen terdaftar", bg=WHITE,
            fg=NAVY, font=("Segoe UI", 12, "bold")
        )
        self.lbl_count_dosen.pack(side="left")
        self.table = self.make_table(
            box,
            ("id", "nip", "nama", "jabatan", "email", "status_ttd"),
            ("ID", "NIDN", "NAMA DOSEN", "JABATAN AKADEMIK", "EMAIL", "STATUS AKUN")
        )
        self.fill_table(self.dosen)
        self.master_data_actions(box, "dosen", allow_add=True)

    def show_jenis_surat(self):
        page_heading(
            self,
            "Data master",
            "Jenis surat",
            "Daftar jenis layanan surat akademik yang tersedia di sistem."
        )
        if self.error_message:
            self.show_database_error()
        box = panel(self, 20, 17)
        box.pack(fill="both", expand=True)
        toolbar = tk.Frame(box, bg=WHITE)
        toolbar.pack(fill="x", pady=(0, 14))
        self.lbl_count_jenis = tk.Label(
            toolbar, text=f"{len(self.jenis_surat)} jenis surat", bg=WHITE,
            fg=NAVY, font=("Segoe UI", 12, "bold")
        )
        self.lbl_count_jenis.pack(side="left")
        self.table = self.make_table(
            box,
            ("id", "nama", "deskripsi"),
            ("ID", "NAMA JENIS SURAT", "STATUS LAYANAN")
        )
        self.fill_table(self.jenis_surat)
        self.master_data_actions(box, "jenis surat", allow_add=False)

    # =========================================================================
    # HELPER TABEL & TOMBOL AKSI
    # =========================================================================
    @staticmethod
    def stat_card(parent, title, value, accent):
        card = tk.Frame(
            parent, bg=WHITE, padx=16, pady=16,
            highlightbackground=LINE, highlightthickness=1
        )
        card.pack(side="left", fill="x", expand=True, padx=(0, 11))
        tk.Label(card, text=title.upper(), bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        tk.Label(card, text=value, bg=WHITE, fg=accent,
                 font=("Segoe UI", 25, "bold")).pack(anchor="w", pady=(8, 0))

    @staticmethod
    def make_table(parent, columns, headings):
        table = ttk.Treeview(parent, columns=columns, show="headings", height=8)
        col_widths = {
            "nomor": 85,
            "mahasiswa": 150,
            "jenis": 210,
            "tanggal": 105,
            "status": 95,
            "status_dosen": 115,
            "ttd": 170,
            "id": 50,
            "nim": 110,
            "nip": 120,
            "prodi": 140,
            "nama": 170,
            "email": 170,
            "jabatan": 180,
            "status_ttd": 130,
            "deskripsi": 200
        }
        for column, heading in zip(columns, headings):
            table.heading(column, text=heading)
            table.column(column, width=col_widths.get(column, 130), anchor="w")
        table.pack(fill="both", expand=True)
        return table

    def fill_table(self, rows):
        self.table.delete(*self.table.get_children())
        for row in rows:
            self.table.insert("", "end", values=row)

    def master_data_actions(self, parent, nama_data, allow_add=True):
        actions = tk.Frame(parent, bg=WHITE)
        actions.pack(fill="x", pady=(14, 0))
        tk.Label(
            actions,
            text=f"Pengelolaan {nama_data} tersimpan di basis data akademik.",
            bg=WHITE,
            fg=MUTED,
            font=("Segoe UI", 8)
        ).pack(side="left")

        secondary_button(
            actions, "Hapus", lambda: self.handle_hapus_master(nama_data)
        ).pack(side="right", padx=(8, 0))

        secondary_button(
            actions, "Ubah", lambda: self.handle_ubah_master(nama_data)
        ).pack(side="right", padx=(8, 0))

        if allow_add:
            primary_button(
                actions, "＋ Tambah", lambda: self.handle_tambah_master(nama_data)
            ).pack(side="right")

    # =========================================================================
    # DIALOG TAMBAH PENGAJUAN OLEH ADMIN
    # =========================================================================
    def buka_dialog_tambah_pengajuan(self):
        try:
            master_data = self.controller.get_master_untuk_pengajuan()
            list_mhs = master_data["mahasiswa"]
            list_jenis = master_data["jenis_surat"]
            list_dosen = master_data["dosen"]
        except Exception as e:
            messagebox.showerror("Error Database", f"Gagal memuat data master: {e}")
            return

        if not list_mhs or not list_jenis:
            messagebox.showwarning(
                "Data Master Kosong",
                "Pastikan data Mahasiswa dan Jenis Surat sudah tersedia di database."
            )
            return

        dlg = tk.Toplevel(self)
        dlg.title("Tambah Pengajuan Surat (Admin)")
        dlg.geometry("480x500")
        dlg.configure(bg=WHITE)
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()

        wrap = tk.Frame(dlg, bg=WHITE, padx=22, pady=18)
        wrap.pack(fill="both", expand=True)

        tk.Label(wrap, text="Buat Pengajuan Baru", bg=WHITE, fg=NAVY, font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(wrap, text="Input permohonan surat atas nama mahasiswa.", bg=WHITE, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w", pady=(2, 14))

        # Pilih Mahasiswa
        tk.Label(wrap, text="Mahasiswa *", bg=WHITE, fg="#2C4037", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))
        mhs_map = {f"{m['nim']} — {m['nama']}": m for m in list_mhs}
        cb_mhs = ttk.Combobox(wrap, state="readonly", values=list(mhs_map.keys()), font=("Segoe UI", 9))
        cb_mhs.pack(fill="x", ipady=4, pady=(0, 10))
        cb_mhs.current(0)

        # Pilih Jenis Surat
        tk.Label(wrap, text="Jenis Surat *", bg=WHITE, fg="#2C4037", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))
        jenis_map = {(j.get("jenis_surat") or j.get("nama_jenis")): j for j in list_jenis}
        cb_jenis = ttk.Combobox(wrap, state="readonly", values=list(jenis_map.keys()), font=("Segoe UI", 9))
        cb_jenis.pack(fill="x", ipady=4, pady=(0, 10))
        cb_jenis.current(0)

        # Pilih Dosen
        tk.Label(wrap, text="Dosen Pembimbing / Wali *", bg=WHITE, fg="#2C4037", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))
        dosen_map = {f"{d['nama_dosen']} ({d.get('nidn') or '-'})": d for d in list_dosen}
        cb_dosen = ttk.Combobox(wrap, state="readonly", values=list(dosen_map.keys()), font=("Segoe UI", 9))
        cb_dosen.pack(fill="x", ipady=4, pady=(0, 10))
        if dosen_map:
            cb_dosen.current(0)

        # Keterangan / Keperluan
        tk.Label(wrap, text="Keterangan / Keperluan *", bg=WHITE, fg="#2C4037", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))
        txt_keperluan = tk.Text(wrap, height=4, font=("Segoe UI", 9), relief="solid", bd=1)
        txt_keperluan.pack(fill="x", pady=(0, 12))

        # Kotak Lampiran (Opsional)
        state_lampiran = {"path": None}
        attach_box = tk.Frame(wrap, bg="#F8F8F0", padx=8, pady=6, highlightbackground=LINE, highlightthickness=1)
        attach_box.pack(fill="x", pady=(0, 14))

        btn_pilih = tk.Button(
            attach_box,
            text="＋  Tambahkan lampiran (Opsional)",
            bg="#F8F8F0", fg=BLUE, activebackground="#EFEFE5", activeforeground=BLUE,
            font=("Segoe UI", 9, "bold"), bd=0, highlightthickness=0, cursor="hand2", anchor="w"
        )
        btn_pilih.pack(side="left", fill="x", expand=True)

        btn_hapus = tk.Button(
            attach_box,
            text="✕ Hapus",
            bg="#F8F8F0", fg="#B65C54", activebackground="#EFEFE5", activeforeground="#B65C54",
            font=("Segoe UI", 8, "bold"), bd=0, highlightthickness=0, cursor="hand2"
        )

        lbl_info = tk.Label(attach_box, text="PDF / JPG · maks. 5 MB", bg="#F8F8F0", fg=MUTED, font=("Segoe UI", 8))
        lbl_info.pack(side="right", padx=(0, 4))

        def pilih_file():
            file_path = filedialog.askopenfilename(
                parent=dlg,
                title="Pilih Dokumen Lampiran",
                filetypes=[
                    ("Semua Dokumen", "*.pdf *.jpg *.jpeg *.png *.PDF *.JPG *.JPEG *.PNG"),
                    ("File PDF", "*.pdf *.PDF"),
                    ("Gambar", "*.jpg *.jpeg *.png *.JPG *.JPEG *.PNG")
                ]
            )
            if not file_path:
                return

            valid, info = self.controller.validasi_lampiran(file_path)
            if not valid:
                messagebox.showwarning("Lampiran Tidak Valid", info, parent=dlg)
                return

            state_lampiran["path"] = file_path
            btn_pilih.configure(text=f"📄  {info['nama']}", fg="#2C4037")
            lbl_info.configure(text=info["ukuran"])
            btn_hapus.pack(side="right", padx=(6, 4))

        def hapus_file():
            state_lampiran["path"] = None
            btn_pilih.configure(text="＋  Tambahkan lampiran (Opsional)", fg=BLUE)
            lbl_info.configure(text="PDF / JPG · maks. 5 MB")
            btn_hapus.pack_forget()

        btn_pilih.configure(command=pilih_file)
        btn_hapus.configure(command=hapus_file)

        def simpan():
            mhs_obj = mhs_map[cb_mhs.get()]
            jenis_obj = jenis_map[cb_jenis.get()]
            dosen_obj = dosen_map.get(cb_dosen.get())
            keperluan = txt_keperluan.get("1.0", "end")

            sukses, hasil = self.controller.tambah_pengajuan_admin(
                id_mahasiswa=mhs_obj["id_mahasiswa"],
                id_jenis_surat=jenis_obj["id_jenis_surat"],
                id_dosen=dosen_obj["id_dosen"] if dosen_obj else None,
                keperluan=keperluan,
                path_lampiran=state_lampiran["path"],
            )
            if not sukses:
                messagebox.showwarning("Validasi / Kesalahan", hasil, parent=dlg)
                return

            dlg.destroy()
            self.load_pengajuan()
            self.filter_pengajuan()
            messagebox.showinfo(
                "Berhasil",
                f"Pengajuan #{hasil['id_pengajuan']:03d} berhasil ditambahkan.\nLampiran: {hasil['info_lampiran']}"
            )

        btns = tk.Frame(wrap, bg=WHITE)
        btns.pack(fill="x")
        secondary_button(btns, "Batal", dlg.destroy).pack(side="right", padx=(8, 0))
        primary_button(btns, "Simpan Pengajuan", simpan).pack(side="right")

    # =========================================================================
    # CRUD DATA MASTER (MAHASISWA, DOSEN, & UBAH/HAPUS JENIS SURAT)
    # =========================================================================
    def handle_tambah_master(self, nama_data):
        if nama_data == "mahasiswa":
            self.buka_form_mahasiswa()
        elif nama_data == "dosen":
            self.buka_form_dosen()

    def handle_ubah_master(self, nama_data):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Pilih Data", f"Pilih satu baris {nama_data} pada tabel terlebih dahulu.")
            return

        vals = self.table.item(selected[0], "values")
        id_target = vals[0]

        if nama_data == "mahasiswa":
            data = next((m for m in self.raw_mahasiswa if str(m["id_mahasiswa"]) == str(id_target)), None)
            if data:
                self.buka_form_mahasiswa(data)
        elif nama_data == "dosen":
            data = next((d for d in self.raw_dosen if str(d["id_dosen"]) == str(id_target)), None)
            if data:
                self.buka_form_dosen(data)
        elif nama_data == "jenis surat":
            data = next((j for j in self.raw_jenis_surat if str(j["id_jenis_surat"]) == str(id_target)), None)
            if data:
                self.buka_form_jenis_surat(data)

    def handle_hapus_master(self, nama_data):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Pilih Data", f"Pilih satu baris {nama_data} yang ingin dihapus.")
            return

        vals = self.table.item(selected[0], "values")
        id_target = vals[0]
        label_item = vals[2] if len(vals) > 2 else vals[1]

        if not messagebox.askyesno("Konfirmasi Hapus", f"Yakin ingin menghapus {nama_data} '{label_item}'?"):
            return

        if nama_data == "mahasiswa":
            sukses, pesan = self.controller.hapus_mahasiswa(id_target)
            if sukses:
                self.load_mahasiswa()
                self.fill_table(self.mahasiswa)
                self.lbl_count_mhs.configure(text=f"{len(self.mahasiswa)} mahasiswa")
        elif nama_data == "dosen":
            sukses, pesan = self.controller.hapus_dosen(id_target)
            if sukses:
                self.load_dosen()
                self.fill_table(self.dosen)
                self.lbl_count_dosen.configure(text=f"{len(self.dosen)} dosen terdaftar")
        elif nama_data == "jenis surat":
            sukses, pesan = self.controller.hapus_jenis_surat(id_target)
            if sukses:
                self.load_jenis_surat()
                self.fill_table(self.jenis_surat)
                self.lbl_count_jenis.configure(text=f"{len(self.jenis_surat)} jenis surat")
        else:
            return

        if sukses:
            messagebox.showinfo("Terhapus", pesan)
        else:
            messagebox.showerror("Gagal Menghapus", pesan)

    def buka_form_mahasiswa(self, data=None):
        is_edit = data is not None
        dlg = tk.Toplevel(self)
        dlg.title("Ubah Data Mahasiswa" if is_edit else "Tambah Data Mahasiswa")
        dlg.geometry("420x360")
        dlg.configure(bg=WHITE)
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()

        wrap = tk.Frame(dlg, bg=WHITE, padx=22, pady=18)
        wrap.pack(fill="both", expand=True)

        tk.Label(
            wrap, text="Edit Mahasiswa" if is_edit else "Tambah Mahasiswa Baru",
            bg=WHITE, fg=NAVY, font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", pady=(0, 12))

        fields = {}
        for key, label, default_val in [
            ("nim", "NIM *", data.get("nim", "") if is_edit else ""),
            ("nama", "Nama Lengkap *", data.get("nama", "") if is_edit else ""),
            ("prodi", "Program Studi *", data.get("prodi", "") if is_edit else "Sistem Informasi"),
            ("email", "Email", data.get("email", "") if is_edit else ""),
        ]:
            tk.Label(wrap, text=label, bg=WHITE, fg="#2C4037", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 3))
            ent = tk.Entry(wrap, font=("Segoe UI", 9), relief="solid", bd=1)
            ent.pack(fill="x", ipady=5, pady=(0, 9))
            if default_val:
                ent.insert(0, default_val)
            fields[key] = ent

        def simpan():
            sukses, pesan = self.controller.simpan_mahasiswa(
                nim=fields["nim"].get(),
                nama=fields["nama"].get(),
                prodi=fields["prodi"].get(),
                email=fields["email"].get(),
                id_mahasiswa=data["id_mahasiswa"] if is_edit else None,
            )
            if not sukses:
                messagebox.showwarning("Validasi / Kesalahan", pesan, parent=dlg)
                return

            dlg.destroy()
            self.load_mahasiswa()
            self.fill_table(self.mahasiswa)
            self.lbl_count_mhs.configure(text=f"{len(self.mahasiswa)} mahasiswa")
            messagebox.showinfo("Berhasil", pesan)

        btns = tk.Frame(wrap, bg=WHITE)
        btns.pack(fill="x", pady=(8, 0))
        secondary_button(btns, "Batal", dlg.destroy).pack(side="right", padx=(8, 0))
        primary_button(btns, "Simpan", simpan).pack(side="right")

    def buka_form_dosen(self, data=None):
        is_edit = data is not None
        dlg = tk.Toplevel(self)
        dlg.title("Ubah Data Dosen" if is_edit else "Tambah Data Dosen")
        dlg.geometry("420x370")
        dlg.configure(bg=WHITE)
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()

        wrap = tk.Frame(dlg, bg=WHITE, padx=22, pady=18)
        wrap.pack(fill="both", expand=True)

        tk.Label(
            wrap, text="Edit Dosen" if is_edit else "Tambah Dosen Baru",
            bg=WHITE, fg=NAVY, font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", pady=(0, 12))

        tk.Label(wrap, text="NIDN *", bg=WHITE, fg="#2C4037", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 3))
        ent_nidn = tk.Entry(wrap, font=("Segoe UI", 9), relief="solid", bd=1)
        ent_nidn.pack(fill="x", ipady=5, pady=(0, 9))
        if is_edit and data.get("nidn"):
            ent_nidn.insert(0, data["nidn"])

        tk.Label(wrap, text="Nama Dosen (beserta gelar) *", bg=WHITE, fg="#2C4037", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 3))
        ent_nama = tk.Entry(wrap, font=("Segoe UI", 9), relief="solid", bd=1)
        ent_nama.pack(fill="x", ipady=5, pady=(0, 9))
        if is_edit and data.get("nama_dosen"):
            ent_nama.insert(0, data["nama_dosen"])

        tk.Label(wrap, text="Jabatan Akademik *", bg=WHITE, fg="#2C4037", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 3))
        jabatan_opts = ["Dosen Wali", "Dosen Pembimbing", "Ketua Program Studi", "Ketua Jurusan"]
        cb_jabatan = ttk.Combobox(wrap, state="readonly", values=jabatan_opts, font=("Segoe UI", 9))
        cb_jabatan.pack(fill="x", ipady=4, pady=(0, 9))
        if is_edit and data.get("jabatan") in jabatan_opts:
            cb_jabatan.set(data["jabatan"])
        else:
            cb_jabatan.current(0)

        tk.Label(wrap, text="Email", bg=WHITE, fg="#2C4037", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 3))
        ent_email = tk.Entry(wrap, font=("Segoe UI", 9), relief="solid", bd=1)
        ent_email.pack(fill="x", ipady=5, pady=(0, 12))
        if is_edit and data.get("email"):
            ent_email.insert(0, data["email"])

        def simpan():
            sukses, pesan = self.controller.simpan_dosen(
                nidn=ent_nidn.get(),
                nama_dosen=ent_nama.get(),
                jabatan=cb_jabatan.get(),
                email=ent_email.get(),
                id_dosen=data["id_dosen"] if is_edit else None,
            )
            if not sukses:
                messagebox.showwarning("Validasi / Kesalahan", pesan, parent=dlg)
                return

            dlg.destroy()
            self.load_dosen()
            self.fill_table(self.dosen)
            self.lbl_count_dosen.configure(text=f"{len(self.dosen)} dosen terdaftar")
            messagebox.showinfo("Berhasil", pesan)

        btns = tk.Frame(wrap, bg=WHITE)
        btns.pack(fill="x", pady=(6, 0))
        secondary_button(btns, "Batal", dlg.destroy).pack(side="right", padx=(8, 0))
        primary_button(btns, "Simpan", simpan).pack(side="right")

    def buka_form_jenis_surat(self, data):
        dlg = tk.Toplevel(self)
        dlg.title("Ubah Jenis Surat")
        dlg.geometry("400x230")
        dlg.configure(bg=WHITE)
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()

        wrap = tk.Frame(dlg, bg=WHITE, padx=22, pady=18)
        wrap.pack(fill="both", expand=True)

        tk.Label(wrap, text="Edit Jenis Surat", bg=WHITE, fg=NAVY, font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 12))

        tk.Label(wrap, text="Nama Jenis Surat *", bg=WHITE, fg="#2C4037", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 3))
        ent_nama = tk.Entry(wrap, font=("Segoe UI", 9), relief="solid", bd=1)
        ent_nama.pack(fill="x", ipady=5, pady=(0, 10))
        ent_nama.insert(0, data.get("jenis_surat") or data.get("nama_jenis", ""))

        aktif_var = tk.IntVar(value=1 if data.get("aktif", 1) == 1 else 0)
        tk.Checkbutton(wrap, text="Layanan surat aktif", variable=aktif_var, bg=WHITE, font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 12))

        def simpan():
            sukses, pesan = self.controller.perbarui_jenis_surat(
                id_jenis_surat=data["id_jenis_surat"],
                nama_jenis=ent_nama.get(),
                aktif=aktif_var.get(),
            )
            if not sukses:
                messagebox.showwarning("Validasi / Kesalahan", pesan, parent=dlg)
                return

            dlg.destroy()
            self.load_jenis_surat()
            self.fill_table(self.jenis_surat)
            messagebox.showinfo("Berhasil", pesan)

        btns = tk.Frame(wrap, bg=WHITE)
        btns.pack(fill="x")
        secondary_button(btns, "Batal", dlg.destroy).pack(side="right", padx=(8, 0))
        primary_button(btns, "Simpan", simpan).pack(side="right")

    # =========================================================================
    # PRATINJAU, UPDATE STATUS, & FILTER PENGAJUAN
    # =========================================================================
    def buka_pratinjau_admin(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning(
                "Pilih Pengajuan",
                "Silakan pilih satu pengajuan pada tabel terlebih dahulu."
            )
            return

        nomor = self.table.item(selected[0], "values")[0]
        data = next((r for r in self.raw_pengajuan if str(r.get("nomor_pengajuan")) == str(nomor)), None)
        if not data:
            return

        status = str(data.get("status") or "").strip().lower()
        if status == "ditolak":
            messagebox.showwarning(
                "Surat Ditolak",
                f"Pengajuan #{nomor} masih berstatus Diproses/Ditolak sehingga tidak memiliki surat resmi bertanda tangan."
            )
            return
        if status not in ("disetujui", "selesai"):
            messagebox.showinfo(
                "Belum Ditandatangani",
                f"Pengajuan #{nomor} masih berstatus '{data.get('status')}' dan belum ditandatangani oleh dosen."
            )
            return

        SuratPreviewDialog(self, data)

    def update_status(self):
        selected = self.table.selection()
        new_status = self.status.get()
        if not selected:
            messagebox.showwarning(
                "Pilih pengajuan",
                "Pilih satu pengajuan pada tabel terlebih dahulu."
            )
            return

        nomor = self.table.item(selected[0], "values")[0]
        data_target = next((r for r in self.raw_pengajuan if str(r.get("nomor_pengajuan")) == str(nomor)), None)

        if data_target:
            sukses, pesan = self.controller.ubah_status_pengajuan(
                id_pengajuan=data_target["id_pengajuan"],
                status_baru=new_status,
            )
            if not sukses:
                messagebox.showwarning("Peringatan", pesan)
                return

            self.load_pengajuan()
            self.filter_pengajuan()
            messagebox.showinfo(
                "Status Diperbarui",
                f"Status surat #{nomor} berhasil diubah menjadi '{new_status}' di database."
            )

    def clear_search_hint(self, _event=None):
        if self.search_var.get() == self.search_hint:
            self.search_var.set("")

    def restore_search_hint(self, _event=None):
        if not self.search_var.get().strip():
            self.search_var.set(self.search_hint)

    def filter_pengajuan(self, _event=None):
        query = self.search_var.get().strip()
        if query.lower() == self.search_hint.lower():
            query = ""

        hasil = self.controller.filter_pengajuan(
            self.pengajuan,
            keyword=query,
            filter_status=self.filter.get(),
        )
        self.fill_table(hasil)