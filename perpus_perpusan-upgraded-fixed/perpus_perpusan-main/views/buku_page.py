import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.database import BukuModel
from views.widgets import (COLORS, FONT_HEAD, FONT_BODY, FONT_SMALL, FONT_LABEL, FONT_BTN,
                            page_header, build_treeview, search_bar,
                            action_btn, labeled_entry, labeled_combo, modal, form_card)


class BukuPage:
    def __init__(self, parent, admin):
        self.parent = parent
        self.admin = admin
        self.selected_id = None
        self._build()

    def _build(self):
        page_header(self.parent, "📖  Manajemen Buku",
                    "Kelola koleksi buku pelajaran SD – SMA")

        # Toolbar
        toolbar = tk.Frame(self.parent, bg=COLORS["bg"], pady=10)
        toolbar.pack(fill="x", padx=20)

        sbar, self.search_ent = search_bar(toolbar, self._load_data)
        sbar.pack(side="left", padx=(0, 12))

        # Filter jenjang
        tk.Label(toolbar, text="Jenjang:", font=FONT_LABEL,
                 bg=COLORS["bg"]).pack(side="left")
        self.filter_jenjang = ttk.Combobox(toolbar,
            values=["Semua"] + BukuModel.JENJANG, state="readonly",
            width=8, font=FONT_BODY)
        self.filter_jenjang.set("Semua")
        self.filter_jenjang.pack(side="left", padx=(4, 12))
        self.filter_jenjang.bind("<<ComboboxSelected>>", lambda e: self._load_data())

        # Filter kelas
        tk.Label(toolbar, text="Kelas:", font=FONT_LABEL,
                 bg=COLORS["bg"]).pack(side="left")
        self.filter_kelas = ttk.Combobox(toolbar,
            values=["Semua"] + [str(i) for i in range(1, 13)],
            state="readonly", width=6, font=FONT_BODY)
        self.filter_kelas.set("Semua")
        self.filter_kelas.pack(side="left", padx=(4, 12))
        self.filter_kelas.bind("<<ComboboxSelected>>", lambda e: self._load_data())

        action_btn(toolbar, "➕  Tambah Buku",
                   self._open_add, kind="primary").pack(side="right")
        action_btn(toolbar, "✏  Edit",
                   self._open_edit, kind="secondary").pack(side="right", padx=(0, 8))
        action_btn(toolbar, "🗑  Hapus",
                   self._delete, kind="danger").pack(side="right", padx=(0, 8))

        # Treeview
        cols = ["ID", "ISBN", "Judul", "Pengarang", "Jenjang", "Kelas",
                "Mata Pelajaran", "Stok", "Tersedia"]
        widths = {"ID": 40, "ISBN": 110, "Judul": 220, "Pengarang": 150,
                  "Jenjang": 60, "Kelas": 55, "Mata Pelajaran": 140,
                  "Stok": 55, "Tersedia": 70}
        tree_frame, self.tree = build_treeview(
            self.parent, cols, widths, height=22)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self.tree.bind("<Double-1>", lambda e: self._open_edit())
        self._load_data()

    def _load_data(self, search=""):
        for row in self.tree.get_children():
            self.tree.delete(row)

        if not search and hasattr(self, 'search_ent'):
            val = self.search_ent.get()
            search = "" if val in ("", "Cari...") else val

        jenjang = self.filter_jenjang.get()
        kelas = self.filter_kelas.get()
        buku_list = BukuModel.get_all(
            search=search,
            jenjang="" if jenjang == "Semua" else jenjang,
            kelas="" if kelas == "Semua" else kelas,
        )

        for i, b in enumerate(buku_list):
            tag = "alt" if i % 2 else ""
            if b["stok_tersedia"] == 0:
                tag = "warning"
            self.tree.insert("", "end", iid=str(b["id"]), values=(
                b["id"], b["isbn"] or "-", b["judul"], b["pengarang"],
                b["jenjang"], b["kelas"], b["mata_pelajaran"],
                b["stok"], b["stok_tersedia"]
            ), tags=(tag,))

    def _get_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Pilih buku terlebih dahulu.")
            return None
        return int(sel[0])

    def _open_add(self):
        BukuForm(self.parent, on_save=self._load_data)

    def _open_edit(self):
        bid = self._get_selected()
        if not bid:
            return
        buku = BukuModel.get_by_id(bid)
        BukuForm(self.parent, buku=buku, on_save=self._load_data)

    def _delete(self):
        bid = self._get_selected()
        if not bid:
            return
        buku = BukuModel.get_by_id(bid)
        if not messagebox.askyesno("Konfirmasi",
                f"Hapus buku:\n\"{buku['judul']}\"?\n\nTindakan ini tidak bisa dibatalkan."):
            return
        ok, msg = BukuModel.delete(bid)
        if ok:
            messagebox.showinfo("Berhasil", msg)
            self._load_data()
        else:
            messagebox.showerror("Gagal", msg)


