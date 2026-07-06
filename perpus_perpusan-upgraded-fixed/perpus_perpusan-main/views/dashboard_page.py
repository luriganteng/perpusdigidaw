import tkinter as tk
from tkinter import ttk
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.database import LaporanModel, PeminjamanModel
from views.widgets import (COLORS, FONT_HEAD, FONT_BODY, FONT_SMALL,
                            page_header, stat_card, card, action_btn)
from datetime import datetime


class DashboardPage:
    def __init__(self, parent, admin, navigate):
        self.parent = parent
        self.admin = admin
        self.navigate = navigate
        self._build()

    def _build(self):
        page_header(self.parent,
                    f"Selamat datang, {self.admin['nama']} 👋",
                    datetime.now().strftime("%d %B %Y  •  Perpustakaan Digital Sekolah"))

        scroll_canvas = tk.Canvas(self.parent, bg=COLORS["bg"],
                                  highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.parent, orient="vertical",
                                   command=scroll_canvas.yview)
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        scroll_canvas.pack(fill="both", expand=True)

        body = tk.Frame(scroll_canvas, bg=COLORS["bg"])
        body_id = scroll_canvas.create_window((0, 0), window=body, anchor="nw")

        def on_configure(e):
            scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))

        def on_canvas_resize(e):
            scroll_canvas.itemconfig(body_id, width=e.width)

        body.bind("<Configure>", on_configure)
        scroll_canvas.bind("<Configure>", on_canvas_resize)

        # Bind mousewheel
        def _on_mousewheel(e):
            scroll_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        scroll_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self._build_stats(body)
        self._build_quick_actions(body)
        self._build_recent_loans(body)
        self._build_overdue(body)

    def _build_stats(self, parent):
        stats = LaporanModel.statistik_umum()

        section = tk.Frame(parent, bg=COLORS["bg"])
        section.pack(fill="x", padx=24, pady=(20, 8))

        tk.Label(section, text="Ringkasan", font=FONT_HEAD,
                 bg=COLORS["bg"], fg=COLORS["sidebar"]).pack(anchor="w", pady=(0, 10))

        grid = tk.Frame(section, bg=COLORS["bg"])
        grid.pack(fill="x")

        items = [
            ("Total Judul Buku",    stats["total_judul"],       COLORS["sidebar"],  "📚"),
            ("Total Eksemplar",     stats["total_buku"],        "#5B6FA6",          "🗂"),
            ("Siswa Terdaftar",     stats["total_siswa"],       COLORS["success"],  "👥"),
            ("Sedang Dipinjam",     stats["total_pinjam_aktif"],COLORS["accent"],   "🔄"),
            ("Sudah Dikembalikan",  stats["total_dikembalikan"],COLORS["text_muted"],"✅"),
            ("Terlambat",           stats["total_terlambat"],   COLORS["danger"],   "⚠"),
        ]

        for i, (label, value, color, icon) in enumerate(items):
            sc = stat_card(grid, label, value, color, icon)
            sc.grid(row=0, column=i, padx=6, pady=4, sticky="nsew")
            grid.columnconfigure(i, weight=1)

    def _build_quick_actions(self, parent):
        section = tk.Frame(parent, bg=COLORS["bg"])
        section.pack(fill="x", padx=24, pady=(12, 4))

        tk.Label(section, text="Aksi Cepat", font=FONT_HEAD,
                 bg=COLORS["bg"], fg=COLORS["sidebar"]).pack(anchor="w", pady=(0, 10))

        row = tk.Frame(section, bg=COLORS["bg"])
        row.pack(fill="x")

        actions = [
            ("➕  Tambah Buku",      "buku",       "primary"),
            ("👤  Tambah Siswa",     "siswa",      "primary"),
            ("🔄  Catat Peminjaman", "peminjaman", "success"),
            ("⏰  Cek Keterlambatan","terlambat",  "warning"),
            ("📊  Lihat Laporan",    "laporan",    "secondary"),
        ]

        for label, page, kind in actions:
            btn = action_btn(row, label,
                             lambda p=page: self.navigate(p),
                             kind=kind)
            btn.pack(side="left", padx=(0, 8))

    def _build_recent_loans(self, parent):
        section = tk.Frame(parent, bg=COLORS["bg"])
        section.pack(fill="x", padx=24, pady=(16, 4))

        tk.Label(section, text="Peminjaman Terbaru", font=FONT_HEAD,
                 bg=COLORS["bg"], fg=COLORS["sidebar"]).pack(anchor="w", pady=(0, 10))

        from views.widgets import build_treeview
        cols = ["Siswa", "NIS", "Buku", "Tgl Pinjam", "Wajib Kembali", "Status"]
        widths = {"Siswa": 160, "NIS": 90, "Buku": 200,
                  "Tgl Pinjam": 110, "Wajib Kembali": 120, "Status": 100}

        frame, tree = build_treeview(section, cols, widths, height=8)
        frame.pack(fill="x")

        from models.database import PeminjamanModel
        loans = PeminjamanModel.get_all()[:10]
        for i, p in enumerate(loans):
            tag = "alt" if i % 2 else ""
            status = p["status"].capitalize()
            tree.insert("", "end", values=(
                p["nama_siswa"], p["nis"], p["judul_buku"],
                p["tgl_pinjam"], p["tgl_kembali_rencana"], status
            ), tags=(tag,))

    def _build_overdue(self, parent):
        terlambat = PeminjamanModel.get_terlambat()
        if not terlambat:
            return

        section = tk.Frame(parent, bg=COLORS["bg"])
        section.pack(fill="x", padx=24, pady=(16, 20))

        hdr = tk.Frame(section, bg=COLORS["bg"])
        hdr.pack(fill="x", pady=(0, 10))
        tk.Label(hdr, text="⚠  Keterlambatan Aktif",
                 font=FONT_HEAD, bg=COLORS["bg"],
                 fg=COLORS["danger"]).pack(side="left")
        tk.Label(hdr, text=f"  ({len(terlambat)} buku)",
                 font=FONT_SMALL, bg=COLORS["bg"],
                 fg=COLORS["danger"]).pack(side="left")

        from views.widgets import build_treeview
        cols = ["Siswa", "NIS", "Kelas", "Buku", "Wajib Kembali", "Hari Terlambat"]
        widths = {"Siswa": 150, "NIS": 90, "Kelas": 70, "Buku": 200,
                  "Wajib Kembali": 120, "Hari Terlambat": 110}

        frame, tree = build_treeview(section, cols, widths, height=6)
        frame.pack(fill="x")

        for p in terlambat:
            tree.insert("", "end", values=(
                p["nama_siswa"], p["nis"], f"{p['jenjang']} {p['kelas']}",
                p["judul_buku"], p["tgl_kembali_rencana"], p["hari_terlambat"]
            ), tags=("danger",))
