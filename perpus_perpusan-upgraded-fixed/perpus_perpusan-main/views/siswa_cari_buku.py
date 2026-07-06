import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.database import BukuModel, PeminjamanModel
from datetime import datetime, timedelta

COLORS = {
    "bg":         "#F0F8F4",
    "sidebar":    "#1E6B45",
    "accent":     "#E8A020",
    "accent_d":   "#C4841A",
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
FONT_LABEL = ("Segoe UI", 10)
FONT_BTN   = ("Segoe UI", 10, "bold")


class SiswaCariPinjam:
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
        tk.Label(inner_hdr, text="📖  Cari & Pinjam Buku",
                 font=FONT_HEAD, bg=COLORS["card"],
                 fg=COLORS["sidebar"]).pack(anchor="w")
        tk.Label(inner_hdr,
                 text="Cari buku yang tersedia, lalu klik Pinjam",
                 font=FONT_SMALL, bg=COLORS["card"],
                 fg=COLORS["text_muted"]).pack(anchor="w")

        # Toolbar filter
        toolbar = tk.Frame(self.parent, bg=COLORS["bg"], pady=10)
        toolbar.pack(fill="x", padx=20)

        # Search box
        self.v_search = tk.StringVar()
        ent = tk.Entry(toolbar, textvariable=self.v_search,
                       font=FONT_BODY, relief="flat", bd=0,
                       highlightthickness=1,
                       highlightbackground=COLORS["border"],
                       highlightcolor=COLORS["siswa_clr"],
                       fg=COLORS["text"], width=28)
        ent.pack(side="left", ipady=6)
        ent.bind("<KeyRelease>", lambda e: self._load())
        placeholder = "Cari judul / pengarang..."
        ent.insert(0, placeholder)
        ent.configure(fg=COLORS["text_muted"])

        def on_focus_in(e):
            if ent.get() == placeholder:
                ent.delete(0, "end")
                ent.configure(fg=COLORS["text"])

        def on_focus_out(e):
            if not ent.get():
                ent.insert(0, placeholder)
                ent.configure(fg=COLORS["text_muted"])

        ent.bind("<FocusIn>", on_focus_in)
        ent.bind("<FocusOut>", on_focus_out)

        tk.Label(toolbar, text="  Jenjang:", font=FONT_LABEL,
                 bg=COLORS["bg"]).pack(side="left")
        self.v_jenjang = tk.StringVar(value="Semua")
        cb_j = ttk.Combobox(toolbar,
                             values=["Semua"] + BukuModel.JENJANG,
                             textvariable=self.v_jenjang,
                             state="readonly", width=8, font=FONT_BODY)
        cb_j.pack(side="left", padx=(4, 12))
        cb_j.bind("<<ComboboxSelected>>", lambda e: self._on_jenjang())

        tk.Label(toolbar, text="Kelas:", font=FONT_LABEL,
                 bg=COLORS["bg"]).pack(side="left")
        self.v_kelas = tk.StringVar(value="Semua")
        self.cb_kelas = ttk.Combobox(toolbar,
                                      values=["Semua"],
                                      textvariable=self.v_kelas,
                                      state="readonly", width=6, font=FONT_BODY)
        self.cb_kelas.pack(side="left", padx=(4, 12))
        self.cb_kelas.bind("<<ComboboxSelected>>", lambda e: self._load())

        tk.Label(toolbar, text="Mapel:", font=FONT_LABEL,
                 bg=COLORS["bg"]).pack(side="left")
        self.v_mapel = tk.StringVar(value="Semua")
        self.cb_mapel = ttk.Combobox(toolbar,
                                      values=["Semua"],
                                      textvariable=self.v_mapel,
                                      state="readonly", width=18, font=FONT_BODY)
        self.cb_mapel.pack(side="left", padx=(4, 0))
        self.cb_mapel.bind("<<ComboboxSelected>>", lambda e: self._load())

        # Tabel buku
        cols = ["ID", "Judul Buku", "Pengarang", "Jenjang", "Kelas",
                "Mata Pelajaran", "Tersedia", "Status"]
        widths = {"ID": 40, "Judul Buku": 230, "Pengarang": 160,
                  "Jenjang": 65, "Kelas": 55, "Mata Pelajaran": 150,
                  "Tersedia": 70, "Status": 100}

        from views.widgets import build_treeview
        frame, self.tree = build_treeview(self.parent, cols, widths, height=20)
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 4))
        self.tree.bind("<Double-1>", lambda e: self._pinjam())
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Bottom action bar
        action_bar = tk.Frame(self.parent, bg=COLORS["card"],
                               highlightbackground=COLORS["border"],
                               highlightthickness=1)
        action_bar.pack(fill="x")
        ab_inner = tk.Frame(action_bar, bg=COLORS["card"])
        ab_inner.pack(fill="x", padx=20, pady=10)

        self.lbl_selected = tk.Label(ab_inner,
                                      text="Pilih buku dari tabel di atas, lalu klik Pinjam",
                                      font=FONT_SMALL, bg=COLORS["card"],
                                      fg=COLORS["text_muted"])
        self.lbl_selected.pack(side="left")

        self.btn_pinjam = tk.Button(ab_inner, text="📖  Pinjam Buku Ini",
                                     command=self._pinjam,
                                     bg=COLORS["siswa_clr"], fg="#fff",
                                     activebackground="#247A4A",
                                     font=FONT_BTN, relief="flat",
                                     cursor="hand2", padx=16, pady=7,
                                     state="disabled")
        self.btn_pinjam.pack(side="right")

        self._load()

    def _on_jenjang(self):
        j = self.v_jenjang.get()
        if j == "Semua":
            self.cb_kelas.configure(values=["Semua"])
            self.cb_mapel.configure(values=["Semua"])
        else:
            kelas = ["Semua"] + BukuModel.KELAS_MAP.get(j, [])
            mapel = ["Semua"] + BukuModel.MAPEL_MAP.get(j, [])
            self.cb_kelas.configure(values=kelas)
            self.cb_mapel.configure(values=mapel)
        self.v_kelas.set("Semua")
        self.v_mapel.set("Semua")
        self._load()

    def _load(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        search = self.v_search.get()
        if search in ("", "Cari judul / pengarang..."):
            search = ""

        jenjang = self.v_jenjang.get()
        kelas = self.v_kelas.get()
        mapel = self.v_mapel.get()

        buku_list = BukuModel.get_all(
            search=search,
            jenjang="" if jenjang == "Semua" else jenjang,
            kelas="" if kelas == "Semua" else kelas,
            mapel="" if mapel == "Semua" else mapel,
        )

        # Cek buku yang sudah dipinjam siswa ini
        pinjaman_aktif = {
            p["buku_id"] for p in PeminjamanModel.get_by_siswa(self.siswa["id"])
            if p["status"] == "dipinjam"
        }

        for i, b in enumerate(buku_list):
            sudah_pinjam = b["id"] in pinjaman_aktif
            habis = b["stok_tersedia"] < 1

            if sudah_pinjam:
                status = "✓ Kamu pinjam"
                tag = "warning"
            elif habis:
                status = "Stok habis"
                tag = "danger"
            else:
                status = "✅ Tersedia"
                tag = "success" if i % 2 == 0 else "alt"

            self.tree.insert("", "end", iid=str(b["id"]), values=(
                b["id"], b["judul"], b["pengarang"],
                b["jenjang"], b["kelas"], b["mata_pelajaran"],
                b["stok_tersedia"], status
            ), tags=(tag,))

    def _on_select(self, e=None):
        sel = self.tree.selection()
        if not sel:
            self.lbl_selected.configure(text="Pilih buku dari tabel di atas, lalu klik Pinjam")
            self.btn_pinjam.configure(state="disabled")
            return

        bid = int(sel[0])
        item = self.tree.item(str(bid))
        vals = item["values"]
        judul = vals[1]
        status = str(vals[7])

        if "habis" in status.lower():
            self.lbl_selected.configure(
                text=f"❌  \"{judul}\" — stok habis, tidak bisa dipinjam.",
                fg=COLORS["danger"])
            self.btn_pinjam.configure(state="disabled")
        elif "kamu pinjam" in status.lower():
            self.lbl_selected.configure(
                text=f"ℹ  Kamu sudah meminjam \"{judul}\".",
                fg=COLORS["warning"])
            self.btn_pinjam.configure(state="disabled")
        else:
            tgl_kembali = (datetime.now() + timedelta(days=30)).strftime("%d %B %Y")
            self.lbl_selected.configure(
                text=f"✅  \"{judul}\"  |  Wajib kembali: {tgl_kembali}",
                fg=COLORS["success"])
            self.btn_pinjam.configure(state="normal")

    def _pinjam(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Pilih buku terlebih dahulu.")
            return

        bid = int(sel[0])
        buku = BukuModel.get_by_id(bid)
        if not buku:
            return

        tgl_kembali = (datetime.now() + timedelta(days=30)).strftime("%d %B %Y")

        konfirmasi = messagebox.askyesno(
            "Konfirmasi Peminjaman",
            f"Pinjam buku:\n\n"
            f"📖  {buku['judul']}\n"
            f"✍  {buku['pengarang']}\n"
            f"🏫  {buku['jenjang']} Kelas {buku['kelas']}\n\n"
            f"📅  Batas pengembalian: {tgl_kembali}\n\n"
            f"Lanjutkan?"
        )
        if not konfirmasi:
            return

        # Pinjam tanpa admin_id (siswa yang meminjam sendiri)
        ok, msg = PeminjamanModel.pinjam(
            self.siswa["id"], buku["id"], admin_id=None
        )
        if ok:
            messagebox.showinfo("Berhasil! 🎉",
                                f"Buku berhasil dipinjam!\n\n"
                                f"Jangan lupa kembalikan sebelum:\n{tgl_kembali}\n\n"
                                f"Ambil buku di meja perpustakaan.")
            self._load()
            self._on_select()
        else:
            messagebox.showerror("Gagal", msg)
