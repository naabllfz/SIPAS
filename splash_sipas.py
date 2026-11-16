"""
SIPAS - Splash screen animasi (Tkinter + Pillow)

Animasi logo saat aplikasi dibuka:
tile -> lingkaran -> amplop naik -> surat keluar -> lipatan -> rute pelacakan -> centang terverifikasi
lalu jendela utama muncul dengan efek fade.

Kebutuhan:  pip install pillow

Cara pakai (di file utama aplikasi):

    import tkinter as tk
    from splash_sipas import show_splash

    root = tk.Tk()
    root.withdraw()                      # sembunyikan jendela utama dulu
    # ... bangun seluruh UI seperti biasa ...
    show_splash(root, on_done=root.deiconify)
    root.mainloop()

Klik atau tekan tombol apa saja untuk melewati animasi.
Coba langsung:  python splash_sipas.py
"""
import bisect
import math
import time

try:
    from PIL import Image, ImageChops, ImageDraw, ImageFilter
except ImportError:  # tanpa Pillow splash dilewati, aplikasi tetap jalan
    Image = None

# ----------------------------------------------------------------- palet (dari UI SIPAS)
BG = (23, 59, 53)            # hijau tua sidebar  #173B35
TILE = (246, 244, 236)
TILE_EDGE = (231, 227, 212)
DISC = (241, 237, 227)
DISC_EDGE = (221, 216, 197)
ENVELOPE = (25, 58, 51)
FOLD = (14, 36, 32)
OLIVE = (82, 122, 62)        # hijau zaitun tombol  #527A3E
LEAF = (123, 165, 102)
WHITE = (255, 255, 255)
CARD_EDGE = (230, 226, 212)
GRAY_LINE = (157, 170, 164)
TRACK = (36, 76, 68)
TAGLINE = (176, 200, 188)
FOOTER = (110, 146, 130)

BG_HEX = "#173B35"

# ----------------------------------------------------------------- timeline (detik)
T = dict(
    tile=(0.00, 0.55),
    disc=(0.25, 0.75),
    body=(0.55, 1.05),
    letter=(0.90, 1.45),
    flap=(1.05, 1.55),
    lines=(1.35, 1.75),
    fold=(1.45, 1.80),
    dot=(1.65, 2.00),
    route=(1.60, 2.45),
    badge=(2.40, 2.90),
    check=(2.60, 2.95),
    ripple=(2.65, 3.20),
    word=(1.20, 1.85),
    tagline=(1.60, 2.20),
    bar=(0.20, 3.05),
)
HOLD_UNTIL = 3.35            # animasi selesai, mulai fade out


