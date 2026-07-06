import sqlite3
import hashlib
import os
from datetime import datetime, timedelta


DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "perpustakaan.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Siswa: NIS/kelas/jenjang sekarang opsional (bisa null)
    # auto_registered = 1 berarti siswa daftar sendiri lewat login
    c.executescript("""
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            nama TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS siswa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nis TEXT,
            nama TEXT NOT NULL,
            kelas TEXT DEFAULT '-',
            jenjang TEXT DEFAULT '-',
            telepon TEXT,
            auto_registered INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS buku (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isbn TEXT UNIQUE,
            judul TEXT NOT NULL,
            pengarang TEXT NOT NULL,
            penerbit TEXT,
            tahun_terbit INTEGER,
            jenjang TEXT NOT NULL,
            kelas TEXT NOT NULL,
            mata_pelajaran TEXT NOT NULL,
            stok INTEGER DEFAULT 1,
            stok_tersedia INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS peminjaman (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            siswa_id INTEGER NOT NULL,
            buku_id INTEGER NOT NULL,
            tgl_pinjam TEXT NOT NULL,
            tgl_kembali_rencana TEXT NOT NULL,
            tgl_kembali_aktual TEXT,
            status TEXT DEFAULT 'dipinjam',
            admin_id INTEGER,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (siswa_id) REFERENCES siswa(id),
            FOREIGN KEY (buku_id) REFERENCES buku(id),
            FOREIGN KEY (admin_id) REFERENCES admin(id)
        );
    """)

    # Migrasi DB lama: tambah kolom auto_registered jika belum ada
    cols_info = c.execute("PRAGMA table_info(siswa)").fetchall()
    cols = [row[1] for row in cols_info]
    if "auto_registered" not in cols:
        c.execute("ALTER TABLE siswa ADD COLUMN auto_registered INTEGER DEFAULT 0")

    # Migrasi DB lama: kolom 'nis' mungkin masih NOT NULL (skema versi awal).
    # SQLite tidak bisa ALTER COLUMN langsung, jadi rebuild tabel siswa.
    nis_col = next((row for row in cols_info if row[1] == "nis"), None)
    if nis_col is not None and nis_col[3] == 1:  # notnull == 1 berarti masih NOT NULL
        c.executescript("""
            ALTER TABLE siswa RENAME TO siswa_old;

            CREATE TABLE siswa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nis TEXT,
                nama TEXT NOT NULL,
                kelas TEXT DEFAULT '-',
                jenjang TEXT DEFAULT '-',
                telepon TEXT,
                auto_registered INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now','localtime'))
            );

            INSERT INTO siswa (id, nis, nama, kelas, jenjang, telepon, auto_registered, created_at)
            SELECT id, nis, nama, kelas, jenjang, telepon,
                   COALESCE(auto_registered, 0), created_at
            FROM siswa_old;

            DROP TABLE siswa_old;
        """)

    # Migrasi: pastikan kolom dipinjam_oleh ada di peminjaman (untuk versi web sinkron, opsional)
    pem_cols = [row[1] for row in c.execute("PRAGMA table_info(peminjaman)").fetchall()]
    if "dipinjam_oleh" not in pem_cols:
        c.execute("ALTER TABLE peminjaman ADD COLUMN dipinjam_oleh TEXT DEFAULT 'admin'")

    # Perbaikan DB lama: migrasi rebuild tabel 'siswa' di atas sempat meninggalkan
    # foreign key di 'peminjaman' yang masih menunjuk ke "siswa_old" (tabel yang
    # sudah dihapus). Ini bikin SEMUA percobaan minjam buku gagal diam-diam
    # (FOREIGN KEY constraint failed), sehingga data tidak pernah masuk ke
    # peminjaman/peminjaman aktif. Deteksi dan perbaiki dengan rebuild tabel
    # peminjaman supaya foreign key-nya menunjuk ke 'siswa' yang benar.
    pem_sql_row = c.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='peminjaman'"
    ).fetchone()
    if pem_sql_row and "siswa_old" in (pem_sql_row[0] or ""):
        c.execute("PRAGMA foreign_keys = OFF")
        c.executescript("""
            ALTER TABLE peminjaman RENAME TO peminjaman_old;

            CREATE TABLE peminjaman (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                siswa_id INTEGER NOT NULL,
                buku_id INTEGER NOT NULL,
                tgl_pinjam TEXT NOT NULL,
                tgl_kembali_rencana TEXT NOT NULL,
                tgl_kembali_aktual TEXT,
                status TEXT DEFAULT 'dipinjam',
                admin_id INTEGER,
                created_at TEXT DEFAULT (datetime('now','localtime')),
                dipinjam_oleh TEXT DEFAULT 'admin',
                FOREIGN KEY (siswa_id) REFERENCES siswa(id),
                FOREIGN KEY (buku_id) REFERENCES buku(id),
                FOREIGN KEY (admin_id) REFERENCES admin(id)
            );

            INSERT INTO peminjaman (id, siswa_id, buku_id, tgl_pinjam, tgl_kembali_rencana,
                                     tgl_kembali_aktual, status, admin_id, created_at, dipinjam_oleh)
            SELECT id, siswa_id, buku_id, tgl_pinjam, tgl_kembali_rencana,
                   tgl_kembali_aktual, status, admin_id, created_at, dipinjam_oleh
            FROM peminjaman_old;

            DROP TABLE peminjaman_old;
        """)
        c.execute("PRAGMA foreign_keys = ON")

    # NIS harus unik antar siswa (kolom boleh NULL/kosong untuk data lama),
    # supaya proses signin (nama + NIS) tidak salah sasaran ke siswa lain.
    # Ditaruh setelah migrasi di atas supaya tetap terpasang walau tabel 'siswa'
    # sempat di-rebuild di alur migrasi lama.
    c.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_siswa_nis_unik
        ON siswa(nis) WHERE nis IS NOT NULL AND nis <> ''
    """)

    # Seed admin default
    if not c.execute("SELECT id FROM admin WHERE username = 'admin'").fetchone():
        pw = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute("INSERT INTO admin (username, password, nama) VALUES (?, ?, ?)",
                  ("admin", pw, "Administrator"))

    conn.commit()
    conn.close()


class AdminModel:
    @staticmethod
    def login(username, password):
        conn = get_connection()
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        row = conn.execute(
            "SELECT * FROM admin WHERE username=? AND password=?",
            (username, pw_hash)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_all():
        conn = get_connection()
        rows = conn.execute("SELECT * FROM admin ORDER BY nama").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def add(username, password, nama):
        conn = get_connection()
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            conn.execute("INSERT INTO admin (username, password, nama) VALUES (?,?,?)",
                         (username, pw_hash, nama))
            conn.commit()
            return True, "Admin berhasil ditambahkan"
        except sqlite3.IntegrityError:
            return False, "Username sudah digunakan"
        finally:
            conn.close()

    @staticmethod
    def change_password(admin_id, old_pw, new_pw):
        conn = get_connection()
        old_hash = hashlib.sha256(old_pw.encode()).hexdigest()
        new_hash = hashlib.sha256(new_pw.encode()).hexdigest()
        row = conn.execute("SELECT id FROM admin WHERE id=? AND password=?",
                           (admin_id, old_hash)).fetchone()
        if not row:
            conn.close()
            return False, "Password lama salah"
        conn.execute("UPDATE admin SET password=? WHERE id=?", (new_hash, admin_id))
        conn.commit()
        conn.close()
        return True, "Password berhasil diubah"


class SiswaModel:
    JENJANG = {
        "SD":  [f"Kelas {i}" for i in range(1, 7)],
        "SMP": [f"Kelas {i}" for i in range(7, 10)],
        "SMA": [f"Kelas {i}" for i in range(10, 13)],
    }

    @staticmethod
    def login_atau_daftar(nama):
        """
        Cari siswa berdasarkan nama (case-insensitive).
        - Jika sudah ada → kembalikan data siswa tersebut (langsung masuk).
        - Jika belum ada → auto-register dengan nama itu, lalu kembalikan data baru.
        Mengembalikan (siswa_dict, is_new: bool)
        """
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM siswa WHERE LOWER(TRIM(nama)) = LOWER(TRIM(?))",
            (nama,)
        ).fetchall()

        if rows:
            # Sudah terdaftar — jika lebih dari satu nama sama, kembalikan semua
            conn.close()
            return [dict(r) for r in rows], False
        else:
            # Belum ada → daftar otomatis
            cur = conn.execute(
                "INSERT INTO siswa (nama, nis, kelas, jenjang, auto_registered) VALUES (?, NULL, '-', '-', 1)",
                (nama.strip(),)
            )
            conn.commit()
            siswa_id = cur.lastrowid
            row = conn.execute("SELECT * FROM siswa WHERE id=?", (siswa_id,)).fetchone()
            conn.close()
            return [dict(row)], True

    @staticmethod
    def login(nama, nis):
        """
        Signin murid: cocokkan nama DAN NIS sekaligus (case-insensitive, trim spasi).
        Dipakai untuk login setelah murid sudah pernah signup dengan data lengkap.
        Mengembalikan dict siswa jika cocok, atau None jika tidak ditemukan.
        """
        conn = get_connection()
        row = conn.execute(
            """SELECT * FROM siswa
               WHERE LOWER(TRIM(nama)) = LOWER(TRIM(?))
                 AND LOWER(TRIM(COALESCE(nis,''))) = LOWER(TRIM(?))
                 AND nis IS NOT NULL AND nis <> ''""",
            (nama, nis)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def cek_nama_terdaftar(nama):
        """
        Cek apakah nama sudah ada di database, tanpa membuat data baru.
        Mengembalikan list siswa yang cocok (bisa kosong).
        """
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM siswa WHERE LOWER(TRIM(nama)) = LOWER(TRIM(?))",
            (nama,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def daftar_lengkap(nama, nis, jenjang, kelas, telepon=""):
        """
        Registrasi mandiri siswa baru (login siswa) dengan data lengkap:
        nama, NIS, jenjang, kelas, no. telepon.
        Dipakai setelah nama dipastikan belum terdaftar.
        """
        conn = get_connection()
        try:
            cur = conn.execute(
                """INSERT INTO siswa (nis, nama, kelas, jenjang, telepon, auto_registered)
                   VALUES (?,?,?,?,?,1)""",
                (nis or None, nama.strip(), kelas, jenjang, telepon)
            )
            conn.commit()
            siswa_id = cur.lastrowid
            row = conn.execute("SELECT * FROM siswa WHERE id=?", (siswa_id,)).fetchone()
            return True, dict(row)
        except sqlite3.IntegrityError:
            return False, "NIS sudah digunakan siswa lain"
        finally:
            conn.close()

    @staticmethod
    def login_by_nama(nama):
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM siswa WHERE LOWER(TRIM(nama)) = LOWER(TRIM(?))",
            (nama,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_all(search=""):
        conn = get_connection()
        query = """
            SELECT s.*,
                   COUNT(CASE WHEN p.status='dipinjam' THEN 1 END) as pinjam_aktif
            FROM siswa s
            LEFT JOIN peminjaman p ON s.id = p.siswa_id
            WHERE s.nama LIKE ? OR COALESCE(s.nis,'') LIKE ?
            GROUP BY s.id
            ORDER BY s.nama
        """
        rows = conn.execute(query, (f"%{search}%", f"%{search}%")).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(siswa_id):
        conn = get_connection()
        row = conn.execute("SELECT * FROM siswa WHERE id=?", (siswa_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def add(nis, nama, kelas, jenjang, telepon=""):
        """Tambah siswa manual oleh admin (NIS tetap opsional)."""
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO siswa (nis, nama, kelas, jenjang, telepon, auto_registered) VALUES (?,?,?,?,?,0)",
                (nis or None, nama, kelas, jenjang, telepon)
            )
            conn.commit()
            return True, "Siswa berhasil ditambahkan"
        except sqlite3.IntegrityError:
            return False, "NIS sudah terdaftar"
        finally:
            conn.close()

    @staticmethod
    def update(siswa_id, nis, nama, kelas, jenjang, telepon=""):
        conn = get_connection()
        try:
            conn.execute(
                "UPDATE siswa SET nis=?, nama=?, kelas=?, jenjang=?, telepon=? WHERE id=?",
                (nis or None, nama, kelas, jenjang, telepon, siswa_id)
            )
            conn.commit()
            return True, "Data siswa berhasil diperbarui"
        except sqlite3.IntegrityError:
            return False, "NIS sudah digunakan siswa lain"
        finally:
            conn.close()

    @staticmethod
    def delete(siswa_id):
        conn = get_connection()
        aktif = conn.execute(
            "SELECT id FROM peminjaman WHERE siswa_id=? AND status='dipinjam'",
            (siswa_id,)
        ).fetchone()
        if aktif:
            conn.close()
            return False, "Siswa masih memiliki peminjaman aktif"
        conn.execute("DELETE FROM siswa WHERE id=?", (siswa_id,))
        conn.commit()
        conn.close()
        return True, "Siswa berhasil dihapus"


class BukuModel:
    JENJANG = ["SD", "SMP", "SMA"]
    KELAS_MAP = {
        "SD":  [str(i) for i in range(1, 7)],
        "SMP": [str(i) for i in range(7, 10)],
        "SMA": [str(i) for i in range(10, 13)],
    }
    MAPEL_MAP = {
        "SD":  ["Bahasa Indonesia", "Matematika", "IPA", "IPS", "PKn", "Agama",
                "PJOK", "SBdP", "Bahasa Inggris", "Tematik"],
        "SMP": ["Bahasa Indonesia", "Matematika", "IPA", "IPS", "PKn",
                "Bahasa Inggris", "Agama", "PJOK", "Seni Budaya", "Prakarya", "BK"],
        "SMA": ["Bahasa Indonesia", "Matematika", "Fisika", "Kimia", "Biologi",
                "Sejarah", "Geografi", "Ekonomi", "Sosiologi", "Bahasa Inggris",
                "PKn", "Agama", "PJOK", "Seni Budaya", "Prakarya/TIK", "BK"],
    }

    @staticmethod
    def get_all(search="", jenjang="", kelas="", mapel=""):
        conn = get_connection()
        query = "SELECT * FROM buku WHERE 1=1"
        params = []
        if search:
            query += " AND (judul LIKE ? OR pengarang LIKE ? OR isbn LIKE ?)"
            params += [f"%{search}%", f"%{search}%", f"%{search}%"]
        if jenjang:
            query += " AND jenjang=?"
            params.append(jenjang)
        if kelas:
            query += " AND kelas=?"
            params.append(kelas)
        if mapel:
            query += " AND mata_pelajaran=?"
            params.append(mapel)
        query += " ORDER BY jenjang, kelas, mata_pelajaran, judul"
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(buku_id):
        conn = get_connection()
        row = conn.execute("SELECT * FROM buku WHERE id=?", (buku_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def add(isbn, judul, pengarang, penerbit, tahun, jenjang, kelas, mapel, stok):
        conn = get_connection()
        try:
            conn.execute(
                """INSERT INTO buku
                   (isbn, judul, pengarang, penerbit, tahun_terbit, jenjang, kelas, mata_pelajaran, stok, stok_tersedia)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (isbn, judul, pengarang, penerbit, tahun, jenjang, kelas, mapel, stok, stok)
            )
            conn.commit()
            return True, "Buku berhasil ditambahkan"
        except sqlite3.IntegrityError:
            return False, "ISBN sudah terdaftar"
        finally:
            conn.close()

    @staticmethod
    def update(buku_id, isbn, judul, pengarang, penerbit, tahun, jenjang, kelas, mapel, stok):
        conn = get_connection()
        buku = conn.execute("SELECT stok, stok_tersedia FROM buku WHERE id=?", (buku_id,)).fetchone()
        if not buku:
            conn.close()
            return False, "Buku tidak ditemukan"
        dipinjam = buku["stok"] - buku["stok_tersedia"]
        stok_tersedia_baru = max(0, stok - dipinjam)
        try:
            conn.execute(
                """UPDATE buku SET isbn=?, judul=?, pengarang=?, penerbit=?, tahun_terbit=?,
                   jenjang=?, kelas=?, mata_pelajaran=?, stok=?, stok_tersedia=? WHERE id=?""",
                (isbn, judul, pengarang, penerbit, tahun, jenjang, kelas, mapel,
                 stok, stok_tersedia_baru, buku_id)
            )
            conn.commit()
            return True, "Data buku berhasil diperbarui"
        except sqlite3.IntegrityError:
            return False, "ISBN sudah digunakan buku lain"
        finally:
            conn.close()

    @staticmethod
    def delete(buku_id):
        conn = get_connection()
        aktif = conn.execute(
            "SELECT id FROM peminjaman WHERE buku_id=? AND status='dipinjam'",
            (buku_id,)
        ).fetchone()
        if aktif:
            conn.close()
            return False, "Buku sedang dipinjam, tidak bisa dihapus"
        conn.execute("DELETE FROM buku WHERE id=?", (buku_id,))
        conn.commit()
        conn.close()
        return True, "Buku berhasil dihapus"


