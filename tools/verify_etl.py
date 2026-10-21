import csv
import datetime
import hashlib
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lingkungan import cari_psql, pesan_psql

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DW = os.environ.get("TOKOMAJU_DB_DW", "tokomaju_dw")
DB_OLTP = os.environ.get("TOKOMAJU_DB_OLTP", "tokomaju_oltp")
PGUSER = os.environ.get("PGUSER", "etl")
PGPASSWORD = os.environ.get("PGPASSWORD", "etl_tokomaju")
PGHOST = os.environ.get("PGHOST", "localhost")
PGPORT = os.environ.get("PGPORT", "5432")

BULAN_ANGKA = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "mei": 5,
    "jun": 6,
    "jul": 7,
    "agu": 8,
    "sep": 9,
    "okt": 10,
    "nov": 11,
    "des": 12,
}


def psql_path():
    ditemukan = cari_psql()
    if ditemukan:
        return ditemukan
    raise SystemExit(pesan_psql())


def psql(db, sql):
    env = dict(os.environ)
    env["PGPASSWORD"] = PGPASSWORD
    perintah = [
        psql_path(),
        "-U",
        PGUSER,
        "-d",
        db,
        "-h",
        PGHOST,
        "-p",
        PGPORT,
        "-t",
        "-A",
        "-F",
        "|",
        "-c",
        sql,
    ]
    hasil = subprocess.run(perintah, capture_output=True, text=True, env=env)
    if hasil.returncode != 0:
        print("PSQL GAGAL:", hasil.stderr.strip())
        sys.exit(1)
    return [baris for baris in hasil.stdout.strip().splitlines() if baris != ""]


def ke_int(teks):
    if teks is None:
        return None
    teks = str(teks).strip()
    if teks == "":
        return None
    teks = re.sub(r"^Rp\.?", "", teks, flags=re.IGNORECASE)
    teks = re.sub(r"\s", "", teks)
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", teks):
        teks = teks.replace(".", "")
    if re.fullmatch(r"-?\d+", teks):
        return int(teks)
    return None