# ----------------------------------------------------------------- easing
def _clamp(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def _prog(t, a, b):
    return _clamp((t - a) / (b - a))


def _out_cubic(x):
    return 1 - (1 - x) ** 3


def _in_out(x):
    return x * x * (3 - 2 * x)


def _out_back(x, s=1.70158):
    x -= 1
    return 1 + x * x * ((s + 1) * x + s)


def _mix(a, b, t):
    t = _clamp(t)
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def _hex(c):
    return "#%02x%02x%02x" % tuple(c)


def _partial(pts, p):
    """Titik-titik polyline sampai fraksi p dari total panjangnya."""
    segs = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    target = sum(segs) * p
    out, acc = [pts[0]], 0.0
    for (a, b), ln in zip(zip(pts, pts[1:]), segs):
        if acc + ln <= target:
            out.append(b)
            acc += ln
        else:
            r = (target - acc) / ln
            out.append((a[0] + (b[0] - a[0]) * r, a[1] + (b[1] - a[1]) * r))
            break
    return out


# ----------------------------------------------------------------- renderer logo
class LogoRenderer:
    """Menggambar logo SIPAS pada waktu t (detik). Koordinat desain 1024x1024."""

    SS = 2          # supersampling untuk tepi halus
    MARGIN = 64     # ruang di sekeliling tile supaya efek pop tidak terpotong

    def __init__(self, size):
        self.n = size
        self.N = size * self.SS
        self.k = self.N / (1024 + 2 * self.MARGIN)
        self._shadow = self._make_shadow()
        # rute pelacakan: kurva bezier di bawah amplop
        p0, p1, p2 = (350, 810), (512, 862), (672, 810)
        self.route = []
        for i in range(241):
            u = i / 240
            a, b, c = (1 - u) ** 2, 2 * u * (1 - u), u * u
            self.route.append((a * p0[0] + b * p1[0] + c * p2[0],
                               a * p0[1] + b * p1[1] + c * p2[1]))
        self.cum = [0.0]
        for a, b in zip(self.route, self.route[1:]):
            self.cum.append(self.cum[-1] + math.dist(a, b))
        self.route_len = self.cum[-1]

    # -- util geometri
    def _xf(self, s=1.0, dx=0.0, dy=0.0, pivot=(512.0, 512.0)):
        px, py = pivot
        k, m = self.k, self.MARGIN

        def f(x, y):
            return ((px + (x - px) * s + dx + m) * k, (py + (y - py) * s + dy + m) * k)
        return f

    def _rr(self, d, xf, s, box, r, fill, outline=None, width=0):
        (ax, ay), (bx, by) = xf(box[0], box[1]), xf(box[2], box[3])
        kw = {}
        if outline is not None:
            kw = dict(outline=outline, width=max(1, round(width * s * self.k)))
        d.rounded_rectangle([ax, ay, bx, by], radius=r * s * self.k, fill=fill, **kw)

    def _circle(self, d, xf, s, cx, cy, r, fill, outline=None, width=0):
        x, y = xf(cx, cy)
        rr = r * s * self.k
        kw = {}
        if outline is not None:
            kw = dict(outline=outline, width=max(1, round(width * s * self.k)))
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=fill, **kw)

    def _stroke(self, d, xf, s, pts, w, color):
        q = [xf(*p) for p in pts]
        wd = max(1, round(w * s * self.k))
        r = wd / 2.0
        for a, b in zip(q, q[1:]):
            d.line([a, b], fill=color, width=wd)
        for x, y in q:
            d.ellipse([x - r, y - r, x + r, y + r], fill=color)

    def _layer(self, img, alpha, painter):
        """Gambar dengan transparansi (untuk elemen di atas latar tidak seragam)."""
        if alpha <= 0.003:
            return
        if alpha >= 0.997:
            painter(ImageDraw.Draw(img))
            return
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        painter(ImageDraw.Draw(lay))
        mask = lay.getchannel("A").point(lambda v: int(v * alpha))
        img.paste(lay, (0, 0), mask)

    def _make_shadow(self):
        k, m = self.k, self.MARGIN
        lay = Image.new("L", (self.N, self.N), 0)
        d = ImageDraw.Draw(lay)
        d.rounded_rectangle([(282 + m) * k, (392 + 28 + m) * k, (742 + m) * k, (692 + 28 + m) * k],
                            radius=44 * k, fill=255)
        return lay.filter(ImageFilter.GaussianBlur(26 * k))

    def _route_pt(self, ln):
        ln = max(0.0, min(self.route_len, ln))
        i = bisect.bisect_right(self.cum, ln) - 1
        i = min(i, len(self.route) - 2)
        seg = self.cum[i + 1] - self.cum[i]
        r = 0 if seg == 0 else (ln - self.cum[i]) / seg
        a, b = self.route[i], self.route[i + 1]
        return (a[0] + (b[0] - a[0]) * r, a[1] + (b[1] - a[1]) * r)

    # -- satu frame
    def render(self, t):
        img = Image.new("RGB", (self.N, self.N), BG)
        d = ImageDraw.Draw(img)

        # 1. tile aplikasi (kartu krem)
        p = _prog(t, *T["tile"])
        if p > 0:
            s = 0.72 + 0.28 * _out_back(p)
            a = _clamp(p / 0.6)
            xf = self._xf(s)
            col = _mix(BG, TILE, a)
            self._rr(d, xf, s, (0, 0, 1024, 1024), 230, col)
            self._rr(d, xf, s, (14, 14, 1010, 1010), 216, None, _mix(col, TILE_EDGE, a), 7)

        # 2. lingkaran dalam
        p = _prog(t, *T["disc"])
        if p > 0:
            s = 0.8 + 0.2 * _out_back(p)
            a = _clamp(p / 0.5)
            xf = self._xf(s)
            self._circle(d, xf, s, 512, 512, 437, _mix(TILE, DISC, a), _mix(TILE, DISC_EDGE, a), 6)

        # 3. bayangan + badan amplop
        p = _prog(t, *T["body"])
        if p > 0:
            sh = _clamp((p - 0.6) / 0.4) * 0.20
            if sh > 0:
                mask = self._shadow.point(lambda v, f=sh: int(v * f))
                img.paste(FOLD, (0, 0), mask)
            s = 0.72 + 0.28 * _out_back(p)
            dy = 36 * (1 - _out_cubic(p))
            a = _clamp(p / 0.5)
            xf = self._xf(s, dy=dy, pivot=(512, 542))
            self._rr(d, xf, s, (282, 392, 742, 692), 44, _mix(DISC, ENVELOPE, a))

        # 4. surat keluar dari amplop
        p = _prog(t, *T["letter"])
        ldy = 80 * (1 - _out_cubic(p))
        if p > 0:
            xf = self._xf(dy=ldy)

            def paint_card(dr):
                self._rr(dr, xf, 1, (342, 332, 684, 472), 24, WHITE, CARD_EDGE, 3)
            self._layer(img, _clamp(p / 0.55), paint_card)

        # 5. dua garis teks pada surat "tertulis"
        xf = self._xf(dy=ldy)
        p1 = _out_cubic(_prog(t, T["lines"][0], T["lines"][0] + 0.30))
        p2 = _out_cubic(_prog(t, T["lines"][0] + 0.12, T["lines"][1]))
        if p1 > 0:
            self._stroke(d, xf, 1, [(386, 376), (386 + 132 * p1, 376)], 13, OLIVE)
        if p2 > 0:
            self._stroke(d, xf, 1, [(386, 408), (386 + 211 * p2, 408)], 11, GRAY_LINE)

        # 6. lipatan amplop (V hijau) tergambar
        p = _in_out(_prog(t, *T["flap"]))
        if p > 0:
            pts = _partial([(278, 390), (512, 572), (746, 390)], p)
            self._stroke(d, self._xf(), 1, pts, 26, OLIVE)

        # 7. garis lipatan bawah
        p = _out_cubic(_prog(t, *T["fold"]))
        if p > 0:
            xf = self._xf()
            self._stroke(d, xf, 1, _partial([(282, 692), (440, 552)], p), 14, FOLD)
            self._stroke(d, xf, 1, _partial([(742, 692), (582, 552)], p), 14, FOLD)

        # 8. titik status
        s = _out_back(_prog(t, *T["dot"]))
        if s > 0.01:
            xf = self._xf()
            self._circle(d, xf, s, 350, 632, 24, WHITE)
            self._circle(d, xf, s, 350, 632, 17, LEAF)

        # 9. rute pelacakan (garis putus-putus) + titik kepala yang bergerak
        pr = _in_out(_prog(t, *T["route"]))
        if pr > 0:
            xf = self._xf()
            cut = pr * self.route_len
            for i in range(8):
                a0 = i * 40.0
                a1 = min(a0 + 18.0, cut)
                if a1 > a0:
                    m = max(2, int((a1 - a0) / 3) + 1)
                    pts = [self._route_pt(a0 + (a1 - a0) * j / (m - 1)) for j in range(m)]
                    self._stroke(d, xf, 1, pts, 12, OLIVE)
            if pr < 1:
                hx, hy = self._route_pt(cut)
                self._circle(d, xf, 1, hx, hy, 15, WHITE)
                self._circle(d, xf, 1, hx, hy, 10, LEAF)
            else:
                e = _out_back(_prog(t, T["route"][1], T["route"][1] + 0.25))
                ex, ey = self.route[-1]
                self._circle(d, xf, max(e, 0.01), ex, ey, 9, OLIVE)

        # 10. gelombang + lencana centang (surat terverifikasi)
        p = _prog(t, *T["ripple"])
        if 0 < p < 1:
            xf = self._xf()
            rad = 64 + 90 * _out_cubic(p)
            wd = 8 * (1 - p) + 1

            def paint_ripple(dr):
                self._circle(dr, xf, 1, 672, 384, rad, None, OLIVE, wd)
            self._layer(img, 0.5 * (1 - p), paint_ripple)

        s = _out_back(_prog(t, *T["badge"]))
        if s > 0.01:
            xf = self._xf(s, pivot=(672, 384))
            self._circle(d, xf, s, 672, 384, 64, TILE)
            self._circle(d, xf, s, 672, 384, 50, OLIVE)
            pc = _out_cubic(_prog(t, *T["check"]))
            if pc > 0:
                self._stroke(d, xf, s, _partial([(650, 383), (666, 399), (696, 370)], pc), 12, WHITE)

        return img.reduce(self.SS)


