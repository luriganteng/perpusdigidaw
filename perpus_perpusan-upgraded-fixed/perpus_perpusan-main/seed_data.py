#!/usr/bin/env python3
"""
Seed data contoh untuk testing.
Jalankan: python seed_data.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from models.database import init_db, BukuModel, SiswaModel, PeminjamanModel, AdminModel, get_connection
from datetime import datetime, timedelta

def seed():
    init_db()
    print("Memasukkan data contoh...")

    # Buku SD
    buku_sd = [
        ("978-602-01-0001", "Bahasa Indonesia SD Kelas 1", "Tim Penulis Kemendikbud", "Kemendikbud", 2022, "SD", "1", "Bahasa Indonesia", 3),
        ("978-602-01-0002", "Matematika SD Kelas 1", "Tim Penulis Kemendikbud", "Kemendikbud", 2022, "SD", "1", "Matematika", 3),
        ("978-602-01-0003", "Tematik SD Kelas 2 Tema 1", "Tim Penulis", "Erlangga", 2021, "SD", "2", "Tematik", 2),
        ("978-602-01-0004", "IPA SD Kelas 4", "Heri Sulistyanto", "BSE", 2020, "SD", "4", "IPA", 4),
        ("978-602-01-0005", "IPS SD Kelas 5", "Retno Heny", "BSE", 2020, "SD", "5", "IPS", 2),
        ("978-602-01-0006", "Matematika SD Kelas 6", "Mas Titing", "Erlangga", 2021, "SD", "6", "Matematika", 3),
    ]

    # Buku SMP
    buku_smp = [
        ("978-602-02-0001", "Bahasa Indonesia SMP Kelas 7", "E. Kosasih", "Erlangga", 2022, "SMP", "7", "Bahasa Indonesia", 3),
        ("978-602-02-0002", "Matematika SMP Kelas 7", "M. Cholik Adinawan", "Erlangga", 2022, "SMP", "7", "Matematika", 3),
        ("978-602-02-0003", "IPA SMP Kelas 8", "Wahono Widodo", "Kemendikbud", 2021, "SMP", "8", "IPA", 2),
        ("978-602-02-0004", "IPS SMP Kelas 8", "Iwan Setiawan", "Kemendikbud", 2021, "SMP", "8", "IPS", 2),
        ("978-602-02-0005", "Bahasa Inggris SMP Kelas 9", "Utami Widiati", "Kemendikbud", 2022, "SMP", "9", "Bahasa Inggris", 3),
        ("978-602-02-0006", "Matematika SMP Kelas 9", "As'ari", "Kemendikbud", 2021, "SMP", "9", "Matematika", 4),
    ]

    # Buku SMA
    buku_sma = [
        ("978-602-03-0001", "Fisika SMA Kelas 10", "Marthen Kanginan", "Erlangga", 2022, "SMA", "10", "Fisika", 2),
        ("978-602-03-0002", "Kimia SMA Kelas 10", "Unggul Sudarmo", "Erlangga", 2022, "SMA", "10", "Kimia", 2),
        ("978-602-03-0003", "Biologi SMA Kelas 11", "D.A. Pratiwi", "Erlangga", 2021, "SMA", "11", "Biologi", 3),
        ("978-602-03-0004", "Matematika SMA Kelas 11", "Sukino", "Erlangga", 2022, "SMA", "11", "Matematika", 3),
        ("978-602-03-0005", "Ekonomi SMA Kelas 12", "Alam S.", "Esis", 2021, "SMA", "12", "Ekonomi", 2),
        ("978-602-03-0006", "Sejarah Indonesia SMA Kelas 12", "Restu Gunawan", "Kemendikbud", 2021, "SMA", "12", "Sejarah", 2),
    ]

    for b in buku_sd + buku_smp + buku_sma:
        ok, msg = BukuModel.add(*b)
        print(f"  Buku: {b[1][:40]:40s}  {'✓' if ok else '✗'} {msg if not ok else ''}")

    # Siswa
    siswa_data = [
        ("0001", "Andi Pratama", "1", "SD", "081234567890"),
        ("0002", "Budi Santoso", "3", "SD", "081234567891"),
        ("0003", "Citra Dewi", "6", "SD", "081234567892"),
        ("0004", "Dian Rahayu", "7", "SMP", "081234567893"),
        ("0005", "Eko Prasetyo", "8", "SMP", "081234567894"),
        ("0006", "Fani Kusuma", "9", "SMP", "081234567895"),
        ("0007", "Gita Sari", "10", "SMA", "081234567896"),
        ("0008", "Hendra Wijaya", "11", "SMA", "081234567897"),
        ("0009", "Indah Permata", "12", "SMA", "081234567898"),
        ("0010", "Joko Susanto", "4", "SD", "081234567899"),
    ]

    for s in siswa_data:
        ok, msg = SiswaModel.add(*s)
        print(f"  Siswa: {s[1]:20s}  {'✓' if ok else '✗'} {msg if not ok else ''}")

    # Peminjaman contoh
    conn = get_connection()
    admin = conn.execute("SELECT id FROM admin WHERE username='admin'").fetchone()
    conn.close()

    if admin:
        admin_id = admin["id"]
        siswa_list = SiswaModel.get_all()
        buku_list = BukuModel.get_all()

        pinjaman = [
            (1, 1),   # Andi pinjam buku pertama
            (2, 7),   # Budi pinjam buku ke-7
            (4, 7),   # Dian pinjam buku ke-7
            (7, 13),  # Gita pinjam buku ke-13
        ]

        conn = get_connection()
        for siswa_idx, buku_idx in pinjaman:
            if siswa_idx <= len(siswa_list) and buku_idx <= len(buku_list):
                s = siswa_list[siswa_idx - 1]
                b = buku_list[buku_idx - 1]
                ok, msg = PeminjamanModel.pinjam(s["id"], b["id"], admin_id)
                print(f"  Pinjam: {s['nama']:20s} ← {b['judul'][:30]:30s}  {'✓' if ok else '✗'}")

        # Buat satu peminjaman terlambat (manual)
        tgl_pinjam = (datetime.now() - timedelta(days=40)).strftime("%Y-%m-%d")
        tgl_kembali = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        if len(siswa_list) >= 3 and len(buku_list) >= 2:
            s = siswa_list[2]
            b = buku_list[1]
            # Cek dulu stok
            buku_data = BukuModel.get_by_id(b["id"])
            if buku_data and buku_data["stok_tersedia"] > 0:
                conn.execute(
                    """INSERT INTO peminjaman (siswa_id, buku_id, tgl_pinjam, tgl_kembali_rencana, admin_id)
                       VALUES (?,?,?,?,?)""",
                    (s["id"], b["id"], tgl_pinjam, tgl_kembali, admin_id)
                )
                conn.execute("UPDATE buku SET stok_tersedia = stok_tersedia - 1 WHERE id=?",
                             (b["id"],))
                conn.commit()
                print(f"  Terlambat: {s['nama']:20s} ← {b['judul'][:30]:30s}  ✓ (simulasi keterlambatan)")
        conn.close()

    print("\n✅  Data contoh berhasil dimasukkan!")
    print("    Jalankan: python main.py")
    print("    Login: admin / admin123")


if __name__ == "__main__":
    seed()