class BukuForm:
    def __init__(self, parent, buku=None, on_save=None):
        self.buku = buku
        self.on_save = on_save
        self.win = modal(parent, "Edit Buku" if buku else "Tambah Buku",
                         width=520, height=580)
        self._build()

    def _build(self):
        win = self.win
        fc = form_card(win, "Data Buku")
        fc.pack(fill="both", expand=True, padx=16, pady=16)

        body = tk.Frame(fc, bg=COLORS["card"])
        body.pack(padx=20, pady=10, fill="both")

        self.vars = {
            "isbn":     tk.StringVar(),
            "judul":    tk.StringVar(),
            "pengarang":tk.StringVar(),
            "penerbit": tk.StringVar(),
            "tahun":    tk.StringVar(),
            "stok":     tk.StringVar(value="1"),
        }
        self.jenjang_var = tk.StringVar()
        self.kelas_var   = tk.StringVar()
        self.mapel_var   = tk.StringVar()

        fields = [
            ("ISBN",        "isbn"),
            ("Judul *",     "judul"),
            ("Pengarang *", "pengarang"),
            ("Penerbit",    "penerbit"),
            ("Tahun Terbit","tahun"),
            ("Stok *",      "stok"),
        ]

        for label, key in fields:
            row = tk.Frame(body, bg=COLORS["card"])
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, font=FONT_LABEL,
                     bg=COLORS["card"], fg=COLORS["text"],
                     width=16, anchor="w").pack(side="left")
            ent = tk.Entry(row, textvariable=self.vars[key],
                           font=FONT_BODY, relief="flat", bd=0,
                           highlightthickness=1,
                           highlightbackground=COLORS["border"],
                           highlightcolor=COLORS["accent"],
                           width=28)
            ent.pack(side="left", ipady=5)

        # Jenjang
        row_j = tk.Frame(body, bg=COLORS["card"])
        row_j.pack(fill="x", pady=3)
        tk.Label(row_j, text="Jenjang *", font=FONT_LABEL,
                 bg=COLORS["card"], fg=COLORS["text"],
                 width=16, anchor="w").pack(side="left")
        self.cb_jenjang = ttk.Combobox(row_j, values=BukuModel.JENJANG,
                                        textvariable=self.jenjang_var,
                                        state="readonly", width=10, font=FONT_BODY)
        self.cb_jenjang.pack(side="left")
        self.cb_jenjang.bind("<<ComboboxSelected>>", self._on_jenjang)

        # Kelas
        row_k = tk.Frame(body, bg=COLORS["card"])
        row_k.pack(fill="x", pady=3)
        tk.Label(row_k, text="Kelas *", font=FONT_LABEL,
                 bg=COLORS["card"], fg=COLORS["text"],
                 width=16, anchor="w").pack(side="left")
        self.cb_kelas = ttk.Combobox(row_k, textvariable=self.kelas_var,
                                      state="readonly", width=10, font=FONT_BODY)
        self.cb_kelas.pack(side="left")

        # Mapel
        row_m = tk.Frame(body, bg=COLORS["card"])
        row_m.pack(fill="x", pady=3)
        tk.Label(row_m, text="Mata Pelajaran *", font=FONT_LABEL,
                 bg=COLORS["card"], fg=COLORS["text"],
                 width=16, anchor="w").pack(side="left")
        self.cb_mapel = ttk.Combobox(row_m, textvariable=self.mapel_var,
                                      state="readonly", width=24, font=FONT_BODY)
        self.cb_mapel.pack(side="left")

        if self.buku:
            self._populate()

        # Buttons
        btns = tk.Frame(fc, bg=COLORS["card"])
        btns.pack(fill="x", padx=20, pady=(10, 16))
        action_btn(btns, "Simpan", self._save, kind="primary").pack(side="right")
        action_btn(btns, "Batal", self.win.destroy,
                   kind="secondary").pack(side="right", padx=(0, 8))

    def _on_jenjang(self, e=None):
        j = self.jenjang_var.get()
        kelas_list = BukuModel.KELAS_MAP.get(j, [])
        mapel_list = BukuModel.MAPEL_MAP.get(j, [])
        self.cb_kelas.configure(values=kelas_list)
        self.cb_mapel.configure(values=mapel_list)
        self.kelas_var.set("")
        self.mapel_var.set("")

    def _populate(self):
        b = self.buku
        self.vars["isbn"].set(b.get("isbn") or "")
        self.vars["judul"].set(b["judul"])
        self.vars["pengarang"].set(b["pengarang"])
        self.vars["penerbit"].set(b.get("penerbit") or "")
        self.vars["tahun"].set(b.get("tahun_terbit") or "")
        self.vars["stok"].set(b["stok"])
        self.jenjang_var.set(b["jenjang"])
        self._on_jenjang()
        self.kelas_var.set(b["kelas"])
        self.mapel_var.set(b["mata_pelajaran"])

    def _save(self):
        isbn    = self.vars["isbn"].get().strip()
        judul   = self.vars["judul"].get().strip()
        pengarang = self.vars["pengarang"].get().strip()
        penerbit  = self.vars["penerbit"].get().strip()
        tahun   = self.vars["tahun"].get().strip()
        stok    = self.vars["stok"].get().strip()
        jenjang = self.jenjang_var.get()
        kelas   = self.kelas_var.get()
        mapel   = self.mapel_var.get()

        if not all([judul, pengarang, jenjang, kelas, mapel, stok]):
            messagebox.showwarning("Validasi", "Isi semua kolom wajib (*)", parent=self.win)
            return
        try:
            stok = int(stok)
            if stok < 1:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validasi", "Stok harus berupa angka positif.", parent=self.win)
            return

        tahun_int = int(tahun) if tahun.isdigit() else None

        if self.buku:
            ok, msg = BukuModel.update(
                self.buku["id"], isbn, judul, pengarang, penerbit,
                tahun_int, jenjang, kelas, mapel, stok)
        else:
            ok, msg = BukuModel.add(
                isbn, judul, pengarang, penerbit,
                tahun_int, jenjang, kelas, mapel, stok)

        if ok:
            messagebox.showinfo("Berhasil", msg, parent=self.win)
            if self.on_save:
                self.on_save()
            self.win.destroy()
        else:
            messagebox.showerror("Gagal", msg, parent=self.win)
