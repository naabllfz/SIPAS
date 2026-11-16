import sys
import os
from PIL import Image, ImageTk

_CACHE = {}


def get_asset_path(filename="screen.png"):
    """
    Mengambil path absolut file asset, mendukung mode development
    maupun mode executable PyInstaller (melalui sys._MEIPASS).
    """
    # 1. Jika berjalan dari paket PyInstaller
    if hasattr(sys, "_MEIPASS"):
        bundle_path = os.path.join(sys._MEIPASS, filename)
        if os.path.exists(bundle_path):
            return bundle_path

    # 2. Lokasi saat development
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sipas_dir = os.path.dirname(current_dir)
    parent_dir = os.path.dirname(sipas_dir)

    candidates = [
        os.path.join(sipas_dir, filename),
        os.path.join(sipas_dir, "assets", filename),
        os.path.join(parent_dir, filename),
        os.path.join(current_dir, filename),
        os.path.abspath(filename),
    ]

    for path in candidates:
        if os.path.exists(path):
            return path

    return filename


def get_pil_image(filename="screen.png"):
    """Mengembalikan objek PIL Image yang valid jika ada."""
    path = get_asset_path(filename)
    if os.path.exists(path):
        try:
            return Image.open(path)
        except Exception as e:
            print(f"[image_loader] Gagal membuka {path}: {e}")
    return None


def load_logo_image(size=(44, 44), filename="screen.png"):
    """
    Memuat logo screen.png dengan ukuran tertentu dan mengembalikan PhotoImage.
    Menyimpan cache agar referensi gambar tidak terhapus oleh garbage collector Tkinter.
    """
    cache_key = (filename, size[0], size[1])
    if cache_key in _CACHE:
        return _CACHE[cache_key]

    path = get_asset_path(filename)
    if not os.path.exists(path):
        return None

    try:
        pil_img = Image.open(path)
        if pil_img.mode != "RGBA":
            pil_img = pil_img.convert("RGBA")

        # Gunakan filter LANCZOS untuk resampling terbaik
        resized = pil_img.resize(size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(resized)
        _CACHE[cache_key] = photo
        return photo
    except Exception as e:
        print(f"[image_loader] Gagal memuat logo ({size}): {e}")
        return None


def set_window_icon(window):
    """
    Memasang icon aplikasi pada jendela Tkinter (baik melalui iconbitmap .ico maupun iconphoto .png).
    """
    # 1. Coba pasang .ico untuk Windows taskbar
    ico_path = get_asset_path("app.ico")
    if os.path.exists(ico_path):
        try:
            window.iconbitmap(ico_path)
        except Exception:
            pass

    # 2. Pasang PhotoImage dari screen.png
    photo = load_logo_image((64, 64), "screen.png")
    if photo:
        try:
            window.iconphoto(True, photo)
        except Exception:
            pass