class PeminjamanModel:
    DURASI_HARI = 30

    @staticmethod
    def get_all(search="", status=""):
        conn = get_connection()
        query = """
            SELECT p.*, s.nama as nama_siswa, s.nis, s.kelas, s.jenjang,
                   b.judul as judul_buku, b.mata_pelajaran,
                   a.nama as nama_admin
            FROM peminjaman p
            JOIN siswa s ON p.siswa_id = s.id
            JOIN buku b ON p.buku_id = b.id
            LEFT JOIN admin a ON p.admin_id = a.id
            WHERE 1=1
        """
        params = []
        if search:
            query += " AND (s.nama LIKE ? OR COALESCE(s.nis,'') LIKE ? OR b.judul LIKE ?)"
            params += [f"%{search}%", f"%{search}%", f"%{search}%"]
        if status:
            query += " AND p.status=?"
            params.append(status)
        query += " ORDER BY p.created_at DESC"
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_siswa(siswa_id):
        conn = get_connection()
        rows = conn.execute("""
            SELECT p.*, b.judul, b.mata_pelajaran
            FROM peminjaman p JOIN buku b ON p.buku_id = b.id
            WHERE p.siswa_id=? ORDER BY p.tgl_pinjam DESC
        """, (siswa_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def pinjam(siswa_id, buku_id, admin_id=None):
        conn = get_connection()
        buku = conn.execute("SELECT stok_tersedia FROM buku WHERE id=?", (buku_id,)).fetchone()
        if not buku or buku["stok_tersedia"] < 1:
            conn.close()
            return False, "Stok buku tidak tersedia"

        aktif = conn.execute(
            "SELECT id FROM peminjaman WHERE siswa_id=? AND buku_id=? AND status='dipinjam'",
            (siswa_id, buku_id)
        ).fetchone()
        if aktif:
            conn.close()
            return False, "Siswa ini sudah meminjam buku yang sama"

        tgl_pinjam = datetime.now().strftime("%Y-%m-%d")
        tgl_kembali = (datetime.now() + timedelta(days=PeminjamanModel.DURASI_HARI)).strftime("%Y-%m-%d")

        conn.execute(
            """INSERT INTO peminjaman (siswa_id, buku_id, tgl_pinjam, tgl_kembali_rencana, admin_id)
               VALUES (?,?,?,?,?)""",
            (siswa_id, buku_id, tgl_pinjam, tgl_kembali, admin_id)
        )
        conn.execute("UPDATE buku SET stok_tersedia = stok_tersedia - 1 WHERE id=?", (buku_id,))
        conn.commit()
        conn.close()
        return True, f"Peminjaman berhasil. Wajib kembali: {tgl_kembali}"

    @staticmethod
    def kembalikan(peminjaman_id):
        conn = get_connection()
        p = conn.execute(
            "SELECT * FROM peminjaman WHERE id=? AND status='dipinjam'", (peminjaman_id,)
        ).fetchone()
        if not p:
            conn.close()
            return False, "Data peminjaman tidak ditemukan atau sudah dikembalikan"

        tgl_aktual = datetime.now().strftime("%Y-%m-%d")
        conn.execute(
            "UPDATE peminjaman SET tgl_kembali_aktual=?, status='dikembalikan' WHERE id=?",
            (tgl_aktual, peminjaman_id)
        )
        conn.execute(
            "UPDATE buku SET stok_tersedia = stok_tersedia + 1 WHERE id=?", (p["buku_id"],)
        )
        conn.commit()
        conn.close()
        return True, "Buku berhasil dikembalikan"

    @staticmethod
    def get_terlambat():
        conn = get_connection()
        hari_ini = datetime.now().strftime("%Y-%m-%d")
        rows = conn.execute("""
            SELECT p.*, s.nama as nama_siswa, s.nis, s.kelas,
                   b.judul as judul_buku,
                   CAST((julianday(?) - julianday(p.tgl_kembali_rencana)) AS INTEGER) as hari_terlambat
            FROM peminjaman p
            JOIN siswa s ON p.siswa_id = s.id
            JOIN buku b ON p.buku_id = b.id
            WHERE p.status='dipinjam' AND p.tgl_kembali_rencana < ?
            ORDER BY hari_terlambat DESC
        """, (hari_ini, hari_ini)).fetchall()
        conn.close()
        return [dict(r) for r in rows]


class LaporanModel:
    @staticmethod
    def statistik_umum():
        conn = get_connection()
        stats = {}
        stats["total_buku"] = conn.execute("SELECT COUNT(*) FROM buku").fetchone()[0]
        stats["total_judul"] = conn.execute("SELECT COUNT(DISTINCT judul) FROM buku").fetchone()[0]
        stats["total_siswa"] = conn.execute("SELECT COUNT(*) FROM siswa").fetchone()[0]
        stats["total_siswa_mandiri"] = conn.execute(
            "SELECT COUNT(*) FROM siswa WHERE auto_registered=1"
        ).fetchone()[0]
        stats["total_pinjam_aktif"] = conn.execute(
            "SELECT COUNT(*) FROM peminjaman WHERE status='dipinjam'"
        ).fetchone()[0]
        stats["total_terlambat"] = conn.execute(
            "SELECT COUNT(*) FROM peminjaman WHERE status='dipinjam' AND tgl_kembali_rencana < date('now')"
        ).fetchone()[0]
        stats["total_dikembalikan"] = conn.execute(
            "SELECT COUNT(*) FROM peminjaman WHERE status='dikembalikan'"
        ).fetchone()[0]
        conn.close()
        return stats

    @staticmethod
    def buku_terpopuler(limit=10):
        conn = get_connection()
        rows = conn.execute("""
            SELECT b.judul, b.jenjang, b.kelas, b.mata_pelajaran,
                   COUNT(p.id) as jumlah_dipinjam
            FROM buku b
            LEFT JOIN peminjaman p ON b.id = p.buku_id
            GROUP BY b.id ORDER BY jumlah_dipinjam DESC LIMIT ?
        """, (limit,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def peminjaman_per_bulan():
        conn = get_connection()
        rows = conn.execute("""
            SELECT strftime('%Y-%m', tgl_pinjam) as bulan, COUNT(*) as jumlah
            FROM peminjaman
            GROUP BY bulan ORDER BY bulan DESC LIMIT 12
        """).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def distribusi_jenjang():
        conn = get_connection()
        rows = conn.execute("""
            SELECT b.jenjang, COUNT(p.id) as jumlah
            FROM buku b
            LEFT JOIN peminjaman p ON b.id = p.buku_id
            GROUP BY b.jenjang
        """).fetchall()
        conn.close()
        return [dict(r) for r in rows]
