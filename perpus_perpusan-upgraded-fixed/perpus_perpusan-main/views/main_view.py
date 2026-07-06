import tkinter as tk
from tkinter import ttk
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

COLORS = {
    "bg":         "#F0F4F8",
    "sidebar":    "#2F4E6D",
    "sidebar_h":  "#2A5F8F",
    "accent":     "#E8A020",
    "accent_d":   "#C4841A",
    "card":       "#FFFFFF",
    "text":       "#1C2B3A",
    "text_muted": "#6B7E8F",
    "danger":     "#C46C6C",
    "success":    "#1FAC5C",
    "warning":    "#E07B1A",
    "border":     "#D0DCE8",
    "header":     "#12263D",
    "row_alt":    "#F7FAFC",
    "sidebar_txt":"#AECDE0",
}

FONT_HEAD  = ("Segoe UI", 13, "bold")
FONT_BODY  = ("Segoe UI", 11)
FONT_SMALL = ("Segoe UI", 9)
FONT_BTN   = ("Segoe UI", 10, "bold")
FONT_NAV   = ("Segoe UI", 11)


class MainDashboard:
    def __init__(self, root, admin, on_logout):
        self.root = root
        self.admin = admin
        self.on_logout = on_logout
        self.current_page = None
        self.nav_buttons = {}

        root.title(f"Perpustakaan Digital – {admin['nama']}")
        root.configure(bg=COLORS["bg"]) # Set background color
        root.state("zoomed")  # fullscreen on windows; fallback below
        try:
            root.state("zoomed")
        except Exception:
            root.geometry("1200x720")

        self._build()

    def _build(self):
        # ── Sidebar ────────────────────────────────────────────────
        self.sidebar = tk.Frame(self.root, bg=COLORS["sidebar"], width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo area
        logo_frame = tk.Frame(self.sidebar, bg=COLORS["header"], height=70)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)
        tk.Label(logo_frame, text="📚 PerpusDigi",
                 font=("Segoe UI", 13, "bold"),
                 bg=COLORS["header"], fg=COLORS["accent"],
                 anchor="w", padx=16).pack(fill="both", expand=True)

        # Admin info
        info = tk.Frame(self.sidebar, bg=COLORS["sidebar"], pady=10)
        info.pack(fill="x")
        tk.Label(info, text=f"👤 {self.admin['nama']}",
                 font=FONT_SMALL, bg=COLORS["sidebar"],
                 fg=COLORS["sidebar_txt"], anchor="w",
                 padx=16, wraplength=180).pack(fill="x")

        sep = tk.Frame(self.sidebar, bg=COLORS["sidebar_h"], height=1)
        sep.pack(fill="x", padx=16, pady=6)

        # Nav items
        nav_items = [
            ("🏠", "Dashboard",    "dashboard"),
            ("📖", "Daftar Buku",  "buku"),
            ("👥", "Data Siswa",   "siswa"),
            ("🔄", "Peminjaman",   "peminjaman"),
            ("⏰", "Keterlambatan","terlambat"),
            ("📊", "Laporan",      "laporan"),
        ]
        self.nav_frame = tk.Frame(self.sidebar, bg=COLORS["sidebar"])
        self.nav_frame.pack(fill="both", expand=True)

        for icon, label, key in nav_items:
            btn = self._nav_btn(self.nav_frame, icon, label, key)
            self.nav_buttons[key] = btn

        # Logout at bottom
        bottom = tk.Frame(self.sidebar, bg=COLORS["sidebar"], pady=10)
        bottom.pack(fill="x", side="bottom")
        sep2 = tk.Frame(bottom, bg=COLORS["sidebar_h"], height=1)
        sep2.pack(fill="x", padx=16, pady=(0, 8))
        logout_btn = tk.Button(bottom, text="⬅ Keluar",
                               font=FONT_NAV, bg=COLORS["sidebar"],
                               fg=COLORS["sidebar_txt"],
                               activebackground=COLORS["danger"],
                               activeforeground="#fff",
                               relief="flat", cursor="hand2",
                               anchor="w", padx=16, pady=8,
                               command=self.on_logout)
        logout_btn.pack(fill="x")

        # ── Content area ───────────────────────────────────────────
        self.content = tk.Frame(self.root, bg=COLORS["bg"])
        self.content.pack(side="right", fill="both", expand=True)

        # Navigate to dashboard by default
        self.navigate("dashboard")

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

        lbl = tk.Label(frame,
                       text=f"  {icon}  {label}",
                       font=FONT_NAV,
                       bg=COLORS["sidebar"],
                       fg=COLORS["sidebar_txt"],
                       anchor="w", pady=10, padx=8)
        lbl.pack(fill="x")

        frame.bind("<Button-1>", lambda e: on_click())
        lbl.bind("<Button-1>", lambda e: on_click())
        frame.bind("<Enter>", on_enter)
        frame.bind("<Leave>", on_leave)
        lbl.bind("<Enter>", on_enter)
        lbl.bind("<Leave>", on_leave)

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
        # Destroy current content
        for w in self.content.winfo_children():
            w.destroy()
        self.current_page = page_key
        self.set_active_nav(page_key)

        # Lazy import pages
        if page_key == "dashboard":
            from views.dashboard_page import DashboardPage
            DashboardPage(self.content, self.admin, self.navigate)
        elif page_key == "buku":
            from views.buku_page import BukuPage
            BukuPage(self.content, self.admin)
        elif page_key == "siswa":
            from views.siswa_page import SiswaPage
            SiswaPage(self.content, self.admin)
        elif page_key == "peminjaman":
            from views.peminjaman_page import PeminjamanPage
            PeminjamanPage(self.content, self.admin)
        elif page_key == "terlambat":
            from views.terlambat_page import TerlambatPage
            TerlambatPage(self.content)
        elif page_key == "laporan":
            from views.laporan_page import LaporanPage
            LaporanPage(self.content)
