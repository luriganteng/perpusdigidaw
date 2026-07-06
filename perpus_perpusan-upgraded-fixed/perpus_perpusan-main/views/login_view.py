import tkinter as tk
from tkinter import ttk, messagebox
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models.database import AdminModel, SiswaModel

COLORS = {
    "bg":         "#F0F4F8",
    "sidebar":    "#1A3C5E",
    "sidebar_h":  "#2A5F8F",
    "accent":     "#E8A020",
    "accent_d":   "#C4841A",
    "card":       "#FFFFFF",
    "text":       "#1C2B3A",
    "text_muted": "#6B7E8F",
    "danger":     "#D94040",
    "success":    "#2E9E5E",
    "warning":    "#E07B1A",
    "border":     "#D0DCE8",
    "header":     "#12263D",
    "siswa_clr":  "#2E9E5E",   # hijau untuk mode siswa
    "admin_clr":  "#1A3C5E",   # biru tua untuk mode admin
}

FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_HEAD  = ("Segoe UI", 13, "bold")
FONT_BODY  = ("Segoe UI", 11)
FONT_SMALL = ("Segoe UI", 9)
FONT_LABEL = ("Segoe UI", 10)
FONT_BTN   = ("Segoe UI", 11, "bold")


# ─────────────────────────────────────────────────────────────────
# Layar pemilihan mode (Admin / Siswa)
# ─────────────────────────────────────────────────────────────────
class ModeSelectWindow:
    def __init__(self, root, on_admin, on_siswa):
        self.root = root
        self.on_admin = on_admin
        self.on_siswa = on_siswa

        root.title("Perpustakaan Digital")
        root.resizable(False, False)
        w, h = 500, 420
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        root.configure(bg=COLORS["bg"])
        self._build()

    def _build(self):
        outer = tk.Frame(self.root, bg=COLORS["bg"])
        outer.pack(expand=True, fill="both", padx=40, pady=30)

        # Top stripe
        tk.Frame(outer, bg=COLORS["sidebar"], height=5).pack(fill="x")

        card = tk.Frame(outer, bg=COLORS["card"],
                        highlightbackground=COLORS["border"],
                        highlightthickness=1)
        card.pack(fill="both", expand=True)

        inner = tk.Frame(card, bg=COLORS["card"])
        inner.pack(padx=36, pady=30, fill="both", expand=True)

        tk.Label(inner, text="📚", font=("Segoe UI", 38),
                 bg=COLORS["card"]).pack()
        tk.Label(inner, text="Perpustakaan Digital",
                 font=FONT_TITLE, bg=COLORS["card"],
                 fg=COLORS["sidebar"]).pack(pady=(6, 2))
        tk.Label(inner, text="Buku Pelajaran SD – SMA",
                 font=FONT_SMALL, bg=COLORS["card"],
                 fg=COLORS["text_muted"]).pack(pady=(0, 28))

        tk.Label(inner, text="Masuk sebagai:",
                 font=FONT_LABEL, bg=COLORS["card"],
                 fg=COLORS["text_muted"]).pack(pady=(0, 12))

        # Dua tombol besar
        row = tk.Frame(inner, bg=COLORS["card"])
        row.pack()

        self._mode_btn(row, "🏫\nAdmin", "Kelola buku & siswa",
                       COLORS["admin_clr"], self.on_admin).pack(
            side="left", padx=10)
        self._mode_btn(row, "🎒\nSiswa", "Pinjam & cek buku",
                       COLORS["siswa_clr"], self.on_siswa).pack(
            side="left", padx=10)

    def _mode_btn(self, parent, title, subtitle, color, cmd):
        frame = tk.Frame(parent, bg=color, cursor="hand2",
                         highlightbackground=color,
                         highlightthickness=2)
        frame.bind("<Button-1>", lambda e: cmd())

        inner = tk.Frame(frame, bg=color)
        inner.pack(padx=22, pady=18)
        inner.bind("<Button-1>", lambda e: cmd())

        lbl_t = tk.Label(inner, text=title, font=("Segoe UI", 14, "bold"),
                         bg=color, fg="#FFFFFF", justify="center")
        lbl_t.pack()
        lbl_t.bind("<Button-1>", lambda e: cmd())

        lbl_s = tk.Label(inner, text=subtitle, font=FONT_SMALL,
                         bg=color, fg="#CCDDCC", justify="center")
        lbl_s.pack(pady=(4, 0))
        lbl_s.bind("<Button-1>", lambda e: cmd())

        # Hover effect
        def on_enter(e):
            darker = self._darken(color)
            for w in [frame, inner, lbl_t, lbl_s]:
                w.configure(bg=darker)
        def on_leave(e):
            for w in [frame, inner, lbl_t, lbl_s]:
                w.configure(bg=color)
        for w in [frame, inner, lbl_t, lbl_s]:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

        return frame

    def _darken(self, hex_color):
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        r = max(0, r - 30)
        g = max(0, g - 30)
        b = max(0, b - 30)
        return f"#{r:02x}{g:02x}{b:02x}"


