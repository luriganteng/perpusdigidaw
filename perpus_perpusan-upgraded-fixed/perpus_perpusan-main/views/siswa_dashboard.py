import tkinter as tk
from tkinter import ttk
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

COLORS = {
    "bg":         "#F0F8F4",   # hijau sangat muda (beda dari admin)
    "sidebar":    "#1E6B45",   # hijau tua
    "sidebar_h":  "#2E9E65",
    "accent":     "#E8A020",
    "accent_d":   "#C4841A",
    "card":       "#FFFFFF",
    "text":       "#1C2B3A",
    "text_muted": "#6B7E8F",
    "danger":     "#D94040",
    "success":    "#2E9E5E",
    "warning":    "#E07B1A",
    "border":     "#C8E0D4",
    "header":     "#124530",
    "sidebar_txt":"#A8D4BC",
    "siswa_clr":  "#2E9E5E",
}

FONT_HEAD  = ("Segoe UI", 13, "bold")
FONT_BODY  = ("Segoe UI", 11)
FONT_SMALL = ("Segoe UI", 9)
FONT_BTN   = ("Segoe UI", 10, "bold")
FONT_NAV   = ("Segoe UI", 11)


class SiswaDashboard:
    def __init__(self, root, siswa, on_logout):
        self.root = root
        self.siswa = siswa
        self.on_logout = on_logout
        self.nav_buttons = {}
        self.current_page = None

        root.title(f"Perpustakaan Digital – {siswa['nama']}")
        root.configure(bg=COLORS["bg"])
        try:
            root.state("zoomed")
        except Exception:
            root.geometry("1100x680")

        self._build()

    def _build(self):
        # ── Sidebar ─────────────────────────────────────────────
        self.sidebar = tk.Frame(self.root, bg=COLORS["sidebar"], width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        logo = tk.Frame(self.sidebar, bg=COLORS["header"], height=70)
        logo.pack(fill="x")
        logo.pack_propagate(False)
        tk.Label(logo, text="📚 PerpusDigi",
                 font=("Segoe UI", 13, "bold"),
                 bg=COLORS["header"], fg=COLORS["accent"],
                 anchor="w", padx=16).pack(fill="both", expand=True)

        # Info siswa
        info = tk.Frame(self.sidebar, bg=COLORS["sidebar"], pady=8)
        info.pack(fill="x")
        tk.Label(info, text=f"🎒 {self.siswa['nama']}",
                 font=("Segoe UI", 10, "bold"),
                 bg=COLORS["sidebar"], fg="#FFFFFF",
                 anchor="w", padx=16, wraplength=190).pack(fill="x")
        jenjang = self.siswa.get('jenjang') or '-'
        kelas = self.siswa.get('kelas') or '-'
        nis = self.siswa.get('nis') or 'belum dilengkapi'
        if jenjang == '-' and kelas == '-':
            info_text = f"   NIS: {nis}"
        else:
            info_text = f"   {jenjang} {kelas}  |  NIS: {nis}"
        tk.Label(info, text=info_text,
                 font=FONT_SMALL, bg=COLORS["sidebar"],
                 fg=COLORS["sidebar_txt"], anchor="w", padx=16).pack(fill="x")

        tk.Frame(self.sidebar, bg=COLORS["sidebar_h"],
                 height=1).pack(fill="x", padx=16, pady=6)

        # Nav
        nav_items = [
            ("🏠", "Beranda",          "beranda"),
            ("📖", "Cari & Pinjam Buku","cari_buku"),
            ("🔄", "Pinjaman Aktif",   "pinjaman_aktif"),
            ("📋", "Riwayat Pinjaman", "riwayat"),
        ]
        self.nav_frame = tk.Frame(self.sidebar, bg=COLORS["sidebar"])
        self.nav_frame.pack(fill="both", expand=True)

        for icon, label, key in nav_items:
            btn = self._nav_btn(self.nav_frame, icon, label, key)
            self.nav_buttons[key] = btn

        # Logout
        bottom = tk.Frame(self.sidebar, bg=COLORS["sidebar"], pady=10)
        bottom.pack(fill="x", side="bottom")
        tk.Frame(bottom, bg=COLORS["sidebar_h"],
                 height=1).pack(fill="x", padx=16, pady=(0, 8))
        tk.Button(bottom, text="⬅ Keluar",
                  font=FONT_NAV, bg=COLORS["sidebar"],
                  fg=COLORS["sidebar_txt"],
                  activebackground=COLORS["danger"],
                  activeforeground="#fff",
                  relief="flat", cursor="hand2",
                  anchor="w", padx=16, pady=8,
                  command=self.on_logout).pack(fill="x")

        # ── Content ─────────────────────────────────────────────
        self.content = tk.Frame(self.root, bg=COLORS["bg"])
        self.content.pack(side="right", fill="both", expand=True)

        self.navigate("beranda")

    def _nav_btn(self, parent, icon, label, key):
        frame = tk.Frame(parent, bg=COLORS["sidebar"], cursor="hand2")
        frame.pack(fill="x")

        def on_click():
            self.navigate(key)

        def on_enter(e):
            if self.current_page != key:
                frame.configure(bg=COLORS["sidebar_h"])
                lbl.configure(bg=COLORS["sidebar_h"])

        def on_leave(e):
            if self.current_page != key:
                frame.configure(bg=COLORS["sidebar"])
                lbl.configure(bg=COLORS["sidebar"])

        lbl = tk.Label(frame, text=f"  {icon}  {label}",
                       font=FONT_NAV, bg=COLORS["sidebar"],
                       fg=COLORS["sidebar_txt"],
                       anchor="w", pady=10, padx=8)
        lbl.pack(fill="x")

        for w in [frame, lbl]:
            w.bind("<Button-1>", lambda e: on_click())
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

        return (frame, lbl)

    def set_active_nav(self, key):
        for k, (frame, lbl) in self.nav_buttons.items():
            if k == key:
                frame.configure(bg=COLORS["accent"])
                lbl.configure(bg=COLORS["accent"], fg=COLORS["text"])
            else:
                frame.configure(bg=COLORS["sidebar"])
                lbl.configure(bg=COLORS["sidebar"], fg=COLORS["sidebar_txt"])

    def navigate(self, page_key):
        for w in self.content.winfo_children():
            w.destroy()
        self.current_page = page_key
        self.set_active_nav(page_key)

        if page_key == "beranda":
            from views.siswa_beranda import SiswaBeranda
            SiswaBeranda(self.content, self.siswa, self.navigate)
        elif page_key == "cari_buku":
            from views.siswa_cari_buku import SiswaCariPinjam
            SiswaCariPinjam(self.content, self.siswa)
        elif page_key == "pinjaman_aktif":
            from views.siswa_pinjaman import SiswaPinjamanAktif
            SiswaPinjamanAktif(self.content, self.siswa)
        elif page_key == "riwayat":
            from views.siswa_riwayat import SiswaRiwayat
            SiswaRiwayat(self.content, self.siswa)