# ----------------------------------------------------------------- jendela splash (Tkinter)
class _Splash:
    def __init__(self, root, on_done, duration, fade, skippable):
        import tkinter as tk
        from PIL import ImageTk
        self._tk, self._ImageTk = tk, ImageTk
        self.root, self.on_done, self.fade = root, on_done, fade
        self.speed = HOLD_UNTIL / max(0.5, duration)
        self.fading = False
        self.alive = True

        try:
            ui = max(1.0, root.winfo_fpixels("1i") / 96.0)
        except Exception:
            ui = 1.0
        self.ui = ui
        W, H = int(520 * ui), int(610 * ui)
        L = int(380 * ui)

        win = self.win = tk.Toplevel(root)
        win.withdraw()
        win.overrideredirect(True)
        win.configure(bg=BG_HEX)
        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        win.geometry(f"{W}x{H}+{(sw - W) // 2}+{(sh - H) // 2}")
        win.attributes("-topmost", True)

        cv = self.cv = tk.Canvas(win, width=W, height=H, bg=BG_HEX, highlightthickness=0, bd=0)
        cv.pack()

        self.logo = LogoRenderer(L)
        self.photo = ImageTk.PhotoImage(self.logo.render(0))
        self.img_item = cv.create_image((W - L) // 2, int(24 * ui), image=self.photo, anchor="nw")

        self.y_word = int(446 * ui)
        self.slide = int(14 * ui)
        fam = "Segoe UI"
        self.t_word = cv.create_text(W // 2, self.y_word, text="SIPAS", fill=BG_HEX,
                                     font=(fam, -int(38 * ui), "bold"))
        self.t_tag = cv.create_text(W // 2, int(490 * ui), text="Layanan pengajuan surat akademik",
                                    fill=BG_HEX, font=(fam, -int(15 * ui)))
        bw, bh, by = int(200 * ui), max(2, int(3 * ui)), int(540 * ui)
        self.bar_x0, self.bar_w, self.bar_y, self.bar_h = (W - bw) // 2, bw, by, bh
        cv.create_rectangle(self.bar_x0, by, self.bar_x0 + bw, by + bh, fill=_hex(TRACK), width=0)
        self.bar = cv.create_rectangle(self.bar_x0, by, self.bar_x0, by + bh, fill=_hex(LEAF), width=0)
        self.t_foot = cv.create_text(W // 2, int(584 * ui), text="PORTAL LAYANAN AKADEMIK  •  2026",
                                     fill=BG_HEX, font=(fam, -int(10 * ui), "bold"))

        if skippable:
            win.bind("<Button-1>", self._skip)
            win.bind("<Key>", self._skip)
        win.update_idletasks()
        win.deiconify()
        win.lift()
        try:
            win.focus_force()
        except Exception:
            pass
        win.update()
        self.start = time.perf_counter()
        self._tick()

    def _skip(self, _e=None):
        if not self.fading:
            self.start = time.perf_counter() - HOLD_UNTIL / self.speed

    def _finish(self):
        if not self.alive:
            return
        self.alive = False
        try:
            self.win.destroy()
        except Exception:
            pass

    def _tick(self):
        if not self.alive:
            return
        t0 = time.perf_counter()
        t = (t0 - self.start) * self.speed

        if t >= HOLD_UNTIL and not self.fading:
            self.fading = True
            self.fade_t0 = t0
            if self.on_done:
                try:
                    self.on_done()
                except Exception:
                    self._finish()
                    raise
        if self.fading:
            a = 1.0 - (t0 - self.fade_t0) / max(0.05, self.fade)
            if a <= 0:
                self._finish()
                return
            try:
                self.win.attributes("-alpha", a)
            except Exception:
                pass

        tt = min(t, HOLD_UNTIL)
        self.photo = self._ImageTk.PhotoImage(self.logo.render(tt))
        cv = self.cv
        cv.itemconfigure(self.img_item, image=self.photo)

        e = _prog(tt, *T["word"])
        cv.itemconfigure(self.t_word, fill=_hex(_mix(BG, WHITE, _out_cubic(e) * 1.0)))
        cv.coords(self.t_word, cv.coords(self.t_word)[0], self.y_word + self.slide * (1 - _out_cubic(e)))
        e = _out_cubic(_prog(tt, *T["tagline"]))
        cv.itemconfigure(self.t_tag, fill=_hex(_mix(BG, TAGLINE, e)))
        cv.itemconfigure(self.t_foot, fill=_hex(_mix(BG, FOOTER, e)))
        pb = _in_out(_prog(tt, *T["bar"]))
        cv.coords(self.bar, self.bar_x0, self.bar_y, self.bar_x0 + self.bar_w * pb, self.bar_y + self.bar_h)

        used = int((time.perf_counter() - t0) * 1000)
        self.win.after(max(1, 15 - used), self._tick)


def show_splash(root, on_done=None, duration=HOLD_UNTIL, fade=0.35, skippable=True):
    """Tampilkan splash animasi SIPAS.

    root      : jendela utama Tk (sebaiknya sudah di-withdraw())
    on_done   : dipanggil saat fade-out dimulai, misalnya root.deiconify
    duration  : lama animasi dalam detik (default 3,35 dtk)
    fade      : lama fade-out dalam detik
    skippable : klik / tekan tombol apa saja untuk melewati
    """
    if Image is None:
        print("[splash_sipas] Pillow belum terpasang (pip install pillow), splash dilewati.")
        if on_done:
            on_done()
        return None
    return _Splash(root, on_done, duration, fade, skippable)


if __name__ == "__main__":
    import tkinter as tk

    demo = tk.Tk()
    demo.title("SIPAS | demo splash")
    demo.geometry("900x560")
    demo.configure(bg="#F4F3EA")
    tk.Label(demo, text="Di sinilah jendela utama aplikasi muncul", bg="#F4F3EA", fg=BG_HEX,
             font=("Segoe UI", 18, "bold")).pack(expand=True)
    demo.withdraw()
    show_splash(demo, on_done=demo.deiconify)
    demo.mainloop()
