import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.database import PeminjamanModel, SiswaModel, BukuModel
from views.widgets import (COLORS, FONT_HEAD, FONT_BODY, FONT_SMALL, FONT_LABEL, FONT_BTN,
                            page_header, build_treeview, search_bar,
                            action_btn, modal, form_card)


class PeminjamanPage:
    def __init__(self, parent, admin):
        self.parent = parent
        self.admin = admin
        self._build()

    def _build(self):
        page_header(self.parent, "🔄  Peminjaman Buku",
                    "Catat peminjaman dan pengembalian buku")

        toolbar = tk.Frame(self.parent, bg=COLORS["bg"], pady=10)
        toolbar.pack(fill="x", padx=20)

        sbar, self.search_ent = search_bar(toolbar, self._load_data)
        sbar.pack(side="left", padx=(0, 12))

        tk.Label(toolbar, text="Status:", font=FONT_LABEL,
                 bg=COLORS["bg"]).pack(side="left")
        self.filter_status = ttk.Combobox(toolbar,
            values=["Semua", "Dipinjam", "Dikembalikan"],
            state="readonly", width=12, font=FONT_BODY)
        self.filter_status.set("Semua")
        self.filter_status.pack(side="left", padx=(4, 12))
        self.filter_status.bind("<<ComboboxSelected>>", lambda e: self._load_data())

        action_btn(toolbar, "➕  Catat Peminjaman",
                   self._open_pinjam, kind="primary").pack(side="right")
        action_btn(toolbar, "✅  Kembalikan",
                   self._kembalikan, kind="success").pack(side="right", padx=(0, 8))

        cols = ["ID", "Nama Siswa", "NIS", "Kelas", "Judul Buku",
                "Tgl Pinjam", "Wajib Kembali", "Tgl Dikembalikan", "Status"]
        widths = {"ID": 40, "Nama Siswa": 160, "NIS": 90, "Kelas": 70,
                  "Judul Buku": 200, "Tgl Pinjam": 100,
                  "Wajib Kembali": 110, "Tgl Dikembalikan": 120, "Status": 100}

        frame, self.tree = build_treeview(self.parent, cols, widths, height=22)
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        self._load_data()

    def _load_data(self, search=""):
        for row in self.tree.get_children():
            self.tree.delete(row)
        if not search and hasattr(self, "search_ent"):
            val = self.search_ent.get()
            search = "" if val in ("", "Cari...") else val

        status_filter = self.filter_status.get()
        status = "" if status_filter == "Semua" else status_filter.lower()

        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")

        for i, p in enumerate(PeminjamanModel.get_all(search, status)):
            tag = "alt" if i % 2 else ""
            if p["status"] == "dipinjam" and p["tgl_kembali_rencana"] < today:
                tag = "danger"
            elif p["status"] == "dikembalikan":
                tag = "success" if i % 2 == 0 else "alt"

            kelas_info = f"{p.get('jenjang','')} {p.get('kelas','')}"
            self.tree.insert("", "end", iid=str(p["id"]), values=(
                p["id"], p["nama_siswa"], p["nis"], kelas_info,
                p["judul_buku"], p["tgl_pinjam"],
                p["tgl_kembali_rencana"],
                p.get("tgl_kembali_aktual") or "-",
                p["status"].capitalize()
            ), tags=(tag,))

    def _get_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Pilih data peminjaman terlebih dahulu.")
            return None
        return int(sel[0])

    def _open_pinjam(self):
        PeminjamanForm(self.parent, self.admin, on_save=self._load_data)

    def _kembalikan(self):
        pid = self._get_selected()
        if not pid:
            return

        # Check status from tree
        item = self.tree.item(str(pid))
        vals = item["values"]
        status = str(vals[8]).lower()
        if status == "dikembalikan":
            messagebox.showinfo("Info", "Buku ini sudah dikembalikan.")
            return

        judul = vals[4]
        nama  = vals[1]
        if not messagebox.askyesno("Konfirmasi Pengembalian",
                f"Kembalikan buku:\n\"{judul}\"\ndari {nama}?"):
            return

        ok, msg = PeminjamanModel.kembalikan(pid)
        if ok:
            messagebox.showinfo("Berhasil", msg)
            self._load_data()
        else:
            messagebox.showerror("Gagal", msg)


