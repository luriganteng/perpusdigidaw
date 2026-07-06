import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.database import SiswaModel
from views.widgets import (COLORS, FONT_HEAD, FONT_BODY, FONT_SMALL, FONT_LABEL, FONT_BTN,
                            page_header, build_treeview, search_bar,
                            action_btn, modal, form_card)


class SiswaPage:
    def __init__(self, parent, admin):
        self.parent = parent
        self.admin = admin
        self._build()

    def _build(self):
        page_header(self.parent, "👥  Data Siswa",
                    "Kelola data siswa yang terdaftar di perpustakaan")

        toolbar = tk.Frame(self.parent, bg=COLORS["bg"], pady=10)
        toolbar.pack(fill="x", padx=20)

        sbar, self.search_ent = search_bar(toolbar, self._load_data)
        sbar.pack(side="left", padx=(0, 12))

        action_btn(toolbar, "➕  Tambah Siswa",
                   self._open_add, kind="primary").pack(side="right")
        action_btn(toolbar, "✏  Edit",
                   self._open_edit, kind="secondary").pack(side="right", padx=(0, 8))
        action_btn(toolbar, "🗑  Hapus",
                   self._delete, kind="danger").pack(side="right", padx=(0, 8))
        action_btn(toolbar, "📋  Riwayat Pinjam",
                   self._open_history, kind="warning").pack(side="right", padx=(0, 8))

        cols = ["ID", "NIS", "Nama", "Jenjang", "Kelas", "Telepon",
                "Pinjam Aktif", "Sumber", "Terdaftar"]
        widths = {"ID": 40, "NIS": 100, "Nama": 200, "Jenjang": 70,
                  "Kelas": 60, "Telepon": 110, "Pinjam Aktif": 90,
                  "Sumber": 100, "Terdaftar": 110}

        frame, self.tree = build_treeview(self.parent, cols, widths, height=24)
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        self.tree.bind("<Double-1>", lambda e: self._open_edit())
        self._load_data()

    def _load_data(self, search=""):
        for row in self.tree.get_children():
            self.tree.delete(row)
        if not search and hasattr(self, "search_ent"):
            val = self.search_ent.get()
            search = "" if val in ("", "Cari...") else val

        for i, s in enumerate(SiswaModel.get_all(search)):
            tag = "alt" if i % 2 else ""
            if s.get("pinjam_aktif", 0) > 0:
                tag = "success"

            is_auto = s.get("auto_registered") == 1
            sumber = "🎒 Login sendiri" if is_auto else "🏫 Admin"
            if is_auto:
                tag = "warning"

            self.tree.insert("", "end", iid=str(s["id"]), values=(
                s["id"], s.get("nis") or "-", s["nama"],
                s.get("jenjang") or "-", s.get("kelas") or "-",
                s.get("telepon") or "-",
                s.get("pinjam_aktif", 0),
                sumber,
                s["created_at"][:10]
            ), tags=(tag,))

    def _get_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Pilih siswa terlebih dahulu.")
            return None
        return int(sel[0])

    def _open_add(self):
        SiswaForm(self.parent, on_save=self._load_data)

    def _open_edit(self):
        sid = self._get_selected()
        if not sid:
            return
        siswa = SiswaModel.get_by_id(sid)
        SiswaForm(self.parent, siswa=siswa, on_save=self._load_data)

    def _delete(self):
        sid = self._get_selected()
        if not sid:
            return
        siswa = SiswaModel.get_by_id(sid)
        if not messagebox.askyesno("Konfirmasi",
                f"Hapus siswa:\n\"{siswa['nama']}\" ({siswa['nis']})?"):
            return
        ok, msg = SiswaModel.delete(sid)
        if ok:
            messagebox.showinfo("Berhasil", msg)
            self._load_data()
        else:
            messagebox.showerror("Gagal", msg)

    def _open_history(self):
        sid = self._get_selected()
        if not sid:
            return
        siswa = SiswaModel.get_by_id(sid)
        RiwayatSiswa(self.parent, siswa)


