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
}
FONT_HEAD  = ("Segoe UI", 13, "bold")
FONT_BODY  = ("Segoe UI", 11)
FONT_SMALL = ("Segoe UI", 9)
FONT_BTN   = ("Segoe UI", 10, "bold")


class SiswaBeranda:
    def __init__(self, parent, siswa, navigate):
        self.parent = parent
        self.siswa = siswa
        self.navigate = navigate
        self._build()

    def _build(self):
        # Header
        hdr = tk.Frame(self.parent, bg=COLORS["card"],
                       highlightbackground=COLORS["border"],
                       highlightthickness=1)
        hdr.pack(fill="x")
        inner_hdr = tk.Frame(hdr, bg=COLORS["card"])
        inner_hdr.pack(fill="x", padx=24, pady=14)
        tgl = datetime.now().strftime("%d %B %Y")
        tk.Label(inner_hdr,
                 text=f"Halo, {self.siswa['nama']}! 👋",
                 font=FONT_HEAD, bg=COLORS["card"],
                 fg=COLORS["sidebar"]).pack(anchor="w")

        jenjang = self.siswa.get('jenjang') or '-'
        kelas = self.siswa.get('kelas') or '-'
        subtitle = f"{tgl}" if jenjang == '-' else f"{jenjang} {kelas}  •  {tgl}"
        tk.Label(inner_hdr,
                 text=subtitle,
                 font=FONT_SMALL, bg=COLORS["card"],
                 fg=COLORS["text_muted"]).pack(anchor="w")

        # Scrollable body
        canvas = tk.Canvas(self.parent, bg=COLORS["bg"], highlightthickness=0)
        vsb = ttk.Scrollbar(self.parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        body = tk.Frame(canvas, bg=COLORS["bg"])
        win_id = canvas.create_window((0, 0), window=body, anchor="nw")

        body.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))
        canvas.bind_all("<MouseWheel>",
                         lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        self._build_stat_cards(body)
        self._build_quick_actions(body)
        self._build_pinjaman_aktif(body)
        self._build_terlambat_warning(body)

    def _build_stat_cards(self, parent):
        riwayat = PeminjamanModel.get_by_siswa(self.siswa["id"])
        aktif = [p for p in riwayat if p["status"] == "dipinjam"]
        kembali = [p for p in riwayat if p["status"] == "dikembalikan"]

        hari_ini = datetime.now().strftime("%Y-%m-%d")
        terlambat = [p for p in aktif if p["tgl_kembali_rencana"] < hari_ini]

        sec = tk.Frame(parent, bg=COLORS["bg"])
        sec.pack(fill="x", padx=24, pady=(20, 8))
        tk.Label(sec, text="Ringkasan Pinjamanmu",
                 font=FONT_HEAD, bg=COLORS["bg"],
                 fg=COLORS["sidebar"]).pack(anchor="w", pady=(0, 10))

        grid = tk.Frame(sec, bg=COLORS["bg"])
        grid.pack(fill="x")

        items = [
            ("Sedang Dipinjam", len(aktif),    COLORS["siswa_clr"], "🔄"),
            ("Sudah Dikembalikan", len(kembali), COLORS["text_muted"], "✅"),
            ("Terlambat",       len(terlambat), COLORS["danger"],    "⚠"),
        ]
        for i, (lbl, val, clr, icon) in enumerate(items):
            c = tk.Frame(grid, bg=COLORS["card"],
                         highlightbackground=COLORS["border"],
                         highlightthickness=1)
            c.grid(row=0, column=i, padx=6, sticky="nsew")
            grid.columnconfigure(i, weight=1)

            inner = tk.Frame(c, bg=COLORS["card"])
            inner.pack(padx=18, pady=14)
            top = tk.Frame(inner, bg=COLORS["card"])
            top.pack(fill="x")
            tk.Label(top, text=icon, font=("Segoe UI", 20),
                     bg=COLORS["card"]).pack(side="left")
            tk.Label(top, text=str(val),
                     font=("Segoe UI", 26, "bold"),
                     bg=COLORS["card"], fg=clr).pack(side="right")
            tk.Label(inner, text=lbl, font=FONT_SMALL,
                     bg=COLORS["card"], fg=COLORS["text_muted"],
                     anchor="w").pack(fill="x", pady=(4, 0))
            tk.Frame(inner, bg=clr, height=3).pack(fill="x", pady=(8, 0))

    def _build_quick_actions(self, parent):
        sec = tk.Frame(parent, bg=COLORS["bg"])
        sec.pack(fill="x", padx=24, pady=(12, 4))
        tk.Label(sec, text="Aksi Cepat", font=FONT_HEAD,
                 bg=COLORS["bg"], fg=COLORS["sidebar"]).pack(anchor="w", pady=(0, 10))

        row = tk.Frame(sec, bg=COLORS["bg"])
        row.pack(fill="x")

        actions = [
            ("📖  Cari & Pinjam Buku", "cari_buku",      COLORS["siswa_clr"]),
            ("🔄  Pinjaman Aktif",      "pinjaman_aktif", COLORS["sidebar"]),
            ("📋  Riwayat Pinjaman",    "riwayat",        COLORS["text_muted"]),
        ]
        for label, page, bg in actions:
            btn = tk.Button(row, text=label,
                            command=lambda p=page: self.navigate(p),
                            bg=bg, fg="#fff" if bg != COLORS["text_muted"] else COLORS["text"],
                            activebackground=bg,
                            font=FONT_BTN, relief="flat", cursor="hand2",
                            padx=14, pady=8)
            btn.pack(side="left", padx=(0, 8))

    def _build_pinjaman_aktif(self, parent):
        from views.widgets import build_treeview
        riwayat = PeminjamanModel.get_by_siswa(self.siswa["id"])
        aktif = [p for p in riwayat if p["status"] == "dipinjam"]

        sec = tk.Frame(parent, bg=COLORS["bg"])
        sec.pack(fill="x", padx=24, pady=(16, 4))
        tk.Label(sec, text="📚  Buku yang Sedang Kamu Pinjam",
                 font=FONT_HEAD, bg=COLORS["bg"],
                 fg=COLORS["sidebar"]).pack(anchor="w", pady=(0, 10))

        if not aktif:
            tk.Label(sec, text="Kamu belum meminjam buku apapun saat ini.",
                     font=FONT_BODY, bg=COLORS["bg"],
                     fg=COLORS["text_muted"]).pack(anchor="w")
            return

        cols = ["Judul Buku", "Mata Pelajaran", "Tgl Pinjam",
                "Wajib Kembali", "Sisa Hari"]
        widths = {"Judul Buku": 250, "Mata Pelajaran": 150,
                  "Tgl Pinjam": 110, "Wajib Kembali": 120, "Sisa Hari": 90}

        frame, tree = build_treeview(sec, cols, widths, height=len(aktif) + 1)
        frame.pack(fill="x")

        hari_ini = datetime.now()
        for p in aktif:
            tgl_kembali = datetime.strptime(p["tgl_kembali_rencana"], "%Y-%m-%d")
            sisa = (tgl_kembali - hari_ini).days
            if sisa < 0:
                sisa_str = f"Terlambat {abs(sisa)} hari"
                tag = "danger"
            elif sisa <= 3:
                sisa_str = f"{sisa} hari lagi"
                tag = "warning"
            else:
                sisa_str = f"{sisa} hari lagi"
                tag = "success"

            tree.insert("", "end", values=(
                p["judul"], p["mata_pelajaran"],
                p["tgl_pinjam"], p["tgl_kembali_rencana"], sisa_str
            ), tags=(tag,))

    def _build_terlambat_warning(self, parent):
        from datetime import datetime
        riwayat = PeminjamanModel.get_by_siswa(self.siswa["id"])
        hari_ini = datetime.now().strftime("%Y-%m-%d")
        terlambat = [p for p in riwayat
                     if p["status"] == "dipinjam"
                     and p["tgl_kembali_rencana"] < hari_ini]

        if not terlambat:
            return

        sec = tk.Frame(parent, bg="#FDECEA",
                       highlightbackground=COLORS["danger"],
                       highlightthickness=1)
        sec.pack(fill="x", padx=24, pady=(12, 20))

        inner = tk.Frame(sec, bg="#FDECEA")
        inner.pack(padx=16, pady=12, fill="x")

        tk.Label(inner,
                 text=f"⚠  Kamu memiliki {len(terlambat)} buku yang terlambat dikembalikan!",
                 font=("Segoe UI", 11, "bold"),
                 bg="#FDECEA", fg=COLORS["danger"]).pack(anchor="w")
        for p in terlambat:
            hari = (datetime.now() - datetime.strptime(p["tgl_kembali_rencana"], "%Y-%m-%d")).days
            tk.Label(inner,
                     text=f"  • {p['judul']}  (terlambat {hari} hari)",
                     font=FONT_SMALL, bg="#FDECEA",
                     fg=COLORS["danger"]).pack(anchor="w")
        tk.Label(inner,
                 text="Segera kembalikan buku ke perpustakaan.",
                 font=FONT_SMALL, bg="#FDECEA",
                 fg=COLORS["text_muted"]).pack(anchor="w", pady=(6, 0))
