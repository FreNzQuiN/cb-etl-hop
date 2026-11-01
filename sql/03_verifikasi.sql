-- 1. SEBELUM: staging (sudah tanpa duplikat), semua baris
SELECT COUNT(*) AS baris,
       SUM(qty::int * regexp_replace(harga_satuan, '[^0-9]', '', 'g')::bigint) AS total
FROM stg_penjualan;

-- 2. SEBELUM: staging, hanya qty > 0
SELECT COUNT(*) AS baris,
       SUM(qty::int * regexp_replace(harga_satuan, '[^0-9]', '', 'g')::bigint) AS total
FROM stg_penjualan
WHERE qty::int > 0;

-- 3. SESUDAH: tabel fakta
SELECT COUNT(*) AS baris, SUM(qty) AS qty, SUM(total_penjualan) AS total
FROM fakta_penjualan;

-- 4. Jumlah baris dimensi
SELECT 'dim_waktu' AS tabel, COUNT(*) FROM dim_waktu
UNION ALL SELECT 'dim_produk', COUNT(*) FROM dim_produk
UNION ALL SELECT 'dim_pelanggan', COUNT(*) FROM dim_pelanggan;

-- 5. Transaksi yang masuk ke unknown member
SELECT COUNT(*) FILTER (WHERE produk_key = 0)    AS produk_unknown,
       COUNT(*) FILTER (WHERE pelanggan_key = 0) AS pelanggan_unknown
FROM fakta_penjualan;

-- 6. Analisis: total penjualan per kategori per bulan
SELECT w.bulan, w.nama_bulan, p.kategori, SUM(f.total_penjualan) AS total
FROM fakta_penjualan f
JOIN dim_waktu  w ON w.waktu_key  = f.waktu_key
JOIN dim_produk p ON p.produk_key = f.produk_key
GROUP BY w.bulan, w.nama_bulan, p.kategori
ORDER BY w.bulan, total DESC;