class SiswaForm:
    def __init__(self, parent, siswa=None, on_save=None):
        self.siswa = siswa
        self.on_save = on_save
        self.win = modal(parent, "Edit Siswa" if siswa else "Tambah Siswa",
                         width=480, height=460)
        self._build()

    def _build(self):
        fc = form_card(self.win, "Data Siswa")
        fc.pack(fill="both", expand=True, padx=16, pady=16)

        body = tk.Frame(fc, bg=COLORS["card"])
        body.pack(padx=20, pady=10, fill="both")

        self.v_nis      = tk.StringVar()
        self.v_nama     = tk.StringVar()
        self.v_telepon  = tk.StringVar()
        self.v_jenjang  = tk.StringVar()
        self.v_kelas    = tk.StringVar()

        fields = [("NIS *", self.v_nis), ("Nama Lengkap *", self.v_nama),
                  ("No. Telepon", self.v_telepon)]
        for label, var in fields:
            row = tk.Frame(body, bg=COLORS["card"])
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, font=FONT_LABEL,
                     bg=COLORS["card"], fg=COLORS["text"],
                     width=18, anchor="w").pack(side="left")
            tk.Entry(row, textvariable=var, font=FONT_BODY,
                     relief="flat", bd=0, highlightthickness=1,
                     highlightbackground=COLORS["border"],
                     highlightcolor=COLORS["accent"],
                     width=26).pack(side="left", ipady=5)

        # Jenjang
        row_j = tk.Frame(body, bg=COLORS["card"])
        row_j.pack(fill="x", pady=4)
        tk.Label(row_j, text="Jenjang *", font=FONT_LABEL,
                 bg=COLORS["card"], fg=COLORS["text"],
                 width=18, anchor="w").pack(side="left")
        self.cb_jenjang = ttk.Combobox(row_j,
            values=list(SiswaModel.JENJANG.keys()),
            textvariable=self.v_jenjang, state="readonly",
            width=10, font=FONT_BODY)
        self.cb_jenjang.pack(side="left")
        self.cb_jenjang.bind("<<ComboboxSelected>>", self._on_jenjang)

        # Kelas
        row_k = tk.Frame(body, bg=COLORS["card"])
        row_k.pack(fill="x", pady=4)
        tk.Label(row_k, text="Kelas *", font=FONT_LABEL,
                 bg=COLORS["card"], fg=COLORS["text"],
                 width=18, anchor="w").pack(side="left")
        self.cb_kelas = ttk.Combobox(row_k, textvariable=self.v_kelas,
                                      state="readonly", width=14, font=FONT_BODY)
        self.cb_kelas.pack(side="left")

        if self.siswa:
            self._populate()

        btns = tk.Frame(fc, bg=COLORS["card"])
        btns.pack(fill="x", padx=20, pady=(10, 16))
        action_btn(btns, "Simpan", self._save, kind="primary").pack(side="right")
        action_btn(btns, "Batal", self.win.destroy,
                   kind="secondary").pack(side="right", padx=(0, 8))

    def _on_jenjang(self, e=None):
        j = self.v_jenjang.get()
        self.cb_kelas.configure(values=SiswaModel.JENJANG.get(j, []))
        self.v_kelas.set("")

    def _populate(self):
        s = self.siswa
        self.v_nis.set(s.get("nis") or "")
        self.v_nama.set(s["nama"])
        self.v_telepon.set(s.get("telepon") or "")

        jenjang = s.get("jenjang") or ""
        kelas = s.get("kelas") or ""
        if jenjang in SiswaModel.JENJANG:
            self.v_jenjang.set(jenjang)
            self._on_jenjang()
            if kelas in SiswaModel.JENJANG.get(jenjang, []):
                self.v_kelas.set(kelas)
        # Jika jenjang masih '-' (siswa auto-register), biarkan kosong dan admin memilih sendiri saat melengkapi data.
        # supaya admin memilih sendiri saat melengkapi data.

    def _save(self):
        nis     = self.v_nis.get().strip()
        nama    = self.v_nama.get().strip()
        telepon = self.v_telepon.get().strip()
        jenjang = self.v_jenjang.get()
        kelas   = self.v_kelas.get()

        if not all([nis, nama, jenjang, kelas]):
            messagebox.showwarning("Validasi", "Isi semua kolom wajib (*)", parent=self.win)
            return

        if self.siswa:
            ok, msg = SiswaModel.update(self.siswa["id"], nis, nama, kelas, jenjang, telepon)
        else:
            ok, msg = SiswaModel.add(nis, nama, kelas, jenjang, telepon)

        if ok:
            messagebox.showinfo("Berhasil", msg, parent=self.win)
            if self.on_save:
                self.on_save()
            self.win.destroy()
        else:
            messagebox.showerror("Gagal", msg, parent=self.win)


class RiwayatSiswa:
    def __init__(self, parent, siswa):
        self.siswa = siswa
        self.win = modal(parent, f"Riwayat Peminjaman – {siswa['nama']}",
                         width=700, height=420)
        self._build()

    def _build(self):
        from models.database import PeminjamanModel
        from views.widgets import build_treeview

        nis = self.siswa.get('nis') or '-'
        jenjang = self.siswa.get('jenjang') or '-'
        kelas = self.siswa.get('kelas') or '-'
        tk.Label(self.win,
                 text=f"📋  {self.siswa['nama']}  |  NIS: {nis}  |  {jenjang} {kelas}",
                 font=FONT_LABEL, bg=COLORS["bg"],
                 fg=COLORS["text"]).pack(anchor="w", padx=16, pady=(12, 6))

        cols = ["Judul Buku", "Mata Pelajaran", "Tgl Pinjam",
                "Wajib Kembali", "Tgl Dikembalikan", "Status"]
        widths = {"Judul Buku": 220, "Mata Pelajaran": 140,
                  "Tgl Pinjam": 100, "Wajib Kembali": 110,
                  "Tgl Dikembalikan": 120, "Status": 90}

        frame, tree = build_treeview(self.win, cols, widths, height=14)
        frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        riwayat = PeminjamanModel.get_by_siswa(self.siswa["id"])
        for i, p in enumerate(riwayat):
            tag = "alt" if i % 2 else ""
            if p["status"] == "dipinjam":
                tag = "warning"
            tree.insert("", "end", values=(
                p["judul"], p["mata_pelajaran"],
                p["tgl_pinjam"], p["tgl_kembali_rencana"],
                p.get("tgl_kembali_aktual") or "-",
                p["status"].capitalize()
            ), tags=(tag,))