def parse_tanggal(teks):
    teks = (teks or "").strip()
    hasil = None
    m = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", teks)
    if m:
        hasil = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    if hasil is None:
        m = re.fullmatch(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", teks)
        if m:
            hasil = (int(m.group(3)), int(m.group(2)), int(m.group(1)))
    if hasil is None:
        m = re.fullmatch(r"(\d{1,2})\s+([A-Za-z]{3,9})\s+(\d{4})", teks)
        if m:
            kunci = m.group(2).lower()[:3]
            if kunci in BULAN_ANGKA:
                hasil = (int(m.group(3)), BULAN_ANGKA[kunci], int(m.group(1)))
    if hasil is None:
        return None
    try:
        datetime.date(hasil[0], hasil[1], hasil[2])
    except ValueError:
        return None
    return hasil


def klasifikasi_baris(baris, idx):
    id_transaksi = baris[idx["id_transaksi"]].strip()
    tanggal = baris[idx["tanggal"]]
    id_produk = baris[idx["id_produk"]].strip()
    id_pelanggan = baris[idx["id_pelanggan"]].strip()
    qty = ke_int(baris[idx["qty"]])
    harga = ke_int(baris[idx["harga_satuan"]])
    metode = baris[idx["metode_bayar"]].strip()
    if id_transaksi == "":
        return "id transaksi kosong", qty, harga
    if parse_tanggal(tanggal) is None:
        return "tanggal tidak valid", qty, harga
    if qty is None:
        return "jumlah terjual tidak valid", qty, harga
    if qty < 0:
        return "jumlah terjual negatif", qty, harga
    if qty == 0:
        return "jumlah terjual nol", qty, harga
    if harga is None:
        return "harga satuan tidak valid", qty, harga
    if harga <= 0:
        return "harga satuan tidak valid", qty, harga
    if id_produk == "":
        return "id produk kosong", qty, harga
    if id_pelanggan == "":
        return "id pelanggan kosong", qty, harga
    if metode == "":
        return "metode bayar kosong", qty, harga
    return "VALID", qty, harga


def baca_sumber(master_produk):
    path = os.path.join(ROOT, "data", "penjualan.csv")
    with open(path, encoding="utf-8") as f:
        baris = list(csv.reader(f, delimiter=";"))
    header = baris[0]
    idx = {h: i for i, h in enumerate(header)}
    data = [b for b in baris[1:] if any(c.strip() for c in b)]
    unik = {}
    for b in data:
        unik.setdefault(b[idx["id_transaksi"]].strip(), b)
    alasan = {}
    karantina = 0
    total_unik = 0
    total_valid = 0
    total_mentah = 0
    for b in data:
        label, qty, harga = klasifikasi_baris(b, idx)
        if qty is not None and harga is not None:
            total_mentah += qty * harga
    for b in unik.values():
        label, qty, harga = klasifikasi_baris(b, idx)
        alasan[label] = alasan.get(label, 0) + 1
        if qty is not None and harga is not None:
            total_unik += qty * harga
        if label == "VALID":
            if b[idx["id_produk"]].strip() not in master_produk:
                karantina += 1
            else:
                total_valid += qty * harga
    return {
        "baris_sumber": len(data),
        "baris_unik": len(unik),
        "duplikat": len(data) - len(unik),
        "total_unik": total_unik,
        "total_mentah": total_mentah,
        "total_valid": total_valid,
        "karantina": karantina,
        "alasan": alasan,
    }


def main():
    master_produk = set(psql(DB_DW, "SELECT id_produk FROM dim_produk"))
    sumber = baca_sumber(master_produk)

    print("=" * 78)
    print("REKONSILIASI DATA TOKOMAJU: SEBELUM DAN SESUDAH ETL")
    print("=" * 78)
    print("\n-- SUMBER (data/penjualan.csv)")
    print("baris sumber                 : %d" % sumber["baris_sumber"])
    print("baris transaksi unik         : %d" % sumber["baris_unik"])
    print("baris duplikat dibuang       : %d" % sumber["duplikat"])
    print("total penjualan semua baris : %d" % sumber["total_mentah"])
    print("total penjualan baris unik  : %d" % sumber["total_unik"])
    print("kontribusi baris duplikat    : %d" % (sumber["total_mentah"] - sumber["total_unik"]))
    print("klasifikasi baris unik  :")
    for label, jml in sorted(sumber["alasan"].items(), key=lambda x: -x[1]):
        print("   %-38s %d" % (label, jml))

    print("\n-- DATA WAREHOUSE (tokomaju_dw)")
    for baris in psql(
        DB_DW,
        "SELECT 'dim_waktu', COUNT(*) FROM dim_waktu UNION ALL SELECT 'dim_produk', COUNT(*) FROM dim_produk "
        "UNION ALL SELECT 'dim_pelanggan', COUNT(*) FROM dim_pelanggan UNION ALL SELECT 'fact_penjualan', COUNT(*) FROM fact_penjualan ORDER BY 1",
    ):
        print("%-28s %s" % tuple(baris.split("|")))

    ringkas = psql(
        DB_DW,
        "SELECT COUNT(*), COUNT(DISTINCT id_transaksi), SUM(qty), SUM(total_penjualan), MIN(tanggal), MAX(tanggal) FROM fact_penjualan",
    )[0].split("|")
    print("\nfakta                    : %s" % ringkas[0])
    print("transaksi unik di fakta  : %s" % ringkas[1])
    print("total unit terjual       : %s" % ringkas[2])
    print("total penjualan          : %s" % ringkas[3])
    print("rentang tanggal          : %s s.d. %s" % (ringkas[4], ringkas[5]))

    cek = psql(
        DB_DW,
        "SELECT (SELECT COUNT(*) FROM fact_penjualan f LEFT JOIN dim_waktu d ON d.date_sk=f.date_sk WHERE d.date_sk IS NULL), "
        "(SELECT COUNT(*) FROM fact_penjualan f LEFT JOIN dim_produk d ON d.product_sk=f.product_sk WHERE d.product_sk IS NULL), "
        "(SELECT COUNT(*) FROM fact_penjualan f LEFT JOIN dim_pelanggan d ON d.customer_sk=f.customer_sk WHERE d.customer_sk IS NULL), "
        "(SELECT COUNT(*) FROM (SELECT id_transaksi FROM fact_penjualan GROUP BY id_transaksi HAVING COUNT(*)>1) x), "
        "(SELECT COUNT(*) FROM fact_penjualan WHERE total_penjualan <> qty * harga_satuan), "
        "(SELECT COUNT(*) FROM fact_penjualan WHERE date_sk IS NULL OR product_sk IS NULL OR customer_sk IS NULL)",
    )[0].split("|")
    print("\n-- INTEGRITAS REFERENSIAL")
    print("fakta tanpa dimensi waktu    : %s" % cek[0])
    print("fakta tanpa dimensi produk   : %s" % cek[1])
    print("fakta tanpa dimensi pelanggan: %s" % cek[2])
    print("id transaksi kembar di fakta : %s" % cek[3])
    print("total tidak sama qty x harga : %s" % cek[4])
    print("surrogate key bernilai kosong : %s" % cek[5])

    print("\n-- MD5 BERKAS KELUARAN")
    for nama in ("transaksi_bersih.csv", "transaksi_ditolak.csv", "transaksi_produk_tidak_dikenal.csv"):
        jalan = os.path.join(ROOT, "out", nama)
        if os.path.exists(jalan):
            with open(jalan, "rb") as f:
                sidik = hashlib.md5(f.read()).hexdigest()
            print("%-36s %s" % (nama, sidik))

    print("\n-- HASIL ANALISIS: TOTAL PENJUALAN PER KATEGORI PER BULAN (10 TERATAS)")
    query = (
        "SELECT d.kategori, w.tahun, w.bulan, SUM(f.total_penjualan) "
        "FROM fact_penjualan f "
        "JOIN dim_produk d ON d.product_sk = f.product_sk "
        "JOIN dim_waktu w ON w.date_sk = f.date_sk "
        "GROUP BY d.kategori, w.tahun, w.bulan "
        "ORDER BY SUM(f.total_penjualan) DESC LIMIT 10"
    )
    print("kategori | tahun | bulan | total_penjualan")
    for baris in psql(DB_DW, query):
        bagian = baris.split("|")
        print("%-26s %5s %5s %15s" % (bagian[0], bagian[1], bagian[2], bagian[3]))

    print("\n-- HASIL: TOTAL PENJUALAN PER KATEGORI PER TAHUN")
    query = (
        "SELECT d.kategori, w.tahun, SUM(f.total_penjualan), SUM(f.qty) "
        "FROM fact_penjualan f "
        "JOIN dim_produk d ON d.product_sk = f.product_sk "
        "JOIN dim_waktu w ON w.date_sk = f.date_sk "
        "GROUP BY d.kategori, w.tahun ORDER BY w.tahun, d.kategori"
    )
    print("kategori | tahun | total_penjualan | unit")
    for baris in psql(DB_DW, query):
        bagian = baris.split("|")
        print("%-26s %5s %15s %8s" % (bagian[0], bagian[1], bagian[2], bagian[3]))

    lolos = sumber["alasan"].get("VALID", 0)
    ditolak = sumber["baris_unik"] - lolos
    karantina = sumber["karantina"]
    fakta = int(ringkas[0])
    print("\n-- SELISIH")
    print(
        "baris unik sumber %d dikurangi %d baris ditolak = %d baris lolos cleansing"
        % (sumber["baris_unik"], ditolak, lolos)
    )
    print(
        "%d baris lolos cleansing dikurangi %d baris karantina = %d baris fakta"
        % (lolos, karantina, lolos - karantina)
    )
    print(
        "total penjualan data mentah %d, total penjualan baris unik %d, total penjualan data warehouse %d"
        % (sumber["total_mentah"], sumber["total_unik"], int(ringkas[3]))
    )
    print(
        "selisih data mentah ke data warehouse %d, selisih baris unik ke data warehouse %d"
        % (
            sumber["total_mentah"] - int(ringkas[3]),
            sumber["total_unik"] - int(ringkas[3]),
        )
    )

    print("\nRINGKASAN KATEGORI DI DATA WAREHOUSE:")
    for baris in psql(
        DB_DW,
        "SELECT kategori, COUNT(*) FROM dim_produk GROUP BY kategori ORDER BY kategori",
    ):
        bagian = baris.split("|")
        print("   %-26s %s produk" % (bagian[0], bagian[1]))

    masalah = []
    if fakta != lolos - karantina:
        masalah.append(
            "jumlah fakta %d tidak sama dengan %d baris yang seharusnya lolos"
            % (fakta, lolos - karantina)
        )
    if int(ringkas[3]) != sumber["total_valid"]:
        masalah.append(
            "total penjualan %s tidak sama dengan %d hasil perhitungan ulang"
            % (ringkas[3], sumber["total_valid"])
        )
    if int(ringkas[1]) != fakta:
        masalah.append("ada id transaksi kembar di tabel fakta")
    for nama, nilai in zip(["waktu", "produk", "pelanggan"], cek[0:3]):
        if int(nilai) != 0:
            masalah.append(
                "ada fakta tanpa pasangan dimensi %s (%s baris)" % (nama, nilai)
            )
    if int(cek[3]) != 0:
        masalah.append("ada id transaksi kembar di tabel fakta")
    if int(cek[4]) != 0:
        masalah.append(
            "ada baris fakta dengan total_penjualan berbeda dari qty x harga_satuan"
        )

    print("\n-- HASIL PEMERIKSAAN")
    if masalah:
        for m in masalah:
            print("GAGAL:", m)
        sys.exit(1)
    print(
        "LULUS: jumlah baris, total penjualan, dan integritas referensial sesuai hasil perhitungan ulang"
    )


if __name__ == "__main__":
    main()