# ─────────────────────────────────────────────────────────────────
# Login Admin (username + password)
# ─────────────────────────────────────────────────────────────────
class LoginWindow:
    def __init__(self, root, on_success, on_back=None):
        self.root = root
        self.on_success = on_success
        self.on_back = on_back

        root.title("Login Admin – Perpustakaan Digital")
        root.resizable(False, False)
        w, h = 440, 500
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        root.configure(bg=COLORS["bg"])
        self._build()

    def _build(self):
        outer = tk.Frame(self.root, bg=COLORS["bg"])
        outer.pack(expand=True, fill="both", padx=40, pady=30)

        tk.Frame(outer, bg=COLORS["sidebar"], height=5).pack(fill="x")
        card = tk.Frame(outer, bg=COLORS["card"],
                        highlightbackground=COLORS["border"],
                        highlightthickness=1)
        card.pack(fill="both", expand=True)

        inner = tk.Frame(card, bg=COLORS["card"])
        inner.pack(padx=36, pady=32, fill="both", expand=True)

        tk.Label(inner, text="🏫", font=("Segoe UI", 36),
                 bg=COLORS["card"]).pack()
        tk.Label(inner, text="Login Admin",
                 font=FONT_TITLE, bg=COLORS["card"],
                 fg=COLORS["sidebar"]).pack(pady=(6, 2))
        tk.Label(inner, text="Masukkan username dan password",
                 font=FONT_SMALL, bg=COLORS["card"],
                 fg=COLORS["text_muted"]).pack(pady=(0, 22))

        for label, attr, show in [
            ("Username", "ent_user", None),
            ("Password", "ent_pw",   "•"),
        ]:
            tk.Label(inner, text=label, font=FONT_LABEL,
                     bg=COLORS["card"], fg=COLORS["text"],
                     anchor="w").pack(fill="x")
            ent = tk.Entry(inner, font=FONT_BODY,
                           relief="flat", bd=0,
                           highlightthickness=1,
                           highlightbackground=COLORS["border"],
                           highlightcolor=COLORS["accent"],
                           show=show or "")
            ent.pack(fill="x", ipady=8, pady=(2, 12))
            setattr(self, attr, ent)

        tk.Button(inner, text="Masuk", command=self._login,
                  bg=COLORS["admin_clr"], fg="#fff",
                  activebackground=COLORS["sidebar_h"],
                  activeforeground="#fff",
                  font=FONT_BTN, relief="flat", cursor="hand2",
                  pady=9).pack(fill="x", pady=(6, 0))

        if self.on_back:
            tk.Button(inner, text="← Kembali", command=self.on_back,
                      bg=COLORS["card"], fg=COLORS["text_muted"],
                      activebackground=COLORS["border"],
                      font=FONT_SMALL, relief="flat", cursor="hand2",
                      pady=4).pack(fill="x", pady=(8, 0))

        tk.Label(inner, text="Default: admin / admin123",
                 font=FONT_SMALL, bg=COLORS["card"],
                 fg=COLORS["text_muted"]).pack(pady=(10, 0))

        self.ent_user.focus()
        self.root.bind("<Return>", lambda e: self._login())

    def _login(self):
        u = self.ent_user.get().strip()
        p = self.ent_pw.get().strip()
        if not u or not p:
            messagebox.showwarning("Login", "Isi username dan password!")
            return
        admin = AdminModel.login(u, p)
        if admin:
            self.on_success(admin)
        else:
            messagebox.showerror("Login Gagal", "Username atau password salah.")
            self.ent_pw.delete(0, "end")
            self.ent_pw.focus()


