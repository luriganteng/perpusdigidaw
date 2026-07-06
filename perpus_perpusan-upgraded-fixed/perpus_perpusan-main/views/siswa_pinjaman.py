import tkinter as tk
from tkinter import ttk
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.database import PeminjamanModel
from datetime import datetime

COLORS = {
    "bg":         "#F0F8F4",
    "sidebar":    "#1E6B45",
    "accent":     "#E8A020",
    "card":       "#FFFFFF",
    "text":       "#1C2B3A",
    "text_muted": "#6B7E8F",
    "danger":     "#D94040",
    "success":    "#2E9E5E",
    "warning":    "#E07B1A",
    "border":     "#C8E0D4",
    "siswa_clr":  "#2E9E5E",
    "row_alt":    "#F7FAFC",
}
FONT_HEAD  = ("Segoe UI", 13, "bold")
FONT_BODY  = ("Segoe UI", 11)
FONT_SMALL = ("Segoe UI", 9)
FONT_BTN   = ("Segoe UI", 10, "bold")


class SiswaPinjamanAktif:
    def __init__(self, parent, siswa):
        self.parent = parent
        self.siswa = siswa
        self._build()

    def _build(self):
        # Header
        hdr = tk.Frame(self.parent, bg=COLORS["card"],
                       highlightbackground=COLORS["border"],
                       highlightthickness=1)
        hdr.pack(fill="x")
        inner_hdr = tk.Frame(hdr, bg=COLORS["card"])
        inner_hdr.pack(fill="x", padx=24, pady=14)
        tk.Label(inner_hdr, text="🔄  Pinjaman Aktif",
                 font=FONT_HEAD, bg=COLORS["card"],
                 fg=COLORS["sidebar"]).pack(anchor="w")
        tk.Label(inner_hdr,
                 text="Buku yang sedang kamu pinjam saat ini",
                 font=FONT_SMALL, bg=COLORS["card"],
                 fg=COLORS["text_muted"]).pack(anchor="w")

        # Toolbar
        toolbar = tk.Frame(self.parent, bg=COLORS["bg"], pady=10)
        toolbar.pack(fill="x", padx=20)
        tk.Button(toolbar, text="🔄  Refresh", command=self._load,
                  bg=COLORS["border"], fg=COLORS["text"],
                  activebackground="#B8C8D8",
                  font=FONT_BTN, relief="flat", cursor="hand2",
                  padx=12, pady=5).pack(side="left")

        # Tabel
        cols = ["Judul Buku", "Mata Pelajaran", "Jenjang",
                "Tgl Pinjam", "Wajib Kembali", "Sisa Hari", "Status"]
        widths = {"Judul Buku": 250, "Mata Pelajaran": 150, "Jenjang": 80,
                  "Tgl Pinjam": 110, "Wajib Kembali": 120,
                  "Sisa Hari": 90, "Status": 110}

        from views.widgets import build_treeview
        frame, self.tree = build_treeview(self.parent, cols, widths, height=22)
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self._load()

    def _load(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        riwayat = PeminjamanModel.get_by_siswa(self.siswa["id"])
        aktif = [p for p in riwayat if p["status"] == "dipinjam"]

        if not aktif:
            self.tree.insert("", "end", values=(
                "Tidak ada pinjaman aktif", "", "", "", "", "", ""
            ))
            return

        hari_ini = datetime.now()
        for p in aktif:
            tgl_kembali = datetime.strptime(p["tgl_kembali_rencana"], "%Y-%m-%d")
            sisa = (tgl_kembali - hari_ini).days

            if sisa < 0:
                sisa_str = f"Terlambat {abs(sisa)} hr"
                status_str = "⚠ Terlambat"
                tag = "danger"
            elif sisa <= 3:
                sisa_str = f"{sisa} hari lagi"
                status_str = "⏰ Segera!"
                tag = "warning"
            else:
                sisa_str = f"{sisa} hari lagi"
                status_str = "✅ Tepat waktu"
                tag = "success"

            self.tree.insert("", "end", values=(
                p["judul"], p["mata_pelajaran"],
                p.get("jenjang", ""),
                p["tgl_pinjam"], p["tgl_kembali_rencana"],
                sisa_str, status_str
            ), tags=(tag,))

        # Info box
        terlambat_count = sum(
            1 for p in aktif
            if p["tgl_kembali_rencana"] < hari_ini.strftime("%Y-%m-%d")
        )
        if terlambat_count > 0:
            banner = tk.Frame(self.parent, bg="#FFF3CD",
                               highlightbackground="#E8C84A",
                               highlightthickness=1)
            banner.pack(fill="x", padx=20, pady=(0, 10))
            tk.Label(banner,
                     text=f"⚠  {terlambat_count} buku terlambat dikembalikan. "
                          f"Segera kembalikan ke perpustakaan!",
                     font=FONT_BODY, bg="#FFF3CD",
                     fg="#856404", anchor="w",
                     padx=14, pady=8).pack(fill="x")


class SiswaRiwayat:
    def __init__(self, parent, siswa):
        self.parent = parent
        self.siswa = siswa
        self._build()

    def _build(self):
        # Header
        hdr = tk.Frame(self.parent, bg=COLORS["card"],
                       highlightbackground=COLORS["border"],
                       highlightthickness=1)
        hdr.pack(fill="x")
        inner_hdr = tk.Frame(hdr, bg=COLORS["card"])
        inner_hdr.pack(fill="x", padx=24, pady=14)
        tk.Label(inner_hdr, text="📋  Riwayat Pinjaman",
                 font=FONT_HEAD, bg=COLORS["card"],
                 fg=COLORS["sidebar"]).pack(anchor="w")
        tk.Label(inner_hdr,
                 text="Semua riwayat peminjaman buku kamu",
                 font=FONT_SMALL, bg=COLORS["card"],
                 fg=COLORS["text_muted"]).pack(anchor="w")

        cols = ["Judul Buku", "Mata Pelajaran",
                "Tgl Pinjam", "Wajib Kembali",
                "Tgl Dikembalikan", "Status"]
        widths = {"Judul Buku": 260, "Mata Pelajaran": 150,
                  "Tgl Pinjam": 110, "Wajib Kembali": 120,
                  "Tgl Dikembalikan": 130, "Status": 110}

        from views.widgets import build_treeview
        frame, self.tree = build_treeview(self.parent, cols, widths, height=24)
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        riwayat = PeminjamanModel.get_by_siswa(self.siswa["id"])

        if not riwayat:
            self.tree.insert("", "end", values=(
                "Belum ada riwayat pinjaman", "", "", "", "", ""
            ))
            return

        hari_ini = datetime.now().strftime("%Y-%m-%d")
        for i, p in enumerate(riwayat):
            if p["status"] == "dikembalikan":
                tag = "success" if i % 2 == 0 else "alt"
                status_str = "✅ Dikembalikan"
            elif p["tgl_kembali_rencana"] < hari_ini:
                tag = "danger"
                status_str = "⚠ Terlambat"
            else:
                tag = "warning"
                status_str = "🔄 Dipinjam"

            self.tree.insert("", "end", values=(
                p["judul"], p["mata_pelajaran"],
                p["tgl_pinjam"], p["tgl_kembali_rencana"],
                p.get("tgl_kembali_aktual") or "-",
                status_str
            ), tags=(tag,))
