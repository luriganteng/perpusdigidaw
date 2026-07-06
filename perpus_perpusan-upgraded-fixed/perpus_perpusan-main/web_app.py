import os
import sys
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, flash

# Pastikan import models bisa jalan
sys.path.insert(0, os.path.dirname(__file__))

from models.database import init_db, AdminModel, SiswaModel, BukuModel, LaporanModel, PeminjamanModel


def create_app():
    app = Flask(__name__, template_folder="web/templates", static_folder="web/static")
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")

    init_db()

    def current_role():
        return session.get("role")

    # -----------------------------
    # Mode select
    # -----------------------------
    @app.get("/")
    def mode_select():
        tab = request.args.get("tab", "siswa-masuk")
        return render_template(
            "mode_select.html",
            active_tab=tab,
            jenjang_map=SiswaModel.JENJANG,
        )

    # -----------------------------
    # Admin auth
    # -----------------------------
    @app.post("/login/admin")
    def login_admin():
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if not username or not password:
            flash("Isi username dan password!", "error")
            return redirect(url_for("mode_select"))

        admin = AdminModel.login(username, password)
        if not admin:
            flash("Username atau password salah.", "error")
            return redirect(url_for("mode_select"))

        session["role"] = "admin"
        session["admin"] = {
            "id": admin.get("id"),
            "nama": admin.get("nama") or admin.get("username") or username,
            "username": admin.get("username"),
        }
        return redirect(url_for("admin_dashboard"))

    # -----------------------------
    # Siswa auth
    # -----------------------------
    @app.post("/login/siswa")
    def login_siswa():
        nama = request.form.get("nama", "").strip()
        nis = request.form.get("nis", "").strip()

        if not nama or not nis:
            flash("Isi nama dan NIS terlebih dahulu!", "error")
            return redirect(url_for("mode_select", tab="siswa-masuk"))

        siswa = SiswaModel.login(nama, nis)
        if not siswa:
            flash("Nama atau NIS tidak cocok / belum terdaftar. Silakan daftar dulu.", "error")
            return redirect(url_for("mode_select", tab="siswa-daftar"))

        session["role"] = "siswa"
        session["siswa"] = siswa
        return redirect(url_for("siswa_beranda"))

    @app.post("/daftar/siswa")
    def daftar_siswa():
        nama = request.form.get("nama", "").strip()
        nis = request.form.get("nis", "").strip()
        jenjang = request.form.get("jenjang", "").strip()
        kelas = request.form.get("kelas", "").strip()
        telepon = request.form.get("telepon", "").strip()

        if not all([nama, nis, jenjang, kelas, telepon]):
            flash("Semua kolom (nama, NIS, jenjang, kelas, no. telepon) wajib diisi.", "error")
            return redirect(url_for("mode_select", tab="siswa-daftar"))

        if jenjang not in SiswaModel.JENJANG or kelas not in SiswaModel.JENJANG.get(jenjang, []):
            flash("Jenjang/kelas tidak valid.", "error")
            return redirect(url_for("mode_select", tab="siswa-daftar"))

        ok, hasil = SiswaModel.daftar_lengkap(nama, nis, jenjang, kelas, telepon)
        if not ok:
            flash(hasil, "error")
            return redirect(url_for("mode_select", tab="siswa-daftar"))

        session["role"] = "siswa"
        session["siswa"] = hasil
        flash(f"Selamat datang, {hasil['nama']}! Akun kamu berhasil dibuat.", "success")
        return redirect(url_for("siswa_beranda"))

    @app.get("/logout")
    def logout():
        session.clear()
        return redirect(url_for("mode_select"))

    # -----------------------------
    # Admin routes
    # -----------------------------
    @app.get("/admin/dashboard")
    def admin_dashboard():
        if current_role() != "admin":
            return redirect(url_for("mode_select"))

        admin = session.get("admin", {})
        stats = LaporanModel.statistik_umum()
        loans = PeminjamanModel.get_all()[:10]
        overdue = PeminjamanModel.get_terlambat()

        return render_template(
            "admin/dashboard.html",
            admin=admin,
            stats=stats,
            loans=loans,
            overdue=overdue,
        )

    @app.get("/admin/siswa-meminjam")
    def admin_siswa_meminjam():
        if current_role() != "admin":
            return redirect(url_for("mode_select"))

        admin = session.get("admin", {})
        # Ambil seluruh peminjaman, lalu saring yang sedang dipinjam
        all_loan = PeminjamanModel.get_all()
        loans = [p for p in all_loan if p.get("status") == "dipinjam"]
        # Urutkan terbaru dulu kalau ada tgl_pinjam
        loans.sort(key=lambda x: x.get("tgl_pinjam") or "0000-00-00", reverse=True)

        return render_template(
            "admin/siswa_meminjam.html",
            admin=admin,
            loans=loans,
        )

    @app.post("/admin/siswa-meminjam/delete")
    def admin_siswa_meminjam_delete():
        if current_role() != "admin":
            return redirect(url_for("mode_select"))

        peminjaman_id = request.form.get("peminjaman_id")
        if not peminjaman_id:
            flash("ID peminjaman tidak ditemukan.", "error")
            return redirect(url_for("admin_siswa_meminjam"))

        # Di model, aksi penghapusan yang relevan adalah mengembalikan buku.
        ok, msg = PeminjamanModel.kembalikan(int(peminjaman_id))
        flash(msg, "success" if ok else "error")
        return redirect(url_for("admin_siswa_meminjam"))


    @app.get("/admin/buku")
    def admin_buku():
        if current_role() != "admin":
            return redirect(url_for("mode_select"))

        search = request.args.get("search", "").strip()
        jenjang = request.args.get("jenjang", "Semua")
        kelas = request.args.get("kelas", "Semua")

        buku_list = BukuModel.get_all(
            search=search,
            jenjang="" if jenjang == "Semua" else jenjang,
            kelas="" if kelas == "Semua" else kelas,
        )

        return render_template(
            "admin/buku_list.html",
            admin=session.get("admin", {}),
            buku_list=buku_list,
            search=search,
            jenjang=jenjang,
            kelas=kelas,
            jenjang_options=BukuModel.JENJANG,
        )

    @app.get("/admin/buku/new")
    def admin_buku_new():
        if current_role() != "admin":
            return redirect(url_for("mode_select"))
        return render_template("admin/buku_form.html", admin=session.get("admin", {}), buku=None)

    @app.get("/admin/buku/<int:buku_id>/edit")
    def admin_buku_edit(buku_id: int):
        if current_role() != "admin":
            return redirect(url_for("mode_select"))

        buku = BukuModel.get_by_id(buku_id)
        if not buku:
            flash("Data buku tidak ditemukan.", "error")
            return redirect(url_for("admin_buku"))

        return render_template("admin/buku_form.html", admin=session.get("admin", {}), buku=buku)

    @app.post("/admin/buku/save")
    def admin_buku_save():
        if current_role() != "admin":
            return redirect(url_for("mode_select"))

        bid = request.form.get("id")
        isbn = request.form.get("isbn", "").strip() or None
        judul = request.form.get("judul", "").strip()
        pengarang = request.form.get("pengarang", "").strip()
        penerbit = request.form.get("penerbit", "").strip() or None
        tahun = request.form.get("tahun", "").strip()
        stok = request.form.get("stok", "").strip()

        jenjang = request.form.get("jenjang", "").strip()
        kelas = request.form.get("kelas", "").strip()
        mapel = request.form.get("mata_pelajaran", "").strip()

        if not all([judul, pengarang, jenjang, kelas, mapel]) or not stok:
            flash("Isi kolom wajib (*) dengan benar.", "error")
            return redirect(request.referrer or url_for("admin_buku"))

        try:
            stok_i = int(stok)
            if stok_i < 1:
                raise ValueError()
        except ValueError:
            flash("Stok harus angka positif.", "error")
            return redirect(request.referrer or url_for("admin_buku"))

        tahun_int = int(tahun) if tahun.isdigit() else None

        if bid:
            ok, msg = BukuModel.update(
                int(bid), isbn, judul, pengarang, penerbit, tahun_int,
                jenjang, kelas, mapel, stok_i
            )
        else:
            ok, msg = BukuModel.add(
                isbn, judul, pengarang, penerbit, tahun_int,
                jenjang, kelas, mapel, stok_i
            )

        flash(msg, "success" if ok else "error")
        return redirect(url_for("admin_buku"))

    @app.post("/admin/buku/delete")
    def admin_buku_delete():
        if current_role() != "admin":
            return redirect(url_for("mode_select"))

        bid = request.form.get("id")
        if not bid:
            flash("ID buku tidak ditemukan.", "error")
            return redirect(url_for("admin_buku"))

        ok, msg = BukuModel.delete(int(bid))
        flash(msg, "success" if ok else "error")
        return redirect(url_for("admin_buku"))

    # -----------------------------
    # Admin: Data Siswa (CRUD)
    # -----------------------------
    @app.get("/admin/siswa")
    def admin_siswa():
        if current_role() != "admin":
            return redirect(url_for("mode_select"))

        search = request.args.get("search", "").strip()
        siswa_list = SiswaModel.get_all(search=search)

        return render_template(
            "admin/siswa_list.html",
            admin=session.get("admin", {}),
            siswa_list=siswa_list,
            search=search,
        )

    @app.get("/admin/siswa/new")
    def admin_siswa_new():
        if current_role() != "admin":
            return redirect(url_for("mode_select"))
        return render_template(
            "admin/siswa_form.html",
            admin=session.get("admin", {}),
            siswa=None,
            jenjang_map=SiswaModel.JENJANG,
        )

    @app.get("/admin/siswa/<int:siswa_id>/edit")
    def admin_siswa_edit(siswa_id: int):
        if current_role() != "admin":
            return redirect(url_for("mode_select"))

        siswa = SiswaModel.get_by_id(siswa_id)
        if not siswa:
            flash("Data siswa tidak ditemukan.", "error")
            return redirect(url_for("admin_siswa"))

        return render_template(
            "admin/siswa_form.html",
            admin=session.get("admin", {}),
            siswa=siswa,
            jenjang_map=SiswaModel.JENJANG,
        )

    @app.post("/admin/siswa/save")
    def admin_siswa_save():
        if current_role() != "admin":
            return redirect(url_for("mode_select"))

        sid = request.form.get("id")
        nis = request.form.get("nis", "").strip() or None
        nama = request.form.get("nama", "").strip()
        jenjang = request.form.get("jenjang", "").strip()
        kelas = request.form.get("kelas", "").strip()
        telepon = request.form.get("telepon", "").strip()

        if not nama:
            flash("Nama siswa wajib diisi.", "error")
            return redirect(request.referrer or url_for("admin_siswa"))

        if sid:
            ok, msg = SiswaModel.update(int(sid), nis, nama, kelas or "-", jenjang or "-", telepon)
        else:
            ok, msg = SiswaModel.add(nis, nama, kelas or "-", jenjang or "-", telepon)

        flash(msg, "success" if ok else "error")
        return redirect(url_for("admin_siswa"))

    @app.post("/admin/siswa/delete")
    def admin_siswa_delete():
        if current_role() != "admin":
            return redirect(url_for("mode_select"))

        sid = request.form.get("id")
        if not sid:
            flash("ID siswa tidak ditemukan.", "error")
            return redirect(url_for("admin_siswa"))

        ok, msg = SiswaModel.delete(int(sid))
        flash(msg, "success" if ok else "error")
        return redirect(url_for("admin_siswa"))

    # -----------------------------
    # Admin: Peminjaman (semua data, bukan cuma yang aktif)
    # -----------------------------
    @app.get("/admin/peminjaman")
    def admin_peminjaman():
        if current_role() != "admin":
            return redirect(url_for("mode_select"))

        search = request.args.get("search", "").strip()
        status = request.args.get("status", "Semua")

        loans = PeminjamanModel.get_all(
            search=search,
            status="" if status == "Semua" else status,
        )

        return render_template(
            "admin/peminjaman_list.html",
            admin=session.get("admin", {}),
            loans=loans,
            search=search,
            status=status,
        )

    @app.post("/admin/peminjaman/kembalikan")
    def admin_peminjaman_kembalikan():
        if current_role() != "admin":
            return redirect(url_for("mode_select"))

        peminjaman_id = request.form.get("peminjaman_id")
        if not peminjaman_id:
            flash("ID peminjaman tidak ditemukan.", "error")
            return redirect(url_for("admin_peminjaman"))

        ok, msg = PeminjamanModel.kembalikan(int(peminjaman_id))
        flash(msg, "success" if ok else "error")
        return redirect(request.referrer or url_for("admin_peminjaman"))

    # -----------------------------
    # Admin: Keterlambatan
    # -----------------------------
    @app.get("/admin/terlambat")
    def admin_terlambat():
        if current_role() != "admin":
            return redirect(url_for("mode_select"))

        overdue = PeminjamanModel.get_terlambat()

        return render_template(
            "admin/terlambat.html",
            admin=session.get("admin", {}),
            overdue=overdue,
        )

    # -----------------------------
    # Admin: Laporan
    # -----------------------------
    @app.get("/admin/laporan")
    def admin_laporan():
        if current_role() != "admin":
            return redirect(url_for("mode_select"))

        stats = LaporanModel.statistik_umum()
        terpopuler = LaporanModel.buku_terpopuler(limit=10)
        per_bulan = LaporanModel.peminjaman_per_bulan()
        distribusi = LaporanModel.distribusi_jenjang()

        return render_template(
            "admin/laporan.html",
            admin=session.get("admin", {}),
            stats=stats,
            terpopuler=terpopuler,
            per_bulan=per_bulan,
            distribusi=distribusi,
        )

    # -----------------------------
    # Siswa routes (sinkron ke database yang sama)
    # -----------------------------
    @app.get("/siswa/beranda")
    def siswa_beranda():
        if current_role() != "siswa":
            return redirect(url_for("mode_select"))

        siswa = session.get("siswa", {})
        riwayat = PeminjamanModel.get_by_siswa(siswa["id"])

        today = datetime.now().strftime("%Y-%m-%d")
        aktif = [p for p in riwayat if p.get("status") == "dipinjam"]
        terlambat = [p for p in aktif if (p.get("tgl_kembali_rencana") or "") < today]

        # Buku yang paling dekat tenggat waktunya, buat ditonjolkan di beranda
        segera = None
        if aktif:
            segera = sorted(aktif, key=lambda p: p.get("tgl_kembali_rencana") or "9999-99-99")[0]

        stats = {
            "pinjam_aktif": len(aktif),
            "terlambat": len(terlambat),
            "total_riwayat": len(riwayat),
        }

        # Rekomendasi buku: prioritaskan yang sesuai jenjang siswa & masih tersedia,
        # lalu lengkapi dengan buku tersedia lainnya kalau jumlahnya kurang.
        semua_tersedia = [b for b in BukuModel.get_all() if (b.get("stok_tersedia") or 0) > 0]
        sesuai_jenjang = [b for b in semua_tersedia if b.get("jenjang") == siswa.get("jenjang")]
        lainnya = [b for b in semua_tersedia if b.get("jenjang") != siswa.get("jenjang")]
        rekomendasi = (sesuai_jenjang + lainnya)[:4]

        return render_template(
            "siswa/beranda.html",
            siswa=siswa,
            stats=stats,
            segera=segera,
            rekomendasi=rekomendasi,
        )

    @app.get("/siswa/cari-buku")
    def siswa_cari_buku():
        if current_role() != "siswa":
            return redirect(url_for("mode_select"))

        siswa = session.get("siswa", {})
        search = request.args.get("search", "").strip()
        jenjang = request.args.get("jenjang", "Semua")
        kelas = request.args.get("kelas", "Semua")
        mapel = request.args.get("mapel", "Semua")

        buku_list = BukuModel.get_all(
            search=search,
            jenjang="" if jenjang == "Semua" else jenjang,
            kelas="" if kelas == "Semua" else kelas,
            mapel="" if mapel == "Semua" else mapel,
        )

        pinjaman_aktif_ids = {
            p["buku_id"] for p in PeminjamanModel.get_by_siswa(siswa["id"])
            if p.get("status") == "dipinjam"
        }

        enriched = []
        for i, b in enumerate(buku_list):
            sudah_pinjam = b["id"] in pinjaman_aktif_ids
            habis = b.get("stok_tersedia", 0) < 1

            if sudah_pinjam:
                status = "✓ Kamu pinjam"
                tag = "warning"
            elif habis:
                status = "Stok habis"
                tag = "danger"
            else:
                status = "✅ Tersedia"
                tag = "success" if i % 2 == 0 else "alt"

            bisa_pinjam = not sudah_pinjam and not habis
            enriched.append({**b, "status": status, "tag": tag, "bisa_pinjam": bisa_pinjam})

        return render_template(
            "siswa/cari_buku.html",
            siswa=siswa,
            search=search,
            jenjang=jenjang,
            kelas=kelas,
            mapel=mapel,
            buku_list=enriched,
            # dipakai buat isi dropdown filter Kelas & Mapel sesuai jenjang yang dipilih
            kelas_map=BukuModel.KELAS_MAP,
            mapel_map=BukuModel.MAPEL_MAP,
        )

    @app.post("/siswa/pinjam")
    def siswa_pinjam():
        if current_role() != "siswa":
            return redirect(url_for("mode_select"))

        siswa = session.get("siswa", {})
        buku_id = request.form.get("buku_id")
        if not buku_id or not buku_id.isdigit():
            flash("Buku tidak ditemukan.", "error")
            return redirect(url_for("siswa_cari_buku"))

        ok, msg = PeminjamanModel.pinjam(siswa["id"], int(buku_id))
        flash(msg, "success" if ok else "error")

        # Balik ke pencarian dengan filter yang sama biar gak reset ke awal
        return redirect(url_for(
            "siswa_cari_buku",
            search=request.form.get("search", ""),
            jenjang=request.form.get("jenjang", "Semua"),
            kelas=request.form.get("kelas", "Semua"),
            mapel=request.form.get("mapel", "Semua"),
        ))

    @app.get("/siswa/pinjaman-aktif")
    def siswa_pinjaman_aktif():
        if current_role() != "siswa":
            return redirect(url_for("mode_select"))

        siswa = session.get("siswa", {})
        riwayat = PeminjamanModel.get_by_siswa(siswa["id"])
        aktif = [p for p in riwayat if p.get("status") == "dipinjam"]

        now = datetime.now()
        rows = []
        terlambat_count = 0

        for p in aktif:
            tgl_kembali_str = p.get("tgl_kembali_rencana")
            if not tgl_kembali_str:
                continue
            tgl_kembali = datetime.strptime(tgl_kembali_str, "%Y-%m-%d")
            sisa = (tgl_kembali - now).days


            if sisa < 0:
                terlambat_count += 1
                sisa_str = f"Terlambat {abs(sisa)} hr"
                status_str = "⚠ Terlambat"
                tag = "danger"
            elif sisa <= 3:
                sisa_str = f"{sisa} hari lagi"
                status_str = "⏰ Segera!"
                tag = "warning"
            else:
                sisa_str = f"{sisa} hari lagi"
                status_str = "✅ Tepat waktu"
                tag = "success"

            rows.append({
                "judul": p.get("judul"),
                "mata_pelajaran": p.get("mata_pelajaran"),
                "jenjang": p.get("jenjang"),
                "tgl_pinjam": p.get("tgl_pinjam"),
                "tgl_kembali_rencana": p.get("tgl_kembali_rencana"),
                "sisa_str": sisa_str,
                "status_str": status_str,
                "tag": tag,
            })

        return render_template(
            "siswa/pinjaman_aktif.html",
            siswa=siswa,
            loans=rows,
            terlambat_count=terlambat_count,
        )

    @app.get("/siswa/riwayat")
    def siswa_riwayat():
        if current_role() != "siswa":
            return redirect(url_for("mode_select"))

        siswa = session.get("siswa", {})
        riwayat = PeminjamanModel.get_by_siswa(siswa["id"])
        today = datetime.now().strftime("%Y-%m-%d")

        rows = []
        for i, p in enumerate(riwayat):
            status = p.get("status")
            tgl_kembali_rencana = p.get("tgl_kembali_rencana")

            if status == "dikembalikan":
                tag = "success" if i % 2 == 0 else "alt"
                status_str = "✅ Dikembalikan"
            elif tgl_kembali_rencana and tgl_kembali_rencana < today:
                tag = "danger"
                status_str = "⚠ Terlambat"
            else:
                tag = "warning"
                status_str = "🔄 Dipinjam"


            rows.append({
                "judul": p.get("judul"),
                "mata_pelajaran": p.get("mata_pelajaran"),
                "tgl_pinjam": p.get("tgl_pinjam"),
                "tgl_kembali_rencana": p.get("tgl_kembali_rencana"),
                "tgl_kembali_aktual": p.get("tgl_kembali_aktual") or "-",
                "status_str": status_str,
                "tag": tag,
            })

        return render_template("siswa/riwayat.html", siswa=siswa, loans=rows)

    return app


if __name__ == "__main__":
    app = create_app()
    # Debug mode nyala secara default buat kemudahan development.
    # Kalau dipakai/di-deploy di luar localhost, set FLASK_DEBUG=0 dulu,
    # soalnya debugger Flask yang aktif bisa dipakai eksekusi kode dari browser.
    debug_mode = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)

