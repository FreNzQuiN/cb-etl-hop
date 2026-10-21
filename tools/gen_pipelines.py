import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gen_pipelines_lib import (
    csv_field,
    date_field,
    out_field,
    pipeline,
    script_transform,
    sel_field,
    text_field,
    tulis,
)
from gen_pipelines_parts import (
    csv_input,
    database_lookup,
    dummy,
    excel_input,
    filter_rows,
    select_values,
    table_input,
    table_output,
    text_output,
    unique_hashset,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WF_DIR = os.path.join(ROOT, "workflows")

SCRIPT_P1 = [
    r"var BULAN = {jan:1,feb:2,mar:3,apr:4,mei:5,jun:6,jul:7,agu:8,sep:9,okt:10,nov:11,des:12};",
    r'var rawId = id_transaksi === null || id_transaksi === undefined ? "" : String(id_transaksi).trim();',
    r'var rawTgl = tanggal === null || tanggal === undefined ? "" : String(tanggal).trim();',
    r'var rawProd = id_produk === null || id_produk === undefined ? "" : String(id_produk).trim();',
    r'var rawPel = id_pelanggan === null || id_pelanggan === undefined ? "" : String(id_pelanggan).trim();',
    r'var rawQty = qty === null || qty === undefined ? "" : String(qty).trim();',
    r'var rawHrg = harga_satuan === null || harga_satuan === undefined ? "" : String(harga_satuan).trim();',
    r'var rawBayar = metode_bayar === null || metode_bayar === undefined ? "" : String(metode_bayar).trim();',
    r"var parseTgl = function (s) {",
    r"  var m = /^(\d{4})-(\d{1,2})-(\d{1,2})$/.exec(s);",
    r"  if (m !== null) { return [parseInt(m[1], 10), parseInt(m[2], 10), parseInt(m[3], 10)]; }",
    r"  m = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/.exec(s);",
    r"  if (m !== null) { return [parseInt(m[3], 10), parseInt(m[2], 10), parseInt(m[1], 10)]; }",
    r"  m = /^(\d{1,2})-(\d{1,2})-(\d{4})$/.exec(s);",
    r"  if (m !== null) { return [parseInt(m[3], 10), parseInt(m[2], 10), parseInt(m[1], 10)]; }",
    r"  m = /^(\d{1,2})\s+([A-Za-z]{3,9})\s+(\d{4})$/.exec(s);",
    r"  if (m !== null) {",
    r"    var kunci = m[2].toLowerCase().substring(0, 3);",
    r"    if (BULAN[kunci] !== undefined) { return [parseInt(m[3], 10), BULAN[kunci], parseInt(m[1], 10)]; }",
    r"  }",
    r"  return null;",
    r"};",
    r"var parts = parseTgl(rawTgl);",
    r"var thn = 0;",
    r"var bln = 0;",
    r"var hr = 0;",
    r"var tglOk = false;",
    r"if (parts !== null) {",
    r"  thn = parts[0];",
    r"  bln = parts[1];",
    r"  hr = parts[2];",
    r"  var cek = new Date(Date.UTC(thn, bln - 1, hr));",
    r"  if (cek.getUTCFullYear() === thn && cek.getUTCMonth() + 1 === bln && cek.getUTCDate() === hr) { tglOk = true; }",
    r"}",
    r'var pad = function (x) { return x < 10 ? "0" + x : "" + x; };',
    r'tanggalISO = tglOk ? (thn + "-" + pad(bln) + "-" + pad(hr)) : "";',
    r"var toInt = function (s) {",
    r"  if (s === null || s === undefined) { return null; }",
    r"  var teks = String(s).trim();",
    r'  if (teks === "") { return null; }',
    r'  teks = teks.replace(/^Rp\.?/i, "");',
    r'  teks = teks.replace(/\s/g, "");',
    r'  if (/^\d{1,3}(\.\d{3})+$/.test(teks)) { teks = teks.replace(/\./g, ""); }',
    r"  if (/^-?\d+$/.test(teks)) { return parseInt(teks, 10); }",
    r"  return null;",
    r"};",
    r"var nQty = toInt(rawQty);",
    r"var nHrg = toInt(rawHrg);",
    r'alasan = "";',
    r'if (rawId === "") { alasan = "id transaksi kosong"; }',
    r'if (alasan === "" && !tglOk) { alasan = "tanggal tidak valid"; }',
    r'if (alasan === "" && nQty === null) { alasan = "jumlah terjual tidak valid"; }',
    r'if (alasan === "" && nQty < 0) { alasan = "jumlah terjual negatif"; }',
    r'if (alasan === "" && nQty === 0) { alasan = "jumlah terjual nol"; }',
    r'if (alasan === "" && nHrg === null) { alasan = "harga satuan tidak valid"; }',
    r'if (alasan === "" && nHrg <= 0) { alasan = "harga satuan tidak valid"; }',
    r'if (alasan === "" && rawProd === "") { alasan = "id produk kosong"; }',
    r'if (alasan === "" && rawPel === "") { alasan = "id pelanggan kosong"; }',
    r'if (alasan === "" && rawBayar === "") { alasan = "metode bayar kosong"; }',
    r"qtyInt = nQty === null ? 0 : nQty;",
    r"hargaInt = nHrg === null ? 0 : nHrg;",
    r'totalPenjualan = alasan === "" ? nQty * nHrg : 0;',
    r'valid = alasan === "" ? 1 : 0;',
]

SCRIPT_P2 = [
    r"var rapikan = function (s) {",
    r'  if (s === null || s === undefined) { return ""; }',
    r'  return String(s).replace(/\s+/g, " ").trim();',
    r"};",
    r"var judul = function (s) {",
    r"  var t = rapikan(s).toLowerCase();",
    r"  return t.replace(/(^|\s)([a-z])/g, function (seluruh, spasi, huruf) { return spasi + huruf.toUpperCase(); });",
    r"};",
    r"idProduk = rapikan(id_produk);",
    r"namaProduk = rapikan(nama_produk);",
    r"var kat = judul(kategori);",
    r'kat = kat.replace(/\bDan\b/g, "&");',
    r'if (kat === "Mamin") { kat = "Makanan & Minuman"; }',
    r'if (kat === "") { kat = "Tidak Diketahui"; }',
    r"kategoriNorm = kat;",
    r"merekNorm = rapikan(merek);",
]

SCRIPT_P3 = [
    r"var rapikan = function (s) {",
    r'  if (s === null || s === undefined) { return ""; }',
    r'  return String(s).replace(/\s+/g, " ").trim();',
    r"};",
    r'var kosong = function (s) { return s === null || s === undefined || String(s).trim() === ""; };',
    r"namaBersih = rapikan(nama);",
    r'kotaNorm = kosong(kota) ? "Tidak Diketahui" : rapikan(kota);',
    r'provinsiNorm = kosong(provinsi) ? "" : rapikan(provinsi);',
    r'jenisNorm = kosong(jenis_kelamin) ? "" : rapikan(jenis_kelamin);',
    r'var tel = kosong(telepon) ? "" : String(telepon).replace(/[^0-9]/g, "");',
    r'if (tel.indexOf("62") === 0) {',
    r'  tel = "0" + tel.substring(2);',
    r'} else if (tel !== "" && tel.indexOf("0") !== 0) {',
    r'  tel = "0" + tel;',
    r"}",
    r"teleponNorm = tel;",
]

SCRIPT_P4 = [
    r'var NAMA_BULAN = ["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"];',
    r'var NAMA_HARI = ["Minggu","Senin","Selasa","Rabu","Kamis","Jumat","Sabtu"];',
    r"var thn = 0;",
    r"var bln = 0;",
    r"var hr = 0;",
    r"if (tanggal !== null && tanggal !== undefined) {",
    r'  if (typeof tanggal.getFullYear === "function") {',
    r"    thn = tanggal.getFullYear();",
    r"    bln = tanggal.getMonth() + 1;",
    r"    hr = tanggal.getDate();",
    r'  } else if (typeof tanggal.getYear === "function") {',
    r"    thn = tanggal.getYear() + 1900;",
    r"    bln = tanggal.getMonth() + 1;",
    r"    hr = tanggal.getDate();",
    r"  } else {",
    r"    var m = /^(\d{4})-(\d{1,2})-(\d{1,2})$/.exec(String(tanggal).trim());",
    r"    if (m !== null) {",
    r"      thn = parseInt(m[1], 10);",
    r"      bln = parseInt(m[2], 10);",
    r"      hr = parseInt(m[3], 10);",
    r"    }",
    r"  }",
    r"}",
    r"hari = hr;",
    r"bulan = bln;",
    r"kuartal = Math.ceil(bln / 3);",
    r"tahun = thn;",
    r"namaBulan = NAMA_BULAN[bln - 1];",
    r"namaHari = NAMA_HARI[new Date(Date.UTC(thn, bln - 1, hr)).getUTCDay()];",
]

SCRIPT_P5 = [
    r'alasan = "produk tidak ditemukan di master produk";',
]


def gabung(baris):
    return "\n".join(baris)


def p1():
    field_sumber = [
        csv_field("id_transaksi"),
        csv_field("tanggal"),
        csv_field("id_produk"),
        csv_field("id_pelanggan"),
        csv_field("qty"),
        csv_field("harga_satuan"),
        csv_field("metode_bayar"),
    ]
    transforms = [
        csv_input(
            "Transaksi CSV",
            "${PROJECT_HOME}/data/penjualan.csv",
            ";",
            field_sumber,
            100,
            100,
            "Sumber transaksi penjualan format CSV pemisah titik koma",
        ),
        unique_hashset(
            "Buang Duplikat",
            ["id_transaksi"],
            260,
            100,
            "Buang transaksi kembar berdasarkan id_transaksi",
        ),
        script_transform(
            "Normalisasi",
            "javascript",
            gabung(SCRIPT_P1),
            [
                out_field("tanggalISO"),
                out_field("qtyInt", "Integer"),
                out_field("hargaInt", "Integer"),
                out_field("totalPenjualan", "Integer"),
                out_field("alasan"),
                out_field("valid", "Integer"),
            ],
            420,
            100,
            "Seragamkan tanggal dan harga, hitung total, beri alasan penolakan",
        ),
        filter_rows(
            "Cek Validitas",
            "valid",
            "=",
            "1",
            "Integer",
            "Siap Muat",
            "Ditolak",
            580,
            100,
            "Pisahkan baris sah dan baris bermasalah",
        ),
        dummy("Siap Muat", 740, 60),
        dummy("Ditolak", 740, 160),
        select_values(
            "Pilih Bersih",
            [
                sel_field("id_transaksi", "id_transaksi"),
                sel_field("tanggalISO", "tanggal"),
                sel_field("id_produk", "id_produk"),
                sel_field("id_pelanggan", "id_pelanggan"),
                sel_field("qtyInt", "qty"),
                sel_field("hargaInt", "harga_satuan"),
                sel_field("totalPenjualan", "total_penjualan"),
                sel_field("metode_bayar", "metode_bayar"),
            ],
            900,
            60,
        ),
        text_output(
            "Berkas Bersih",
            "${PROJECT_HOME}/out/transaksi_bersih",
            [
                text_field(n)
                for n in [
                    "id_transaksi",
                    "tanggal",
                    "id_produk",
                    "id_pelanggan",
                    "qty",
                    "harga_satuan",
                    "total_penjualan",
                    "metode_bayar",
                ]
            ],
            1060,
            60,
            "Berkas CSV transaksi yang lolos validasi",
        ),
        select_values(
            "Pilih Ditolak",
            [
                sel_field("id_transaksi", "id_transaksi"),
                sel_field("tanggal", "tanggal"),
                sel_field("id_produk", "id_produk"),
                sel_field("id_pelanggan", "id_pelanggan"),
                sel_field("qty", "qty"),
                sel_field("harga_satuan", "harga_satuan"),
                sel_field("metode_bayar", "metode_bayar"),
                sel_field("alasan", "alasan"),
            ],
            900,
            160,
            "Bawa nilai mentah sumber untuk penelusuran",
        ),
        text_output(
            "Berkas Ditolak",
            "${PROJECT_HOME}/out/transaksi_ditolak",
            [
                text_field(n)
                for n in [
                    "id_transaksi",
                    "tanggal",
                    "id_produk",
                    "id_pelanggan",
                    "qty",
                    "harga_satuan",
                    "metode_bayar",
                    "alasan",
                ]
            ],
            1060,
            160,
            "Berkas CSV transaksi yang ditolak beserta alasannya",
        ),
    ]
    hops = [
        ("Transaksi CSV", "Buang Duplikat"),
        ("Buang Duplikat", "Normalisasi"),
        ("Normalisasi", "Cek Validitas"),
        ("Cek Validitas", "Siap Muat"),
        ("Cek Validitas", "Ditolak"),
        ("Siap Muat", "Pilih Bersih"),
        ("Pilih Bersih", "Berkas Bersih"),
        ("Ditolak", "Pilih Ditolak"),
        ("Pilih Ditolak", "Berkas Ditolak"),
    ]
    return pipeline(
        "P1_cleansing",
        "Ekstrak, bersihkan, dan validasi transaksi penjualan TokoMaju",
        hops,
        transforms,
    )


def p2():
    transforms = [
        excel_input(
            "Master Produk",
            "${PROJECT_HOME}/data/produk.xlsx",
            "Produk",
            [csv_field(n) for n in ["id_produk", "nama_produk", "kategori", "merek"]],
            100,
            100,
            "Sumber master produk dan kategori format Excel",
        ),
        unique_hashset(
            "Buang Duplikat Produk",
            ["id_produk"],
            260,
            100,
            "Buang baris produk kembar pada master",
        ),
        script_transform(
            "Normalisasi Kategori",
            "javascript",
            gabung(SCRIPT_P2),
            [
                out_field("idProduk"),
                out_field("namaProduk"),
                out_field("kategoriNorm"),
                out_field("merekNorm"),
            ],
            420,
            100,
            "Rapikan nama produk dan seragamkan nama kategori",
        ),
        select_values(
            "Pilih Master Produk",
            [
                sel_field("idProduk", "id_produk"),
                sel_field("namaProduk", "nama_produk"),
                sel_field("kategoriNorm", "kategori"),
                sel_field("merekNorm", "merek"),
            ],
            580,
            100,
        ),
        table_output(
            "Muat Dim Produk",
            "tokomaju_dw",
            "dim_produk",
            740,
            100,
            "Muat dimensi produk ke PostgreSQL",
        ),
    ]
    hops = [
        ("Master Produk", "Buang Duplikat Produk"),
        ("Buang Duplikat Produk", "Normalisasi Kategori"),
        ("Normalisasi Kategori", "Pilih Master Produk"),
        ("Pilih Master Produk", "Muat Dim Produk"),
    ]
    return pipeline(
        "P2_dim_produk",
        "Muat dimensi produk dengan kategori yang sudah seragam",
        hops,
        transforms,
    )


def p3():
    transforms = [
        table_input(
            "Tabel Pelanggan",
            "tokomaju_oltp",
            "SELECT id_pelanggan, nama, jenis_kelamin, kota, provinsi, telepon, email, tgl_daftar FROM pelanggan",
            100,
            100,
            "Sumber master pelanggan dari database OLTP TokoMaju",
        ),
        script_transform(
            "Normalisasi Pelanggan",
            "javascript",
            gabung(SCRIPT_P3),
            [
                out_field("namaBersih"),
                out_field("jenisNorm"),
                out_field("kotaNorm"),
                out_field("provinsiNorm"),
                out_field("teleponNorm"),
            ],
            260,
            100,
            "Isi kota kosong, rapikan nama, seragamkan nomor telepon",
        ),
        select_values(
            "Pilih Master Pelanggan",
            [
                sel_field("id_pelanggan", "id_pelanggan"),
                sel_field("namaBersih", "nama"),
                sel_field("jenisNorm", "jenis_kelamin"),
                sel_field("kotaNorm", "kota"),
                sel_field("provinsiNorm", "provinsi"),
                sel_field("teleponNorm", "telepon"),
            ],
            420,
            100,
        ),
        table_output(
            "Muat Dim Pelanggan",
            "tokomaju_dw",
            "dim_pelanggan",
            580,
            100,
            "Muat dimensi pelanggan ke PostgreSQL",
        ),
    ]
    hops = [
        ("Tabel Pelanggan", "Normalisasi Pelanggan"),
        ("Normalisasi Pelanggan", "Pilih Master Pelanggan"),
        ("Pilih Master Pelanggan", "Muat Dim Pelanggan"),
    ]
    return pipeline(
        "P3_dim_pelanggan",
        "Muat dimensi pelanggan dari database OLTP",
        hops,
        transforms,
    )


def bidang_transaksi_bersih():
    return [
        csv_field("id_transaksi"),
        csv_field("tanggal", "Date", "yyyy-MM-dd"),
        csv_field("id_produk"),
        csv_field("id_pelanggan"),
        csv_field("qty", "Integer"),
        csv_field("harga_satuan", "Integer"),
        csv_field("total_penjualan", "Integer"),
        csv_field("metode_bayar"),
    ]


def p4():
    transforms = [
        csv_input(
            "Transaksi Bersih",
            "${PROJECT_HOME}/out/transaksi_bersih.csv",
            ",",
            bidang_transaksi_bersih(),
            100,
            100,
            "Sumber transaksi hasil cleansing P1",
        ),
        script_transform(
            "Atribut Waktu",
            "javascript",
            gabung(SCRIPT_P4),
            [
                out_field("hari", "Integer"),
                out_field("namaHari"),
                out_field("bulan", "Integer"),
                out_field("namaBulan"),
                out_field("kuartal", "Integer"),
                out_field("tahun", "Integer"),
            ],
            260,
            100,
            "Turunkan atribut kalender dari tanggal transaksi",
        ),
        unique_hashset(
            "Unik Tanggal", ["tanggal"], 420, 100, "Ambil satu baris per tanggal"
        ),
        select_values(
            "Pilih Dimensi Waktu",
            [
                sel_field("tanggal", "tanggal"),
                sel_field("hari", "hari"),
                sel_field("namaHari", "nama_hari"),
                sel_field("bulan", "bulan"),
                sel_field("namaBulan", "nama_bulan"),
                sel_field("kuartal", "kuartal"),
                sel_field("tahun", "tahun"),
            ],
            580,
            100,
        ),
        table_output(
            "Muat Dim Waktu",
            "tokomaju_dw",
            "dim_waktu",
            740,
            100,
            "Muat dimensi waktu ke PostgreSQL",
        ),
    ]
    hops = [
        ("Transaksi Bersih", "Atribut Waktu"),
        ("Atribut Waktu", "Unik Tanggal"),
        ("Unik Tanggal", "Pilih Dimensi Waktu"),
        ("Pilih Dimensi Waktu", "Muat Dim Waktu"),
    ]
    return pipeline(
        "P4_dim_waktu",
        "Bangun dimensi waktu dari transaksi yang lolos validasi",
        hops,
        transforms,
    )


def p5():
    transforms = [
        csv_input(
            "Transaksi Bersih",
            "${PROJECT_HOME}/out/transaksi_bersih.csv",
            ",",
            bidang_transaksi_bersih(),
            100,
            100,
            "Sumber transaksi hasil cleansing P1",
        ),
        database_lookup(
            "Lookup Waktu",
            "tokomaju_dw",
            "dim_waktu",
            [("tanggal", "tanggal")],
            [("date_sk", "date_sk", "", "Integer")],
            260,
            100,
            "Ambil surrogate key dimensi waktu",
        ),
        database_lookup(
            "Lookup Pelanggan",
            "tokomaju_dw",
            "dim_pelanggan",
            [("id_pelanggan", "id_pelanggan")],
            [("customer_sk", "customer_sk", "", "Integer")],
            420,
            100,
            "Ambil surrogate key dimensi pelanggan",
        ),
        database_lookup(
            "Lookup Produk",
            "tokomaju_dw",
            "dim_produk",
            [("id_produk", "id_produk")],
            [("product_sk", "product_sk", "0", "Integer")],
            580,
            100,
            "Ambil surrogate key dimensi produk, 0 bila produk tidak ada di master",
        ),
        script_transform(
            "Catat Alasan",
            "javascript",
            gabung(SCRIPT_P5),
            [out_field("alasan")],
            740,
            100,
            "Tandai alasan saat produk tidak ditemukan di master",
        ),
        filter_rows(
            "Cek Produk Master",
            "product_sk",
            ">",
            "0",
            "Integer",
            "Siap Muat",
            "Produk Tidak Dikenal",
            900,
            100,
            "Pisahkan transaksi yang produknya ada di master",
        ),
        dummy("Siap Muat", 1060, 60),
        dummy("Produk Tidak Dikenal", 1060, 160),
        select_values(
            "Pilih Fakta",
            [
                sel_field("id_transaksi", "id_transaksi"),
                sel_field("tanggal", "tanggal"),
                sel_field("date_sk", "date_sk"),
                sel_field("id_produk", "id_produk"),
                sel_field("product_sk", "product_sk"),
                sel_field("id_pelanggan", "id_pelanggan"),
                sel_field("customer_sk", "customer_sk"),
                sel_field("qty", "qty"),
                sel_field("harga_satuan", "harga_satuan"),
                sel_field("total_penjualan", "total_penjualan"),
                sel_field("metode_bayar", "metode_bayar"),
            ],
            1220,
            60,
        ),
        table_output(
            "Muat Fakta",
            "tokomaju_dw",
            "fact_penjualan",
            1380,
            60,
            "Muat tabel fakta penjualan ke PostgreSQL",
        ),
        select_values(
            "Pilih Karantina",
            [
                sel_field("id_transaksi", "id_transaksi"),
                sel_field("tanggal", "tanggal"),
                sel_field("id_produk", "id_produk"),
                sel_field("id_pelanggan", "id_pelanggan"),
                sel_field("qty", "qty"),
                sel_field("harga_satuan", "harga_satuan"),
                sel_field("total_penjualan", "total_penjualan"),
                sel_field("metode_bayar", "metode_bayar"),
                sel_field("alasan", "alasan"),
            ],
            1220,
            160,
        ),
        text_output(
            "Berkas Karantina",
            "${PROJECT_HOME}/out/transaksi_produk_tidak_dikenal",
            [
                text_field("id_transaksi"),
                date_field("tanggal"),
                text_field("id_produk"),
                text_field("id_pelanggan"),
                text_field("qty"),
                text_field("harga_satuan"),
                text_field("total_penjualan"),
                text_field("metode_bayar"),
                text_field("alasan"),
            ],
            1380,
            160,
            "Berkas transaksi yang produknya tidak ada di master produk",
        ),
    ]
    hops = [
        ("Transaksi Bersih", "Lookup Waktu"),
        ("Lookup Waktu", "Lookup Pelanggan"),
        ("Lookup Pelanggan", "Lookup Produk"),
        ("Lookup Produk", "Catat Alasan"),
        ("Catat Alasan", "Cek Produk Master"),
        ("Cek Produk Master", "Siap Muat"),
        ("Cek Produk Master", "Produk Tidak Dikenal"),
        ("Siap Muat", "Pilih Fakta"),
        ("Pilih Fakta", "Muat Fakta"),
        ("Produk Tidak Dikenal", "Pilih Karantina"),
        ("Pilih Karantina", "Berkas Karantina"),
    ]
    return pipeline(
        "P5_fact_penjualan",
        "Muat tabel fakta penjualan dengan surrogate key dimensi",
        hops,
        transforms,
    )


def action_pipeline(nama, deskripsi, file_hpl, x, y):
    return [
        "    <action>",
        "      <name>%s</name>" % nama,
        "      <description>%s</description>" % deskripsi,
        "      <type>PIPELINE</type>",
        "      <attributes/>",
        "      <filename>%s</filename>" % file_hpl,
        "      <params_from_previous>N</params_from_previous>",
        "      <exec_per_row>N</exec_per_row>",
        "      <clear_rows>N</clear_rows>",
        "      <clear_files>N</clear_files>",
        "      <set_logfile>N</set_logfile>",
        "      <logfile/>",
        "      <logext/>",
        "      <add_date>N</add_date>",
        "      <add_time>N</add_time>",
        "      <loglevel>Basic</loglevel>",
        "      <set_append_logfile>N</set_append_logfile>",
        "      <wait_until_finished>Y</wait_until_finished>",
        "      <create_parent_folder>N</create_parent_folder>",
        "      <run_configuration>local</run_configuration>",
        "      <parameters>",
        "        <pass_all_parameters>Y</pass_all_parameters>",
        "      </parameters>",
        "      <parallel>N</parallel>",
        "      <xloc>%d</xloc>" % x,
        "      <yloc>%d</yloc>" % y,
        "      <attributes_hac/>",
        "    </action>",
    ]


def workflow():
    baris = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        "<workflow>",
        "  <name>ETL_Tokomaju</name>",
        "  <name_sync_with_filename>Y</name_sync_with_filename>",
        "  <description>Orkestrasi ETL data warehouse TokoMaju dengan Apache Hop</description>",
        "  <extended_description/>",
        "  <workflow_version/>",
        "  <created_user>-</created_user>",
        "  <created_date>2026/10/21 09:00:00.000</created_date>",
        "  <modified_user>-</modified_user>",
        "  <modified_date>2026/10/21 09:00:00.000</modified_date>",
        "  <parameters>",
        "    </parameters>",
        "  <actions>",
        "    <action>",
        "      <name>Start</name>",
        "      <description/>",
        "      <type>SPECIAL</type>",
        "      <attributes/>",
        "      <repeat>N</repeat>",
        "      <schedulerType>0</schedulerType>",
        "      <intervalSeconds>0</intervalSeconds>",
        "      <intervalMinutes>60</intervalMinutes>",
        "      <hour>12</hour>",
        "      <minutes>0</minutes>",
        "      <weekDay>1</weekDay>",
        "      <DayOfMonth>1</DayOfMonth>",
        "      <parallel>N</parallel>",
        "      <xloc>64</xloc>",
        "      <yloc>112</yloc>",
        "      <attributes_hac/>",
        "    </action>",
    ]
    pipeline_def = [
        ("P1_cleansing", "Ekstrak, bersihkan, dan validasi transaksi penjualan", 224),
        ("P2_dim_produk", "Muat dimensi produk", 544),
        ("P3_dim_pelanggan", "Muat dimensi pelanggan dari OLTP", 704),
        ("P4_dim_waktu", "Bangun dimensi waktu", 864),
        ("P5_fact_penjualan", "Muat tabel fakta penjualan", 1024),
    ]
    baris += action_pipeline(
        pipeline_def[0][0],
        pipeline_def[0][1],
        "${PROJECT_HOME}/pipelines/%s.hpl" % pipeline_def[0][0],
        pipeline_def[0][2],
        112,
    )
    baris += [
        "    <action>",
        "      <name>Kosongkan Data Warehouse</name>",
        "      <description>Kosongkan tabel fakta dan dimensi sebelum muat ulang</description>",
        "      <type>SQL</type>",
        "      <sql>TRUNCATE TABLE fact_penjualan, dim_waktu, dim_produk, dim_pelanggan RESTART IDENTITY</sql>",
        "      <connection>tokomaju_dw</connection>",
        "      <useVariableSubstitution>N</useVariableSubstitution>",
        "      <sqlfromfile>N</sqlfromfile>",
        "      <sendOneStatement>Y</sendOneStatement>",
        "      <attributes/>",
        "      <repeat>N</repeat>",
        "      <schedulerType>0</schedulerType>",
        "      <intervalSeconds>0</intervalSeconds>",
        "      <intervalMinutes>60</intervalMinutes>",
        "      <hour>12</hour>",
        "      <minutes>0</minutes>",
        "      <weekDay>1</weekDay>",
        "      <DayOfMonth>1</DayOfMonth>",
        "      <parallel>N</parallel>",
        "      <xloc>384</xloc>",
        "      <yloc>112</yloc>",
        "      <attributes_hac/>",
        "    </action>",
    ]
    for nama, deskripsi, x in pipeline_def[1:]:
        baris += action_pipeline(
            nama, deskripsi, "${PROJECT_HOME}/pipelines/%s.hpl" % nama, x, 112
        )
    baris += [
        "    <action>",
        "      <name>Sukses</name>",
        "      <description/>",
        "      <type>SUCCESS</type>",
        "      <attributes/>",
        "      <repeat>N</repeat>",
        "      <schedulerType>0</schedulerType>",
        "      <intervalSeconds>0</intervalSeconds>",
        "      <intervalMinutes>60</intervalMinutes>",
        "      <hour>12</hour>",
        "      <minutes>0</minutes>",
        "      <weekDay>1</weekDay>",
        "      <DayOfMonth>1</DayOfMonth>",
        "      <parallel>N</parallel>",
        "      <xloc>1184</xloc>",
        "      <yloc>112</yloc>",
        "      <attributes_hac/>",
        "    </action>",
        "  </actions>",
        "  <hops>",
    ]
    urutan = (
        ["Start", pipeline_def[0][0], "Kosongkan Data Warehouse"]
        + [p[0] for p in pipeline_def[1:]]
        + ["Sukses"]
    )

    for i in range(len(urutan) - 1):
        baris += [
            "    <hop>",
            "      <from>%s</from>" % urutan[i],
            "      <to>%s</to>" % urutan[i + 1],
            "      <enabled>Y</enabled>",
            "      <evaluation>Y</evaluation>",
            "      <unconditional>Y</unconditional>",
            "    </hop>",
        ]
    baris += [
        "  </hops>",
        "  <notepads>",
        "  </notepads>",
        "</workflow>",
        "",
    ]
    isi = "\n".join(baris)
    with io.open(
        os.path.join(WF_DIR, "ETL_Tokomaju.hwf"), "w", encoding="utf-8", newline="\n"
    ) as f:
        f.write(isi)
    print("WROTE ETL_Tokomaju.hwf")


def main():
    tulis("P1_cleansing.hpl", p1())
    tulis("P2_dim_produk.hpl", p2())
    tulis("P3_dim_pelanggan.hpl", p3())
    tulis("P4_dim_waktu.hpl", p4())
    tulis("P5_fact_penjualan.hpl", p5())
    workflow()


if __name__ == "__main__":
    main()
