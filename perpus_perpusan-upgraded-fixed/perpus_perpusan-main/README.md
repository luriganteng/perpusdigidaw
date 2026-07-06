# Perpustakaan Digital 📚
**Sistem Manajemen Perpustakaan Buku Pelajaran SD – SMA**

---

## Fitur
- 🔐 Login admin
- 📖 Manajemen buku (tambah, edit, hapus, filter per jenjang/kelas)
- 👥 Manajemen siswa (tambah, edit, hapus, riwayat pinjam)
- 🔄 Peminjaman & pengembalian buku (batas 30 hari)
- ⏰ Monitor keterlambatan
- 📊 Laporan & statistik

## Cara Menjalankan

### 1. Pastikan Python 3.8+ terinstall
```bash
python --version
```

### 2. Tidak perlu install library tambahan
Program menggunakan:
- `tkinter` (bawaan Python)
- `sqlite3` (bawaan Python)

### 3. Jalankan program
```bash
python main.py
```

### 4. (Opsional) Load data contoh
```bash
python seed_data.py
python main.py
```

## Login Default
| Username | Password |
|----------|----------|
| admin    | admin123 |

## Struktur Folder
```
perpustakaan_digital/
├── main.py                  ← Entry point
├── seed_data.py             ← Data contoh (opsional)
├── perpustakaan.db          ← Database SQLite (auto-dibuat)
├── models/
│   └── database.py          ← Model OOP + koneksi DB
└── views/
    ├── login_view.py        ← Halaman login
    ├── main_view.py         ← Dashboard & navigasi
    ├── widgets.py           ← Komponen UI reusable
    ├── dashboard_page.py    ← Halaman utama
    ├── buku_page.py         ← Manajemen buku
    ├── siswa_page.py        ← Manajemen siswa
    ├── peminjaman_page.py   ← Peminjaman buku
    ├── terlambat_page.py    ← Keterlambatan & laporan
    └── laporan_page.py      ← Re-export laporan
```

## Jenjang & Kelas yang Didukung
| Jenjang | Kelas |
|---------|-------|
| SD      | 1 – 6 |
| SMP     | 7 – 9 |
| SMA     | 10 – 12 |
