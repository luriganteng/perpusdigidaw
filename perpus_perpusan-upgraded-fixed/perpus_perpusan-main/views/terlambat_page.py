import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.database import PeminjamanModel, LaporanModel
from views.widgets import (COLORS, FONT_HEAD, FONT_BODY, FONT_SMALL, FONT_LABEL,
                            page_header, build_treeview, action_btn, card)
from datetime import datetime


class TerlambatPage:
    def __init__(self, parent):
        self.parent = parent
        self._build()

    def _build(self):
        page_header(self.parent, "⏰  Keterlambatan",
                    "Daftar peminjaman yang melewati batas waktu pengembalian")

        toolbar = tk.Frame(self.parent, bg=COLORS["bg"], pady=10)
        toolbar.pack(fill="x", padx=20)
        action_btn(toolbar, "🔄  Refresh", self._load_data,
                   kind="secondary").pack(side="left")
        action_btn(toolbar, "✅  Kembalikan Dipilih",
                   self._kembalikan, kind="success").pack(side="left", padx=(8, 0))

        # Warning banner
        self.banner = tk.Frame(self.parent, bg="#FFF3CD",
                               highlightbackground="#E8C84A",
                               highlightthickness=1)
        self.banner.pack(fill="x", padx=20, pady=(0, 8))
        self.lbl_banner = tk.Label(self.banner,
                                    text="", font=FONT_BODY,
                                    bg="#FFF3CD", fg="#856404",
                                    anchor="w", padx=14, pady=8)
        self.lbl_banner.pack(fill="x")

        cols = ["ID Pinjam", "Nama Siswa", "NIS", "Kelas",
                "Judul Buku", "Wajib Kembali", "Hari Terlambat"]
        widths = {"ID Pinjam": 70, "Nama Siswa": 180, "NIS": 100, "Kelas": 80,
                  "Judul Buku": 220, "Wajib Kembali": 120, "Hari Terlambat": 110}

        frame, self.tree = build_treeview(self.parent, cols, widths, height=24)
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        self._load_data()

    def _load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        data = PeminjamanModel.get_terlambat()
        self.lbl_banner.configure(
            text=f"⚠  Ditemukan {len(data)} peminjaman terlambat  "
                 f"(per {datetime.now().strftime('%d %B %Y')})"
        )
        for i, p in enumerate(data):
            days = p["hari_terlambat"]
            tag = "danger" if days > 7 else "warning"
            self.tree.insert("", "end", iid=str(p["id"]), values=(
                p["id"], p["nama_siswa"], p["nis"],
                f"{p.get('jenjang','')} {p.get('kelas','')}",
                p["judul_buku"], p["tgl_kembali_rencana"], days
            ), tags=(tag,))

    def _kembalikan(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Pilih data terlebih dahulu.")
            return
        pid = int(sel[0])
        item = self.tree.item(str(pid))
        nama = item["values"][1]
        judul = item["values"][4]
        if not messagebox.askyesno("Konfirmasi",
                f"Kembalikan buku:\n\"{judul}\"\ndari {nama}?"):
            return
        ok, msg = PeminjamanModel.kembalikan(pid)
        if ok:
            messagebox.showinfo("Berhasil", msg)
            self._load_data()
        else:
            messagebox.showerror("Gagal", msg)


class LaporanPage:
    def __init__(self, parent):
        self.parent = parent
        self._build()

    def _build(self):
        page_header(self.parent, "📊  Laporan & Statistik",
                    "Ringkasan data perpustakaan digital")

        # Scrollable
        canvas = tk.Canvas(self.parent, bg=COLORS["bg"], highlightthickness=0)
        vsb = ttk.Scrollbar(self.parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        body = tk.Frame(canvas, bg=COLORS["bg"])
        win_id = canvas.create_window((0, 0), window=body, anchor="nw")

        def on_cfg(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_resize(e):
            canvas.itemconfig(win_id, width=e.width)

        body.bind("<Configure>", on_cfg)
        canvas.bind("<Configure>", on_resize)
        canvas.bind_all("<MouseWheel>",
                         lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        self._build_overview(body)
        self._build_popular(body)
        self._build_monthly(body)
        self._build_jenjang(body)

    def _build_overview(self, parent):
        stats = LaporanModel.statistik_umum()
        sec = tk.Frame(parent, bg=COLORS["bg"])
        sec.pack(fill="x", padx=24, pady=(20, 8))
        tk.Label(sec, text="Statistik Umum", font=FONT_HEAD,
                 bg=COLORS["bg"], fg=COLORS["sidebar"]).pack(anchor="w", pady=(0, 10))

        grid = tk.Frame(sec, bg=COLORS["bg"])
        grid.pack(fill="x")
        items = [
            ("Total Judul",         stats["total_judul"],        COLORS["sidebar"],  "📚"),
            ("Total Eksemplar",     stats["total_buku"],         "#5B6FA6",          "🗂"),
            ("Total Siswa",         stats["total_siswa"],        COLORS["success"],  "👥"),
            ("Pinjam Aktif",        stats["total_pinjam_aktif"], COLORS["accent"],   "🔄"),
            ("Sudah Kembali",       stats["total_dikembalikan"], COLORS["text_muted"],"✅"),
            ("Terlambat",           stats["total_terlambat"],    COLORS["danger"],   "⚠"),
        ]
        from views.widgets import stat_card
        for i, (lbl, val, clr, icon) in enumerate(items):
            sc = stat_card(grid, lbl, val, clr, icon)
            sc.grid(row=0, column=i, padx=6, sticky="nsew")
            grid.columnconfigure(i, weight=1)

    def _build_popular(self, parent):
        data = LaporanModel.buku_terpopuler(10)
        sec = tk.Frame(parent, bg=COLORS["bg"])
        sec.pack(fill="x", padx=24, pady=(16, 8))
        tk.Label(sec, text="📖  Buku Paling Sering Dipinjam",
                 font=FONT_HEAD, bg=COLORS["bg"],
                 fg=COLORS["sidebar"]).pack(anchor="w", pady=(0, 10))

        cols = ["No", "Judul Buku", "Jenjang", "Kelas", "Mata Pelajaran", "Dipinjam"]
        widths = {"No": 40, "Judul Buku": 260, "Jenjang": 70,
                  "Kelas": 55, "Mata Pelajaran": 140, "Dipinjam": 80}

        frame, tree = build_treeview(sec, cols, widths, height=10)
        frame.pack(fill="x")

        for i, b in enumerate(data):
            tree.insert("", "end", values=(
                i + 1, b["judul"], b["jenjang"], b["kelas"],
                b["mata_pelajaran"], b["jumlah_dipinjam"]
            ), tags=("alt" if i % 2 else "",))

    def _build_monthly(self, parent):
        data = LaporanModel.peminjaman_per_bulan()
        if not data:
            return
        sec = tk.Frame(parent, bg=COLORS["bg"])
        sec.pack(fill="x", padx=24, pady=(16, 8))
        tk.Label(sec, text="📅  Peminjaman per Bulan (12 Bulan Terakhir)",
                 font=FONT_HEAD, bg=COLORS["bg"],
                 fg=COLORS["sidebar"]).pack(anchor="w", pady=(0, 10))

        chart_frame = tk.Frame(sec, bg=COLORS["card"],
                                highlightbackground=COLORS["border"],
                                highlightthickness=1)
        chart_frame.pack(fill="x")

        inner = tk.Frame(chart_frame, bg=COLORS["card"])
        inner.pack(padx=16, pady=16, fill="x")

        max_val = max(d["jumlah"] for d in data) if data else 1
        bar_w = max(30, min(60, 600 // len(data)))

        for d in reversed(data):
            col = tk.Frame(inner, bg=COLORS["card"])
            col.pack(side="left", padx=3)

            h = int((d["jumlah"] / max_val) * 120) if max_val else 0
            spacer = tk.Frame(col, bg=COLORS["card"], height=120 - h, width=bar_w)
            spacer.pack()
            bar = tk.Frame(col, bg=COLORS["accent"], height=max(4, h), width=bar_w)
            bar.pack()
            tk.Label(col, text=str(d["jumlah"]),
                     font=FONT_SMALL, bg=COLORS["card"],
                     fg=COLORS["text"]).pack()
            bulan = d["bulan"][-5:].replace("-", "/")
            tk.Label(col, text=bulan, font=("Segoe UI", 7),
                     bg=COLORS["card"], fg=COLORS["text_muted"]).pack()

    def _build_jenjang(self, parent):
        data = LaporanModel.distribusi_jenjang()
        if not data:
            return
        sec = tk.Frame(parent, bg=COLORS["bg"])
        sec.pack(fill="x", padx=24, pady=(16, 24))
        tk.Label(sec, text="🏫  Distribusi Peminjaman per Jenjang",
                 font=FONT_HEAD, bg=COLORS["bg"],
                 fg=COLORS["sidebar"]).pack(anchor="w", pady=(0, 10))

        row = tk.Frame(sec, bg=COLORS["bg"])
        row.pack(fill="x")

        colors = {"SD": "#3B82F6", "SMP": "#10B981", "SMA": "#F59E0B"}
        total = sum(d["jumlah"] for d in data) or 1

        for d in data:
            c = tk.Frame(row, bg=COLORS["card"],
                          highlightbackground=COLORS["border"],
                          highlightthickness=1)
            c.pack(side="left", expand=True, fill="both", padx=8)
            pct = round(d["jumlah"] / total * 100, 1)
            clr = colors.get(d["jenjang"], COLORS["sidebar"])
            tk.Frame(c, bg=clr, height=6).pack(fill="x")
            inner = tk.Frame(c, bg=COLORS["card"])
            inner.pack(padx=16, pady=14)
            tk.Label(inner, text=d["jenjang"], font=FONT_HEAD,
                     bg=COLORS["card"], fg=clr).pack()
            tk.Label(inner, text=str(d["jumlah"]),
                     font=("Segoe UI", 28, "bold"),
                     bg=COLORS["card"], fg=COLORS["text"]).pack()
            tk.Label(inner, text=f"{pct}% dari total",
                     font=FONT_SMALL, bg=COLORS["card"],
                     fg=COLORS["text_muted"]).pack()