class PeminjamanForm:
    def __init__(self, parent, admin, on_save=None):
        self.admin = admin
        self.on_save = on_save
        self.win = modal(parent, "Catat Peminjaman Buku",
                         width=560, height=440)
        self._siswa_list = []
        self._buku_list = []
        self._build()

    def _build(self):
        fc = form_card(self.win, "Formulir Peminjaman")
        fc.pack(fill="both", expand=True, padx=16, pady=16)
        body = tk.Frame(fc, bg=COLORS["card"])
        body.pack(padx=20, pady=14, fill="both")

        # Siswa search
        row1 = tk.Frame(body, bg=COLORS["card"])
        row1.pack(fill="x", pady=4)
        tk.Label(row1, text="Cari Siswa *", font=FONT_LABEL,
                 bg=COLORS["card"], fg=COLORS["text"],
                 width=16, anchor="w").pack(side="left")
        self.v_siswa_q = tk.StringVar()
        self.ent_siswa = tk.Entry(row1, textvariable=self.v_siswa_q,
                                   font=FONT_BODY, width=26,
                                   relief="flat", bd=0, highlightthickness=1,
                                   highlightbackground=COLORS["border"],
                                   highlightcolor=COLORS["accent"])
        self.ent_siswa.pack(side="left", ipady=5)
        self.ent_siswa.bind("<KeyRelease>", self._search_siswa)

        # Siswa dropdown
        row1b = tk.Frame(body, bg=COLORS["card"])
        row1b.pack(fill="x", pady=2)
        tk.Label(row1b, text="", width=16, bg=COLORS["card"]).pack(side="left")
        self.v_siswa = tk.StringVar()
        self.cb_siswa = ttk.Combobox(row1b, textvariable=self.v_siswa,
                                      state="readonly", width=36, font=FONT_BODY)
        self.cb_siswa.pack(side="left")

        # Buku search
        row2 = tk.Frame(body, bg=COLORS["card"])
        row2.pack(fill="x", pady=(12, 4))
        tk.Label(row2, text="Cari Buku *", font=FONT_LABEL,
                 bg=COLORS["card"], fg=COLORS["text"],
                 width=16, anchor="w").pack(side="left")
        self.v_buku_q = tk.StringVar()
        self.ent_buku = tk.Entry(row2, textvariable=self.v_buku_q,
                                  font=FONT_BODY, width=26,
                                  relief="flat", bd=0, highlightthickness=1,
                                  highlightbackground=COLORS["border"],
                                  highlightcolor=COLORS["accent"])
        self.ent_buku.pack(side="left", ipady=5)
        self.ent_buku.bind("<KeyRelease>", self._search_buku)

        # Buku dropdown
        row2b = tk.Frame(body, bg=COLORS["card"])
        row2b.pack(fill="x", pady=2)
        tk.Label(row2b, text="", width=16, bg=COLORS["card"]).pack(side="left")
        self.v_buku = tk.StringVar()
        self.cb_buku = ttk.Combobox(row2b, textvariable=self.v_buku,
                                     state="readonly", width=36, font=FONT_BODY)
        self.cb_buku.pack(side="left")

        # Info
        self.lbl_info = tk.Label(body, text="", font=FONT_SMALL,
                                  bg=COLORS["card"], fg=COLORS["text_muted"],
                                  anchor="w", wraplength=420)
        self.lbl_info.pack(fill="x", pady=(12, 0))

        btns = tk.Frame(fc, bg=COLORS["card"])
        btns.pack(fill="x", padx=20, pady=(8, 16))
        action_btn(btns, "Simpan Peminjaman", self._save,
                   kind="primary").pack(side="right")
        action_btn(btns, "Batal", self.win.destroy,
                   kind="secondary").pack(side="right", padx=(0, 8))

        from datetime import datetime, timedelta
        tgl = datetime.now().strftime("%d %B %Y")
        tgl_kembali = (datetime.now() + timedelta(days=30)).strftime("%d %B %Y")
        self.lbl_info.configure(
            text=f"📅  Tanggal pinjam: {tgl}   |   Wajib kembali: {tgl_kembali}")

    def _search_siswa(self, e=None):
        # Simpan id siswa yang sedang terpilih (jika ada) agar tidak
        # hilang/ketimpa begitu saja saat daftar hasil pencarian berubah.
        prev_idx = self.cb_siswa.current()
        prev_id = self._siswa_list[prev_idx]["id"] if 0 <= prev_idx < len(self._siswa_list) else None

        q = self.v_siswa_q.get().strip()
        self._siswa_list = SiswaModel.get_all(q)[:20]
        labels = [f"{s['nama']} ({s['nis']}) – {s['jenjang']} {s['kelas']}"
                  for s in self._siswa_list]
        self.cb_siswa.configure(values=labels)

        if not labels:
            self.cb_siswa.set("")
            return

        # Kalau siswa yang tadi dipilih masih ada di hasil baru, pertahankan.
        keep_idx = next((i for i, s in enumerate(self._siswa_list) if s["id"] == prev_id), None)
        self.cb_siswa.set(labels[keep_idx if keep_idx is not None else 0])

    def _search_buku(self, e=None):
        prev_idx = self.cb_buku.current()
        prev_id = self._buku_list[prev_idx]["id"] if 0 <= prev_idx < len(self._buku_list) else None

        q = self.v_buku_q.get().strip()
        self._buku_list = [b for b in BukuModel.get_all(q) if b["stok_tersedia"] > 0][:20]
        labels = [f"{b['judul']} ({b['jenjang']} Kls {b['kelas']}) – Sisa {b['stok_tersedia']}"
                  for b in self._buku_list]
        self.cb_buku.configure(values=labels)

        if not labels:
            self.cb_buku.set("")
            return

        keep_idx = next((i for i, b in enumerate(self._buku_list) if b["id"] == prev_id), None)
        self.cb_buku.set(labels[keep_idx if keep_idx is not None else 0])

    def _save(self):
        # Resolve siswa
        siswa_idx = self.cb_siswa.current()
        if siswa_idx < 0 or not self._siswa_list:
            messagebox.showwarning("Validasi", "Pilih siswa.", parent=self.win)
            return
        siswa = self._siswa_list[siswa_idx]

        # Resolve buku
        buku_idx = self.cb_buku.current()
        if buku_idx < 0 or not self._buku_list:
            messagebox.showwarning("Validasi", "Pilih buku yang tersedia.", parent=self.win)
            return
        buku = self._buku_list[buku_idx]

        ok, msg = PeminjamanModel.pinjam(siswa["id"], buku["id"], self.admin["id"])
        if ok:
            messagebox.showinfo("Berhasil", msg, parent=self.win)
            if self.on_save:
                self.on_save()
            self.win.destroy()
        else:
            messagebox.showerror("Gagal", msg, parent=self.win)
