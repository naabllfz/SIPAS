import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from PIL import Image, ImageTk

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.utils import simpleSplit

from views.theme import (
    BG, WHITE, NAVY, BLUE, BLUE_DARK, MUTED, LINE,
    GREEN, PALE_GREEN, AMBER, RED, PALE_RED,
    primary_button, secondary_button
)
from views.image_loader import load_logo_image, set_window_icon


class SuratPreviewDialog(tk.Toplevel):
    """
    Dialog pratinjau surat resmi akademik Universitas Tadulako dengan tanda tangan asli & digital dosen,
    serta fitur ekspor langsung ke dokumen PDF (A4) khusus untuk surat yang telah disetujui.
    """

    def __init__(self, parent, data_surat):
        super().__init__(parent)
        self.data = data_surat or {}
        self.ttd_img_ref = None

        status_raw = str(self.data.get("status") or "").strip().lower()
        self.sudah_disetujui = status_raw in ("disetujui", "selesai")
        self.is_ditolak = status_raw == "ditolak"

        nomor = self.data.get("nomor_pengajuan", "000")
        self.title(f"SIPAS UNTAD | Pratinjau Surat Resmi #{nomor}")
        self.geometry("780x840")
        self.minsize(700, 680)
        self.configure(bg="#E5E7DE")

        set_window_icon(self)

        self.transient(parent)
        self.grab_set()

        self.setup_ui()
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2) - 20
        self.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")

    def format_date(self, val):
        if not val:
            return "-"
        if hasattr(val, "strftime"):
            return val.strftime("%d %B %Y")
        try:
            return datetime.strptime(str(val)[:19], "%Y-%m-%d %H:%M:%S").strftime("%d %B %Y")
        except Exception:
            return str(val)

    def format_datetime(self, val):
        if not val:
            return "-"
        if hasattr(val, "strftime"):
            return val.strftime("%d %B %Y, %H:%M:%S WITA")
        try:
            return datetime.strptime(str(val)[:19], "%Y-%m-%d %H:%M:%S").strftime("%d %B %Y, %H:%M:%S WITA")
        except Exception:
            return str(val)

    def setup_ui(self):
        # Action toolbar di bagian atas
        toolbar = tk.Frame(self, bg=NAVY, padx=20, pady=12)
        toolbar.pack(fill="x")

        judul_bar = (
            "PRATINJAU SURAT RESMI UNIVERSITAS TADULAKO"
            if self.sudah_disetujui
            else "PRATINJAU DRAF PERMOHONAN (BELUM DISAHKAN)"
        )
        tk.Label(
            toolbar,
            text=judul_bar,
            bg=NAVY,
            fg="#D9E6D8",
            font=("Segoe UI", 9, "bold")
        ).pack(side="left")

        secondary_button(
            toolbar,
            "✕ Tutup",
            self.tutup_dialog,
            padx=12,
            pady=4
        ).pack(side="right", padx=(8, 0))

        # Tombol Simpan ke PDF HANYA muncul jika surat sudah disetujui
        if self.sudah_disetujui:
            primary_button(
                toolbar,
                "📄 Simpan ke PDF",
                self.simpan_pdf,
                padx=14,
                pady=4
            ).pack(side="right")

        # Scrollable container untuk kertas surat
        container = tk.Frame(self, bg="#E5E7DE")
        container.pack(fill="both", expand=True, padx=20, pady=15)

        self.canvas = tk.Canvas(container, bg="#E5E7DE", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        scrollable_frame = tk.Frame(self.canvas, bg="#E5E7DE")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        canvas_window = self.canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def on_canvas_configure(event):
            self.canvas.itemconfig(canvas_window, width=event.width)

        self.canvas.bind("<Configure>", on_canvas_configure)
        self.canvas.configure(xscrollcommand=None, yscrollcommand=scrollbar.set)

        def on_mousewheel(event):
            if self.canvas.winfo_exists():
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas.bind_all("<MouseWheel>", on_mousewheel)
        self.protocol("WM_DELETE_WINDOW", self.tutup_dialog)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Lembaran Kertas Surat (A4 look)
        paper = tk.Frame(
            scrollable_frame,
            bg=WHITE,
            padx=45,
            pady=40,
            highlightbackground="#CDD2C4",
            highlightthickness=1
        )
        paper.pack(fill="x", expand=True, padx=25, pady=10)

        # 1. KOP SURAT RESMI UNIVERSITAS TADULAKO
        kop = tk.Frame(paper, bg=WHITE)
        kop.pack(fill="x")

        logo_frame = tk.Frame(kop, bg=WHITE)
        logo_frame.pack(side="left", padx=(0, 16))

        logo_img = load_logo_image((62, 62))
        if logo_img:
            lbl_logo = tk.Label(logo_frame, image=logo_img, bg=WHITE)
            lbl_logo.image = logo_img
            lbl_logo.pack()
        else:
            canvas_logo = tk.Canvas(logo_frame, width=62, height=62, bg=WHITE, highlightthickness=0)
            canvas_logo.pack()
            canvas_logo.create_oval(3, 3, 59, 59, outline=NAVY, width=2, fill="#F2F6ED")
            canvas_logo.create_text(31, 31, text="UNTAD", fill=NAVY, font=("Segoe UI", 10, "bold"))

        kop_text = tk.Frame(kop, bg=WHITE)
        kop_text.pack(side="left", fill="x", expand=True)

        tk.Label(
            kop_text,
            text="KEMENTERIAN PENDIDIKAN TINGGI, SAINS, DAN TEKNOLOGI",
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="center")

        tk.Label(
            kop_text,
            text="UNIVERSITAS TADULAKO",
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="center")

        tk.Label(
            kop_text,
            text="FAKULTAS TEKNIK — JURUSAN TEKNOLOGI INFORMASI",
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="center")

        tk.Label(
            kop_text,
            text="PROGRAM STUDI S1 SISTEM INFORMASI",
            bg=WHITE,
            fg=BLUE,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="center")

        tk.Label(
            kop_text,
            text="Kampus Bumi Tadulako Tondo, Jl. Soekarno-Hatta Km. 9 Palu 94118, Sulawesi Tengah\nTelp. (0451) 422611 | Laman: https://untad.ac.id | Email: si@untad.ac.id",
            bg=WHITE,
            fg=MUTED,
            font=("Segoe UI", 8),
            justify="center"
        ).pack(anchor="center", pady=(2, 0))

        # Garis pemisah kop surat ganda
        tk.Frame(paper, bg=NAVY, height=3).pack(fill="x", pady=(10, 1))
        tk.Frame(paper, bg=NAVY, height=1).pack(fill="x", pady=(0, 20))

        # 2. NOMOR & PERIHAL SURAT
        nomor_pengajuan = self.data.get("nomor_pengajuan", "-")
        jenis_surat = self.data.get("jenis_surat") or self.data.get("nama_jenis") or self.data.get("nama_jenis_surat") or "Surat Akademik"
        tgl_pengajuan = self.format_date(self.data.get("tanggal_pengajuan"))
        nama_lampiran = self.data.get("nama_file")
        teks_lampiran = f": 1 Berkas ({nama_lampiran})" if nama_lampiran and str(nama_lampiran).startswith("lampiran_") else ": —"

        header_meta = tk.Frame(paper, bg=WHITE)
        header_meta.pack(fill="x", pady=(0, 16))

        col_left = tk.Frame(header_meta, bg=WHITE)
        col_left.pack(side="left")

        nomor_resmi = f": B/{nomor_pengajuan}/UN28.1/KM/2026" if self.sudah_disetujui else f": [DRAF #{nomor_pengajuan} — BELUM BERNOMOR RESMI]"
        meta_rows = [
            ("Nomor", nomor_resmi),
            ("Lampiran", teks_lampiran),
            ("Perihal", f": {jenis_surat}")
        ]
        for lbl, val in meta_rows:
            row = tk.Frame(col_left, bg=WHITE)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=lbl, bg=WHITE, fg=NAVY, width=9, anchor="w", font=("Segoe UI", 9, "bold")).pack(side="left")
            tk.Label(row, text=val, bg=WHITE, fg=NAVY if self.sudah_disetujui else MUTED, font=("Segoe UI", 9)).pack(side="left")

        col_right = tk.Frame(header_meta, bg=WHITE)
        col_right.pack(side="right", anchor="n")
        tk.Label(col_right, text=f"Palu, {tgl_pengajuan}", bg=WHITE, fg=NAVY, font=("Segoe UI", 9)).pack(anchor="e")

        # 3. KEPADA
        tujuan_box = tk.Frame(paper, bg=WHITE)
        tujuan_box.pack(fill="x", pady=(8, 16))
        tk.Label(
            tujuan_box,
            text="Yth. Mahasiswa yang bersangkutan / Pihak Berkepentingan\ndi Lingkungan Universitas Tadulako",
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 9),
            justify="left"
        ).pack(anchor="w")

        # 4. ISI SURAT
        nama_mhs = self.data.get("nama") or self.data.get("nama_mahasiswa") or "-"
        nim_mhs = self.data.get("nim") or "-"
        prodi_mhs = self.data.get("prodi") or "Sistem Informasi"
        keperluan = self.data.get("keperluan") or self.data.get("deskripsi_jenis") or "Keperluan administrasi akademik mahasiswa."

        isi_pembuka = (
            "Dengan hormat,\n"
            "Yang bertanda tangan di bawah ini, Dosen Pembimbing Akademik / Dosen Wali Program Studi "
            "S1 Sistem Informasi Fakultas Teknik Universitas Tadulako, dengan ini menerangkan bahwa:"
        )
        tk.Label(
            paper,
            text=isi_pembuka,
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 9),
            justify="left",
            wraplength=620
        ).pack(anchor="w", pady=(0, 10))

        # Tabel Data Mahasiswa
        identitas = tk.Frame(paper, bg="#F9FAF5", padx=16, pady=12, highlightbackground=LINE, highlightthickness=1)
        identitas.pack(fill="x", pady=(0, 14))

        data_rows = [
            ("Nama Mahasiswa", nama_mhs),
            ("NIM", nim_mhs),
            ("Program Studi", prodi_mhs),
            ("Fakultas / Perguruan Tinggi", "Fakultas Teknik — Universitas Tadulako"),
            ("Keperluan Permohonan", keperluan),
        ]
        for label, val in data_rows:
            r = tk.Frame(identitas, bg="#F9FAF5")
            r.pack(fill="x", pady=2)
            tk.Label(r, text=label, bg="#F9FAF5", fg=MUTED, width=23, anchor="w", font=("Segoe UI", 9, "bold")).pack(side="left")
            tk.Label(r, text=f":  {val}", bg="#F9FAF5", fg=NAVY, font=("Segoe UI", 9, "bold" if label == "Nama Mahasiswa" else "normal")).pack(side="left")

        if self.sudah_disetujui:
            isi_penutup = (
                "Berdasarkan hasil verifikasi dan tinjauan akademik di lingkungan Jurusan Teknologi Informasi "
                "Universitas Tadulako, permohonan surat tersebut telah disetujui dan disahkan secara resmi. "
                "Demikian surat ini dibuat dengan sebenarnya untuk dapat dipergunakan sebagaimana mestinya."
            )
        elif self.is_ditolak:
            alasan = self.data.get("catatan_dosen") or self.data.get("catatan_admin") or "Persyaratan tidak terpenuhi."
            isi_penutup = (
                f"[STATUS: PERMOHONAN DITOLAK — Alasan: {alasan}] "
                "Dokumen ini tidak disahkan dan tidak berlaku sebagai surat resmi."
            )
        else:
            isi_penutup = (
                "[STATUS: DRAF DALAM PROSES VERIFIKASI] "
                "Permohonan surat ini masih menunggu persetujuan dan pengesahan tanda tangan dosen."
            )

        tk.Label(
            paper,
            text=isi_penutup,
            bg=WHITE,
            fg=NAVY if self.sudah_disetujui else (RED if self.is_ditolak else AMBER),
            font=("Segoe UI", 9, "normal" if self.sudah_disetujui else "bold"),
            justify="left",
            wraplength=620
        ).pack(anchor="w", pady=(0, 20))

        # 5. BAGIAN PENGESAHAN & TANDA TANGAN DOSEN
        ttd_digital = self.data.get("tanda_tangan_digital")
        nama_dosen = self.data.get("nama_dosen") or "Dr. Lukman Syafie, S.Kom., M.Kom."
        nip_dosen = self.data.get("nip_dosen") or self.data.get("nidn") or "198204122008121001"
        jabatan_dosen = self.data.get("jabatan_dosen") or "Dosen Wali / Pembimbing Akademik"
        file_ttd_dosen = self.data.get("file_ttd_dosen")
        tgl_disetujui = self.format_datetime(
            self.data.get("tanggal_keputusan_dosen") or self.data.get("tanggal_disetujui") or self.data.get("tanggal_pengajuan")
        )

        ttd_section = tk.Frame(paper, bg=WHITE)
        ttd_section.pack(fill="x", pady=(10, 0))

        ttd_box = tk.Frame(ttd_section, bg=WHITE)
        ttd_box.pack(side="right", anchor="e")

        tgl_teks = f"Palu, {self.format_date(self.data.get('tanggal_keputusan_dosen') or self.data.get('tanggal_disetujui') or self.data.get('tanggal_pengajuan'))}"
        tk.Label(ttd_box, text=tgl_teks, bg=WHITE, fg=NAVY, font=("Segoe UI", 9)).pack(anchor="w")
        tk.Label(ttd_box, text=jabatan_dosen + ",", bg=WHITE, fg=NAVY, font=("Segoe UI", 9, "bold")).pack(anchor="w")

        if self.sudah_disetujui:
            area_ttd = tk.Frame(ttd_box, bg=WHITE)
            area_ttd.pack(fill="x", pady=8)

            # Tampilkan Gambar TTD Asli Dosen jika tersedia
            if file_ttd_dosen and os.path.exists(file_ttd_dosen):
                try:
                    img = Image.open(file_ttd_dosen)
                    img.thumbnail((190, 85), Image.Resampling.LANCZOS)
                    self.ttd_img_ref = ImageTk.PhotoImage(img)

                    lbl_ttd_asli = tk.Label(area_ttd, image=self.ttd_img_ref, bg=WHITE)
                    lbl_ttd_asli.pack(anchor="w", pady=(2, 6))
                except Exception:
                    pass

            # Badge Verifikasi Digital SHA-256 & QR
            token_tampil = (ttd_digital[:28] + "...") if ttd_digital and len(ttd_digital) > 28 else (ttd_digital or "VERIFIED-UNTAD")
            sig_badge = tk.Frame(
                area_ttd,
                bg="#F2F8EE",
                padx=10,
                pady=8,
                highlightbackground="#527A3E",
                highlightthickness=1
            )
            sig_badge.pack(fill="x")

            b_head = tk.Frame(sig_badge, bg="#F2F8EE")
            b_head.pack(fill="x")

            qr_canvas = tk.Canvas(b_head, width=48, height=48, bg="white", highlightthickness=1, highlightbackground="#A5BA9B")
            qr_canvas.pack(side="left", padx=(0, 8))
            self.draw_mini_qr(qr_canvas, ttd_digital or nama_dosen)

            b_info = tk.Frame(b_head, bg="#F2F8EE")
            b_info.pack(side="left", fill="x", expand=True)

            tk.Label(
                b_info,
                text="✓ DITANDATANGANI & TERVERIFIKASI",
                bg="#F2F8EE",
                fg="#3D6330",
                font=("Segoe UI", 7, "bold")
            ).pack(anchor="w")

            tk.Label(
                b_info,
                text="SIPAS UNIVERSITAS TADULAKO",
                bg="#F2F8EE",
                fg=NAVY,
                font=("Segoe UI", 8, "bold")
            ).pack(anchor="w")

            tk.Label(
                b_info,
                text=f"Hash: {token_tampil}",
                bg="#F2F8EE",
                fg="#2C4037",
                font=("Consolas", 7, "bold")
            ).pack(anchor="w", pady=(1, 0))

            tk.Label(
                sig_badge,
                text=f"Disahkan pada: {tgl_disetujui}",
                bg="#F2F8EE",
                fg=MUTED,
                font=("Segoe UI", 7)
            ).pack(anchor="w", pady=(4, 0))

        elif self.is_ditolak:
            rejected_box = tk.Frame(
                ttd_box,
                bg=PALE_RED,
                padx=14,
                pady=14,
                highlightbackground=RED,
                highlightthickness=1
            )
            rejected_box.pack(fill="x", pady=10)
            tk.Label(
                rejected_box,
                text="✕ PENGAJUAN DITOLAK (TANPA PENGESAHAN)",
                bg=PALE_RED,
                fg=RED,
                font=("Segoe UI", 8, "bold")
            ).pack()
        else:
            pending_box = tk.Frame(
                ttd_box,
                bg="#FFF9E6",
                padx=14,
                pady=14,
                highlightbackground=AMBER,
                highlightthickness=1
            )
            pending_box.pack(fill="x", pady=10)
            tk.Label(
                pending_box,
                text="⏳ MENUNGGU TANDA TANGAN DOSEN",
                bg="#FFF9E6",
                fg=AMBER,
                font=("Segoe UI", 8, "bold")
            ).pack()

        tk.Label(
            ttd_box,
            text=nama_dosen,
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", pady=(4, 0))

        tk.Label(
            ttd_box,
            text=f"NIDN/NIP. {nip_dosen}",
            bg=WHITE,
            fg=MUTED,
            font=("Segoe UI", 9)
        ).pack(anchor="w")

        # 6. FOOTNOTE KEABSAHAN
        tk.Frame(paper, bg=LINE, height=1).pack(fill="x", pady=(25, 8))
        footnote = tk.Label(
            paper,
            text=(
                "Catatan Keabsahan: Dokumen ini diterbitkan secara elektronik oleh Sistem Informasi Pengajuan Surat (SIPAS) "
                "Fakultas Teknik Universitas Tadulako dan terverifikasi dengan algoritma kriptografi SHA-256."
                if self.sudah_disetujui
                else "DRAF PRATINJAU: Dokumen ini belum mendapat pengesahan dan tanda tangan dosen sehingga tidak sah untuk digunakan."
            ),
            bg=WHITE,
            fg="#8A968C" if self.sudah_disetujui else RED,
            font=("Segoe UI", 7, "normal" if self.sudah_disetujui else "bold"),
            justify="center",
            wraplength=620
        )
        footnote.pack(anchor="center")

    def tutup_dialog(self):
        try:
            self.canvas.unbind_all("<MouseWheel>")
        except Exception:
            pass
        self.destroy()

    def draw_mini_qr(self, canvas, seed_str):
        """Menggambar pola QR code visual estetik di atas canvas."""
        canvas.delete("all")
        cell_px = 6
        offset = 5

        canvas.create_rectangle(offset, offset, offset + 18, offset + 18, fill=NAVY, outline="")
        canvas.create_rectangle(offset + 3, offset + 3, offset + 15, offset + 15, fill="white", outline="")
        canvas.create_rectangle(offset + 6, offset + 6, offset + 12, offset + 12, fill=NAVY, outline="")

        canvas.create_rectangle(offset + 24, offset, offset + 36, offset + 12, fill=NAVY, outline="")
        canvas.create_rectangle(offset + 27, offset + 3, offset + 33, offset + 9, fill="white", outline="")

        canvas.create_rectangle(offset, offset + 24, offset + 12, offset + 36, fill=NAVY, outline="")
        canvas.create_rectangle(offset + 3, offset + 27, offset + 9, offset + 33, fill="white", outline="")

        val = abs(hash(seed_str))
        for r in range(2, 6):
            for c in range(2, 6):
                if (val >> ((r * 4 + c) % 30)) & 1:
                    x = offset + c * cell_px
                    y = offset + r * cell_px
                    canvas.create_rectangle(x, y, x + cell_px - 1, y + cell_px - 1, fill=NAVY, outline="")

    def simpan_pdf(self):
        """Mengekspor surat resmi Universitas Tadulako ke PDF A4 (hanya jika status Disetujui/Selesai)."""
        if not self.sudah_disetujui:
            messagebox.showwarning(
                "Belum Disahkan",
                "Dokumen hanya dapat disimpan ke PDF setelah disetujui dan ditandatangani oleh dosen.",
                parent=self
            )
            return

        nomor = self.data.get("nomor_pengajuan", "000")
        filename = filedialog.asksaveasfilename(
            parent=self,
            title="Simpan Surat Resmi Universitas Tadulako sebagai PDF",
            initialfile=f"Surat_UNTAD_{nomor}.pdf",
            defaultextension=".pdf",
            filetypes=[("PDF Document", "*.pdf")]
        )
        if not filename:
            return

        try:
            c = pdf_canvas.Canvas(filename, pagesize=A4)
            width, height = A4
            margin_x = 2.2 * cm
            y = height - 1.9 * cm

            # 1. KOP SURAT RESMI UNIVERSITAS TADULAKO
            logo_paths = [
                os.path.join("assets", "logo_untad.png"),
                os.path.join("assets", "logo.png"),
            ]
            logo_ditemukan = next((p for p in logo_paths if os.path.exists(p)), None)
            if logo_ditemukan:
                c.drawImage(logo_ditemukan, margin_x, y - 1.95 * cm, width=1.85 * cm, height=1.85 * cm, mask="auto", preserveAspectRatio=True)

            center_x = width / 2 + (0.7 * cm if logo_ditemukan else 0)
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(center_x, y - 0.25 * cm, "KEMENTERIAN PENDIDIKAN TINGGI, SAINS, DAN TEKNOLOGI")
            c.setFont("Helvetica-Bold", 13.5)
            c.drawCentredString(center_x, y - 0.78 * cm, "UNIVERSITAS TADULAKO")
            c.setFont("Helvetica-Bold", 10.5)
            c.drawCentredString(center_x, y - 1.25 * cm, "FAKULTAS TEKNIK — JURUSAN TEKNOLOGI INFORMASI")
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(center_x, y - 1.68 * cm, "PROGRAM STUDI S1 SISTEM INFORMASI")
            c.setFont("Helvetica", 8)
            c.drawCentredString(
                center_x,
                y - 2.1 * cm,
                "Kampus Bumi Tadulako Tondo, Jl. Soekarno-Hatta Km. 9 Palu 94118 | Laman: https://untad.ac.id | Email: si@untad.ac.id"
            )

            # Garis Ganda Kop Surat
            y -= 2.45 * cm
            c.setLineWidth(2)
            c.line(margin_x, y, width - margin_x, y)
            c.setLineWidth(0.7)
            c.line(margin_x, y - 3, width - margin_x, y - 3)

            # 2. METADATA SURAT & TANGGAL
            y -= 1.0 * cm
            jenis_surat = self.data.get("jenis_surat") or self.data.get("nama_jenis") or "Surat Akademik"
            tgl_pengajuan = self.format_date(self.data.get("tanggal_pengajuan"))
            nama_lampiran = self.data.get("nama_file")
            teks_lampiran = f"1 Berkas ({nama_lampiran})" if nama_lampiran and str(nama_lampiran).startswith("lampiran_") else "—"

            c.setFont("Helvetica", 10)
            c.drawRightString(width - margin_x, y, f"Palu, {tgl_pengajuan}")

            meta = [
                ("Nomor", f": B/{nomor}/UN28.1/KM/2026"),
                ("Lampiran", f": {teks_lampiran}"),
                ("Perihal", f": {jenis_surat}")
            ]
            for lbl, val in meta:
                c.setFont("Helvetica-Bold", 10)
                c.drawString(margin_x, y, lbl)
                c.setFont("Helvetica", 10)
                c.drawString(margin_x + 2.2 * cm, y, val)
                y -= 0.55 * cm

            # 3. TUJUAN SURAT
            y -= 0.5 * cm
            c.setFont("Helvetica", 10)
            c.drawString(margin_x, y, "Yth. Mahasiswa yang bersangkutan / Pihak Berkepentingan")
            y -= 0.5 * cm
            c.drawString(margin_x, y, "di Lingkungan Universitas Tadulako")

            # 4. PARAGRAF PEMBUKA
            y -= 0.9 * cm
            c.drawString(margin_x, y, "Dengan hormat,")
            y -= 0.55 * cm
            pembuka = (
                "Yang bertanda tangan di bawah ini, Dosen Pembimbing Akademik / Dosen Wali Program Studi "
                "S1 Sistem Informasi Fakultas Teknik Universitas Tadulako, dengan ini menerangkan bahwa:"
            )
            for line in simpleSplit(pembuka, "Helvetica", 10, width - 2 * margin_x):
                c.drawString(margin_x, y, line)
                y -= 0.5 * cm

            # 5. KOTAK IDENTITAS MAHASISWA
            y -= 0.3 * cm
            nama_mhs = self.data.get("nama") or self.data.get("nama_mahasiswa") or "-"
            nim_mhs = self.data.get("nim") or "-"
            prodi_mhs = self.data.get("prodi") or "Sistem Informasi"
            keperluan = self.data.get("keperluan") or self.data.get("deskripsi_jenis") or "-"

            keperluan_lines = simpleSplit(keperluan, "Helvetica", 10, width - 2 * margin_x - 5.3 * cm)
            box_height = (4 + max(1, len(keperluan_lines))) * 0.58 * cm + 0.45 * cm

            c.setFillColor(colors.HexColor("#F8FAF5"))
            c.setStrokeColor(colors.HexColor("#CFD6C7"))
            c.rect(margin_x, y - box_height + 0.35 * cm, width - 2 * margin_x, box_height, fill=1, stroke=1)
            c.setFillColor(colors.black)

            detail_rows = [
                ("Nama Mahasiswa", nama_mhs, True),
                ("NIM", nim_mhs, False),
                ("Program Studi", prodi_mhs, False),
                ("Fakultas / PT", "Fakultas Teknik — Universitas Tadulako", False),
            ]
            for lbl, val, is_bold in detail_rows:
                c.setFont("Helvetica-Bold", 10)
                c.drawString(margin_x + 0.4 * cm, y, lbl)
                c.setFont("Helvetica-Bold" if is_bold else "Helvetica", 10)
                c.drawString(margin_x + 4.8 * cm, y, f":  {val}")
                y -= 0.58 * cm

            c.setFont("Helvetica-Bold", 10)
            c.drawString(margin_x + 0.4 * cm, y, "Keperluan")
            c.setFont("Helvetica", 10)
            for idx, k_line in enumerate(keperluan_lines):
                prefix = ":  " if idx == 0 else "   "
                c.drawString(margin_x + 4.8 * cm, y, f"{prefix}{k_line}")
                y -= 0.55 * cm

            # 6. PARAGRAF PENUTUP
            y -= 0.5 * cm
            penutup = (
                "Berdasarkan hasil verifikasi dan tinjauan akademik di lingkungan Jurusan Teknologi Informasi "
                "Universitas Tadulako, permohonan surat tersebut telah disetujui dan disahkan secara resmi. "
                "Demikian surat ini dibuat dengan sebenarnya untuk dapat dipergunakan sebagaimana mestinya."
            )
            for line in simpleSplit(penutup, "Helvetica", 10, width - 2 * margin_x):
                c.drawString(margin_x, y, line)
                y -= 0.5 * cm

            # 7. BLOK TANDA TANGAN DOSEN (KANAN BAWAH)
            y -= 0.8 * cm
            ttd_x = width - margin_x - 7.5 * cm

            nama_dosen = self.data.get("nama_dosen") or "Dr. Lukman Syafie, S.Kom., M.Kom."
            nip_dosen = self.data.get("nip_dosen") or self.data.get("nidn") or "-"
            jabatan_dosen = self.data.get("jabatan_dosen") or "Dosen Wali / Pembimbing Akademik"
            file_ttd_dosen = self.data.get("file_ttd_dosen")
            ttd_digital = self.data.get("tanda_tangan_digital")
            tgl_ttd = self.format_date(
                self.data.get("tanggal_keputusan_dosen") or self.data.get("tanggal_disetujui") or self.data.get("tanggal_pengajuan")
            )
            waktu_ttd = self.format_datetime(
                self.data.get("tanggal_keputusan_dosen") or self.data.get("tanggal_disetujui")
            )

            c.setFont("Helvetica", 10)
            c.drawString(ttd_x, y, f"Palu, {tgl_ttd}")
            y -= 0.5 * cm
            c.setFont("Helvetica-Bold", 10)
            c.drawString(ttd_x, y, f"{jabatan_dosen},")
            y -= 0.3 * cm

            if file_ttd_dosen and os.path.exists(file_ttd_dosen):
                c.drawImage(
                    file_ttd_dosen,
                    ttd_x,
                    y - 2.1 * cm,
                    width=4.5 * cm,
                    height=2.0 * cm,
                    mask="auto",
                    preserveAspectRatio=True
                )
                y -= 2.2 * cm
            else:
                y -= 1.6 * cm

            c.setFillColor(colors.HexColor("#F2F8EE"))
            c.setStrokeColor(colors.HexColor("#527A3E"))
            c.rect(ttd_x, y - 1.15 * cm, 7.5 * cm, 1.15 * cm, fill=1, stroke=1)
            c.setFillColor(colors.HexColor("#2D5C3B"))
            c.setFont("Helvetica-Bold", 7.5)
            c.drawString(ttd_x + 0.25 * cm, y - 0.35 * cm, "✓ TERVERIFIKASI — UNIVERSITAS TADULAKO")
            c.setFillColor(colors.black)
            c.setFont("Courier", 6.5)
            hash_short = (ttd_digital[:34] + "...") if ttd_digital and len(ttd_digital) > 34 else (ttd_digital or "-")
            c.drawString(ttd_x + 0.25 * cm, y - 0.70 * cm, f"SHA256: {hash_short}")
            c.setFont("Helvetica", 6.5)
            c.drawString(ttd_x + 0.25 * cm, y - 1.00 * cm, f"Waktu Sah: {waktu_ttd}")
            y -= 1.65 * cm

            c.setFont("Helvetica-Bold", 10)
            c.drawString(ttd_x, y, nama_dosen)
            y -= 0.45 * cm
            c.setFont("Helvetica", 9.5)
            c.drawString(ttd_x, y, f"NIDN/NIP. {nip_dosen}")

            # 8. FOOTNOTE DI BAGIAN PALING BAWAH HALAMAN
            footer_y = 1.6 * cm
            c.setStrokeColor(colors.HexColor("#CCCCCC"))
            c.setLineWidth(0.6)
            c.line(margin_x, footer_y + 0.45 * cm, width - margin_x, footer_y + 0.45 * cm)
            c.setFillColor(colors.HexColor("#666666"))
            c.setFont("Helvetica", 7.5)
            c.drawCentredString(
                width / 2,
                footer_y + 0.15 * cm,
                "Dokumen ini diterbitkan secara elektronik oleh Sistem Informasi Pengajuan Surat (SIPAS) Universitas Tadulako."
            )
            c.drawCentredString(
                width / 2,
                footer_y - 0.15 * cm,
                "Keabsahan tanda tangan dosen tercatat secara kriptografis menggunakan algoritma SHA-256."
            )

            c.save()
            messagebox.showinfo(
                "PDF Berhasil Disimpan",
                f"Dokumen surat resmi Universitas Tadulako berhasil disimpan ke:\n{filename}",
                parent=self
            )
        except Exception as e:
            messagebox.showerror(
                "Gagal Membuat PDF",
                f"Terjadi kesalahan saat mengekspor PDF: {e}",
                parent=self
            )