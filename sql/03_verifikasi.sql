-- Verifikasi dan analisis data warehouse TokoMaju
-- Jalankan: psql -d tokomaju_dw -f sql/03_verifikasi.sql

-- ===================== VERIFIKASI =====================

-- 1. SEBELUM: staging (sudah tanpa duplikat), semua baris
SELECT COUNT(*) AS baris,
       SUM(qty::int * regexp_replace(harga_satuan, '[^0-9]', '', 'g')::bigint) AS total
FROM stg_penjualan;

-- 2. SEBELUM: staging, hanya qty > 0 (baseline yang seharusnya masuk fakta)
SELECT COUNT(*) AS baris,
       SUM(qty::int * regexp_replace(harga_satuan, '[^0-9]', '', 'g')::bigint) AS total
FROM stg_penjualan
WHERE qty::int > 0;

-- 3. SESUDAH: tabel fakta
SELECT COUNT(*) AS baris, SUM(qty) AS qty, SUM(total_penjualan) AS total
FROM fakta_penjualan;

-- 4. Jumlah baris setiap dimensi
SELECT 'dim_waktu' AS tabel, COUNT(*) FROM dim_waktu
UNION ALL SELECT 'dim_produk', COUNT(*) FROM dim_produk
UNION ALL SELECT 'dim_pelanggan', COUNT(*) FROM dim_pelanggan
UNION ALL SELECT 'dim_metode_bayar', COUNT(*) FROM dim_metode_bayar;

-- 5. Transaksi yang masuk ke baris UNKNOWN (key 0)
SELECT COUNT(*) FILTER (WHERE produk_key = 0)       AS produk_unknown,
       COUNT(*) FILTER (WHERE pelanggan_key = 0)    AS pelanggan_unknown,
       COUNT(*) FILTER (WHERE metode_bayar_key = 0) AS metode_unknown
FROM fakta_penjualan;

-- 6. Rekonsiliasi total: selisih harus 0
SELECT
  (SELECT SUM(qty::int * regexp_replace(harga_satuan, '[^0-9]', '', 'g')::bigint)
     FROM stg_penjualan WHERE qty::int > 0)          AS total_seharusnya,
  (SELECT SUM(total_penjualan) FROM fakta_penjualan) AS total_fakta,
  (SELECT SUM(qty::int * regexp_replace(harga_satuan, '[^0-9]', '', 'g')::bigint)
     FROM stg_penjualan WHERE qty::int > 0)
  - (SELECT SUM(total_penjualan) FROM fakta_penjualan) AS selisih;

-- 7. Rincian baris yang dibuang (qty <= 0)
SELECT qty::int AS qty, COUNT(*) AS jumlah
FROM stg_penjualan
WHERE qty::int <= 0
GROUP BY qty::int
ORDER BY qty;

-- 8. Tidak ada key yang tidak tersambung ke dimensi (harus 0 semua)
SELECT
  COUNT(*) FILTER (WHERE w.waktu_key IS NULL)        AS waktu_yatim,
  COUNT(*) FILTER (WHERE p.produk_key IS NULL)       AS produk_yatim,
  COUNT(*) FILTER (WHERE c.pelanggan_key IS NULL)    AS pelanggan_yatim,
  COUNT(*) FILTER (WHERE m.metode_bayar_key IS NULL) AS metode_yatim
FROM fakta_penjualan f
LEFT JOIN dim_waktu        w ON w.waktu_key        = f.waktu_key
LEFT JOIN dim_produk       p ON p.produk_key       = f.produk_key
LEFT JOIN dim_pelanggan    c ON c.pelanggan_key    = f.pelanggan_key
LEFT JOIN dim_metode_bayar m ON m.metode_bayar_key = f.metode_bayar_key;

-- 9. Spot check satu transaksi (T00009: 21/06/2025, P016, C0076, qty 1, Rp85.000, QRIS)
SELECT f.id_transaksi, w.tanggal, p.id_produk, c.id_pelanggan, m.metode_bayar,
       f.qty, f.harga_satuan, f.total_penjualan
FROM fakta_penjualan f
JOIN dim_waktu        w ON w.waktu_key        = f.waktu_key
JOIN dim_produk       p ON p.produk_key       = f.produk_key
JOIN dim_pelanggan    c ON c.pelanggan_key    = f.pelanggan_key
JOIN dim_metode_bayar m ON m.metode_bayar_key = f.metode_bayar_key
WHERE f.id_transaksi = 'T00009';

-- ===================== ANALISIS =====================

-- A1. Total penjualan per kategori per bulan
SELECT w.bulan, w.nama_bulan, p.kategori, SUM(f.total_penjualan) AS total
FROM fakta_penjualan f
JOIN dim_waktu  w ON w.waktu_key  = f.waktu_key
JOIN dim_produk p ON p.produk_key = f.produk_key
GROUP BY w.bulan, w.nama_bulan, p.kategori
ORDER BY w.bulan, total DESC;

-- A2. Komposisi penjualan per metode pembayaran
SELECT m.metode_bayar,
       COUNT(*)                      AS jumlah_transaksi,
       SUM(f.total_penjualan)        AS total_penjualan,
       ROUND(AVG(f.total_penjualan)) AS rata_rata_per_transaksi,
       ROUND(100.0 * SUM(f.total_penjualan)
             / SUM(SUM(f.total_penjualan)) OVER (), 2) AS persen_total
FROM fakta_penjualan f
JOIN dim_metode_bayar m ON m.metode_bayar_key = f.metode_bayar_key
GROUP BY m.metode_bayar
ORDER BY total_penjualan DESC;

-- A3. Penjualan per kota pelanggan
SELECT c.kota,
       COUNT(DISTINCT f.pelanggan_key) AS jumlah_pelanggan,
       COUNT(*)                        AS jumlah_transaksi,
       SUM(f.total_penjualan)          AS total_penjualan,
       ROUND(AVG(f.total_penjualan))   AS rata_rata_per_transaksi
FROM fakta_penjualan f
JOIN dim_pelanggan c ON c.pelanggan_key = f.pelanggan_key
GROUP BY c.kota
ORDER BY total_penjualan DESC;