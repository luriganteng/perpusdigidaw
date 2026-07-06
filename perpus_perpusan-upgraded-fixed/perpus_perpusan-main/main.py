#!/usr/bin/env python3
"""

Perpustakaan Digital – Buku Pelajaran SD s/d SMA
Mode: Admin (login username+password) | Siswa (login nama saja)
Jalankan: python main.py

"""
import tkinter as tk
import sys, os

sys.path.insert(0, os.path.dirname(__file__))

from models.database import init_db


class App:
    def __init__(self):
        init_db()

        self.root = tk.Tk()
        self.root.title("Perpustakaan Digital")

        try:
            self.root.iconbitmap("assets/icon.ico")
        except Exception:
            pass

        self._show_mode_select()
        self.root.mainloop()

    # ── Mode pilih (Admin / Siswa) ──────────────────────────────
    def _show_mode_select(self):
        self._clear()
        self.root.resizable(False, False)

        from views.login_view import ModeSelectWindow
        ModeSelectWindow(
            self.root,
            on_admin=self._show_login_admin,
            on_siswa=self._show_login_siswa,
        )

    # ── Login Admin ─────────────────────────────────────────────
    def _show_login_admin(self):
        self._clear()
        self.root.resizable(False, False)

        from views.login_view import LoginWindow
        LoginWindow(
            self.root,
            on_success=self._on_login_admin,
            on_back=self._show_mode_select,
        )

    def _on_login_admin(self, admin):
        self._clear()
        self.root.resizable(True, True)

        from views.main_view import MainDashboard
        MainDashboard(self.root, admin, on_logout=self._show_mode_select)

    # ── Login Siswa ─────────────────────────────────────────────
    def _show_login_siswa(self):
        self._clear()
        self.root.resizable(False, False)

        from views.login_view import LoginSiswaWindow
        LoginSiswaWindow(
            self.root,
            on_success=self._on_login_siswa,
            on_back=self._show_mode_select,
        )

    def _on_login_siswa(self, siswa):
        self._clear()
        self.root.resizable(True, True)

        from views.siswa_dashboard import SiswaDashboard
        SiswaDashboard(self.root, siswa, on_logout=self._show_mode_select)

    # ── Helper ──────────────────────────────────────────────────
    def _clear(self):
        for w in self.root.winfo_children():
            w.destroy()


if __name__ == "__main__":
    App()