# ─────────────────────────────────────────────────────────────────
# Login Siswa — satu window dengan tab switcher "Masuk" / "Daftar"
# langsung berdampingan, strukturnya disamakan dengan tab
# Masuk/Daftar pada mode_select.html di versi website.
# ─────────────────────────────────────────────────────────────────
class LoginSiswaWindow:
    def __init__(self, root, on_success, on_back=None, start_tab="masuk", nama_awal=""):
        self.root = root
        self.on_success = on_success
        self.on_back = on_back
        self.nama_awal = nama_awal

        # Bersihkan dulu kalau ada widget/halaman lain yang masih menempel
        # di root (misalnya balik dari halaman lain).
        for w in root.winfo_children():
            w.destroy()
        root.unbind("<Return>")

        root.title("Login Siswa – Perpustakaan Digital")
        root.resizable(False, False)
        w, h = 460, 640
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        root.configure(bg=COLORS["bg"])

        self._build()
        self._show_tab(start_tab)

    def _build(self):
        outer = tk.Frame(self.root, bg=COLORS["bg"])
        outer.pack(expand=True, fill="both", padx=40, pady=26)

        tk.Frame(outer, bg=COLORS["siswa_clr"], height=5).pack(fill="x")
        card = tk.Frame(outer, bg=COLORS["card"],
                        highlightbackground=COLORS["border"],
                        highlightthickness=1)
        card.pack(fill="both", expand=True)

        inner = tk.Frame(card, bg=COLORS["card"])
        inner.pack(padx=32, pady=26, fill="both", expand=True)

        tk.Label(inner, text="🎒", font=("Segoe UI", 32),
                 bg=COLORS["card"]).pack()
        tk.Label(inner, text="Portal Siswa",
                 font=FONT_TITLE, bg=COLORS["card"],
                 fg=COLORS["siswa_clr"]).pack(pady=(4, 2))
        tk.Label(inner, text="Cari & pinjam buku pelajaran",
                 font=FONT_SMALL, bg=COLORS["card"],
                 fg=COLORS["text_muted"]).pack(pady=(0, 16))

        # ---- Tab switcher: Masuk | Daftar (langsung berdampingan) ----
        tabrow = tk.Frame(inner, bg=COLORS["bg"], highlightthickness=1,
                           highlightbackground=COLORS["border"])
        tabrow.pack(fill="x", pady=(0, 18))

        self.btn_tab_masuk = tk.Button(
            tabrow, text="Masuk", command=lambda: self._show_tab("masuk"),
            font=FONT_BTN, relief="flat", cursor="hand2", bd=0, pady=9)
        self.btn_tab_masuk.pack(side="left", fill="x", expand=True)

        self.btn_tab_daftar = tk.Button(
            tabrow, text="Daftar", command=lambda: self._show_tab("daftar"),
            font=FONT_BTN, relief="flat", cursor="hand2", bd=0, pady=9)
        self.btn_tab_daftar.pack(side="left", fill="x", expand=True)

        # ---- Wadah untuk panel Masuk / Daftar (ditukar via pack) ----
        self.panel_container = tk.Frame(inner, bg=COLORS["card"])
        self.panel_container.pack(fill="both", expand=True)

        self._build_panel_masuk()
        self._build_panel_daftar()

        if self.on_back:
            tk.Button(inner, text="← Kembali ke Pilih Mode", command=self.on_back,
                      bg=COLORS["card"], fg=COLORS["text_muted"],
                      activebackground=COLORS["border"],
                      font=FONT_SMALL, relief="flat", cursor="hand2",
                      pady=4).pack(fill="x", pady=(14, 0))

    # ---- Panel: Masuk ----
    def _build_panel_masuk(self):
        p = tk.Frame(self.panel_container, bg=COLORS["card"])
        self.panel_masuk = p

        tk.Label(p, text="Nama Lengkap", font=FONT_LABEL,
                 bg=COLORS["card"], fg=COLORS["text"], anchor="w").pack(fill="x")
        self.ent_nama = tk.Entry(p, font=FONT_BODY,
                                  relief="flat", bd=0, highlightthickness=1,
                                  highlightbackground=COLORS["border"],
                                  highlightcolor=COLORS["siswa_clr"])
        self.ent_nama.insert(0, self.nama_awal)
        self.ent_nama.pack(fill="x", ipady=8, pady=(2, 16))

        tk.Button(p, text="Masuk sebagai Siswa", command=self._login,
                  bg=COLORS["siswa_clr"], fg="#fff",
                  activebackground="#247A4A", activeforeground="#fff",
                  font=FONT_BTN, relief="flat", cursor="hand2",
                  pady=9).pack(fill="x")

        tk.Label(p, text="Belum punya akun? Klik tab Daftar di atas.",
                 font=FONT_SMALL, bg=COLORS["card"],
                 fg=COLORS["text_muted"]).pack(pady=(12, 0))

    # ---- Panel: Daftar ----
    def _build_panel_daftar(self):
        p = tk.Frame(self.panel_container, bg=COLORS["card"])
        self.panel_daftar = p

        tk.Label(p, text="Nama Lengkap", font=FONT_LABEL,
                 bg=COLORS["card"], fg=COLORS["text"], anchor="w").pack(fill="x")
        self.ent_d_nama = tk.Entry(p, font=FONT_BODY,
                                    relief="flat", bd=0, highlightthickness=1,
                                    highlightbackground=COLORS["border"],
                                    highlightcolor=COLORS["siswa_clr"])
        self.ent_d_nama.pack(fill="x", ipady=8, pady=(2, 10))

        tk.Label(p, text="NIS", font=FONT_LABEL,
                 bg=COLORS["card"], fg=COLORS["text"], anchor="w").pack(fill="x")
        self.ent_d_nis = tk.Entry(p, font=FONT_BODY,
                                   relief="flat", bd=0, highlightthickness=1,
                                   highlightbackground=COLORS["border"],
                                   highlightcolor=COLORS["siswa_clr"])
        self.ent_d_nis.pack(fill="x", ipady=8, pady=(2, 10))

        row = tk.Frame(p, bg=COLORS["card"])
        row.pack(fill="x", pady=(0, 10))

        col_j = tk.Frame(row, bg=COLORS["card"])
        col_j.pack(side="left", fill="x", expand=True, padx=(0, 6))
        tk.Label(col_j, text="Jenjang", font=FONT_LABEL,
                 bg=COLORS["card"], fg=COLORS["text"], anchor="w").pack(fill="x")
        self.v_jenjang = tk.StringVar(value="")
        self.cb_jenjang = ttk.Combobox(
            col_j, values=list(SiswaModel.JENJANG.keys()),
            textvariable=self.v_jenjang, state="readonly", font=FONT_BODY)
        self.cb_jenjang.pack(fill="x", ipady=4, pady=(2, 0))
        self.cb_jenjang.bind("<<ComboboxSelected>>", self._on_jenjang_ganti)

        col_k = tk.Frame(row, bg=COLORS["card"])
        col_k.pack(side="left", fill="x", expand=True, padx=(6, 0))
        tk.Label(col_k, text="Kelas", font=FONT_LABEL,
                 bg=COLORS["card"], fg=COLORS["text"], anchor="w").pack(fill="x")
        self.v_kelas = tk.StringVar(value="")
        self.cb_kelas = ttk.Combobox(col_k, values=[],
                                      textvariable=self.v_kelas,
                                      state="readonly", font=FONT_BODY)
        self.cb_kelas.pack(fill="x", ipady=4, pady=(2, 0))

        tk.Label(p, text="No. Telepon", font=FONT_LABEL,
                 bg=COLORS["card"], fg=COLORS["text"], anchor="w").pack(fill="x")
        self.ent_d_telepon = tk.Entry(p, font=FONT_BODY,
                                       relief="flat", bd=0, highlightthickness=1,
                                       highlightbackground=COLORS["border"],
                                       highlightcolor=COLORS["siswa_clr"])
        self.ent_d_telepon.pack(fill="x", ipady=8, pady=(2, 16))

        tk.Button(p, text="Daftar & Masuk", command=self._daftar,
                  bg=COLORS["siswa_clr"], fg="#fff",
                  activebackground="#247A4A", activeforeground="#fff",
                  font=FONT_BTN, relief="flat", cursor="hand2",
                  pady=9).pack(fill="x")

        tk.Label(p, text="Sudah punya akun? Klik tab Masuk di atas.",
                 font=FONT_SMALL, bg=COLORS["card"],
                 fg=COLORS["text_muted"]).pack(pady=(12, 0))

    # ---- Ganti tab aktif ----
    def _show_tab(self, tab):
        is_daftar = (tab == "daftar")

        if is_daftar:
            self.panel_masuk.pack_forget()
            self.panel_daftar.pack(fill="both", expand=True)
        else:
            self.panel_daftar.pack_forget()
            self.panel_masuk.pack(fill="both", expand=True)

        aktif_bg, aktif_fg = COLORS["siswa_clr"], "#fff"
        nonaktif_bg, nonaktif_fg = COLORS["bg"], COLORS["text_muted"]

        self.btn_tab_masuk.configure(
            bg=(nonaktif_bg if is_daftar else aktif_bg),
            fg=(nonaktif_fg if is_daftar else aktif_fg),
            activebackground=(nonaktif_bg if is_daftar else aktif_bg))
        self.btn_tab_daftar.configure(
            bg=(aktif_bg if is_daftar else nonaktif_bg),
            fg=(aktif_fg if is_daftar else nonaktif_fg),
            activebackground=(aktif_bg if is_daftar else nonaktif_bg))

        self.root.unbind("<Return>")
        if is_daftar:
            self.root.bind("<Return>", lambda e: self._daftar())
            self.ent_d_nama.focus()
        else:
            self.root.bind("<Return>", lambda e: self._login())
            self.ent_nama.focus()

    def _on_jenjang_ganti(self, event=None):
        pilihan = SiswaModel.JENJANG.get(self.v_jenjang.get(), [])
        self.cb_kelas.configure(values=pilihan)
        self.v_kelas.set("")

    # ---- Aksi: Masuk ----
    def _login(self):
        nama = self.ent_nama.get().strip()
        if not nama:
            messagebox.showwarning("Login", "Ketik namamu terlebih dahulu!")
            return

        hasil = SiswaModel.cek_nama_terdaftar(nama)

        if not hasil:
            # Nama belum terdaftar → arahkan ke tab Daftar, nama dibawa otomatis.
            messagebox.showinfo(
                "Belum Terdaftar",
                "Nama ini belum terdaftar. Silakan lengkapi form Daftar dulu."
            )
            self.ent_d_nama.delete(0, "end")
            self.ent_d_nama.insert(0, nama)
            self._show_tab("daftar")
            return

        if len(hasil) == 1:
            self.on_success(hasil[0])
            return

        # Lebih dari satu siswa dengan nama yang sama → minta pilih
        self._tampilkan_pilihan(hasil)

    def _tampilkan_pilihan(self, daftar_siswa):
        win = tk.Toplevel(self.root)
        win.title("Pilih Akun")
        win.configure(bg=COLORS["bg"])
        win.resizable(False, False)
        win.grab_set()
        w, h = 420, 360
        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        win.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        inner = tk.Frame(win, bg=COLORS["card"],
                         highlightbackground=COLORS["border"],
                         highlightthickness=1)
        inner.pack(fill="both", expand=True, padx=16, pady=16)

        tk.Label(inner,
                 text=f"Ditemukan {len(daftar_siswa)} siswa dengan nama yang sama.\nPilih akunmu:",
                 font=FONT_LABEL, bg=COLORS["card"], fg=COLORS["text"],
                 justify="left", wraplength=360).pack(anchor="w", padx=16, pady=(16, 10))

        list_frame = tk.Frame(inner, bg=COLORS["card"])
        list_frame.pack(fill="both", expand=True, padx=16)

        for s in daftar_siswa:
            info = s.get("jenjang") or "-"
            kelas = s.get("kelas") or "-"
            nis = s.get("nis") or "Belum ada NIS"
            sub = f"{info} {kelas}  •  {nis}" if info != "-" else "Akun otomatis (belum dilengkapi admin)"

            btn = tk.Button(
                list_frame,
                text=f"{s['nama']}\n{sub}",
                font=FONT_BODY, justify="left", anchor="w",
                bg=COLORS["bg"], fg=COLORS["text"],
                activebackground=COLORS["siswa_clr"],
                activeforeground="#fff",
                relief="flat", cursor="hand2", pady=8, padx=12,
                command=lambda sd=s: self._pilih_akun(win, sd)
            )
            btn.pack(fill="x", pady=3)

        tk.Button(inner, text="Batal", command=win.destroy,
                  bg=COLORS["card"], fg=COLORS["text_muted"],
                  activebackground=COLORS["border"],
                  font=FONT_SMALL, relief="flat", cursor="hand2",
                  pady=6).pack(fill="x", padx=16, pady=(10, 16))

    def _pilih_akun(self, win, siswa):
        win.destroy()
        self.on_success(siswa)

    # ---- Aksi: Daftar ----
    def _daftar(self):
        nama = self.ent_d_nama.get().strip()
        nis = self.ent_d_nis.get().strip()
        jenjang = self.v_jenjang.get()
        kelas = self.v_kelas.get()
        telepon = self.ent_d_telepon.get().strip()

        # Validasi sama seperti route /daftar/siswa di versi website:
        # semua kolom wajib diisi.
        if not all([nama, nis, jenjang, kelas, telepon]):
            messagebox.showwarning(
                "Validasi",
                "Semua kolom (nama, NIS, jenjang, kelas, no. telepon) wajib diisi."
            )
            return

        ok, hasil = SiswaModel.daftar_lengkap(nama, nis, jenjang, kelas, telepon)
        if not ok:
            messagebox.showerror("Gagal", hasil)
            return

        self.root.unbind("<Return>")
        messagebox.showinfo(
            "Selamat Datang! 🎉",
            f"Halo, {hasil['nama']}!\n\nAkun kamu berhasil dibuat."
        )
        self.on_success(hasil)
