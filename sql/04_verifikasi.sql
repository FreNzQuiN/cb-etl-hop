SELECT 'dim_waktu' AS tabel, COUNT(*) AS jumlah_baris FROM dim_waktu
UNION ALL SELECT 'dim_produk', COUNT(*) FROM dim_produk
UNION ALL SELECT 'dim_pelanggan', COUNT(*) FROM dim_pelanggan
UNION ALL SELECT 'fact_penjualan', COUNT(*) FROM fact_penjualan
ORDER BY tabel;

SELECT COUNT(*) AS jumlah_baris_fakta,
       COUNT(DISTINCT id_transaksi) AS jumlah_transaksi_unik,
       SUM(qty) AS total_unit_terjual,
       SUM(total_penjualan) AS total_penjualan,
       MIN(tanggal) AS tanggal_awal,
       MAX(tanggal) AS tanggal_akhir
FROM fact_penjualan;

SELECT COUNT(*) AS fakta_tanpa_dimensi_waktu
FROM fact_penjualan f
LEFT JOIN dim_waktu d ON d.date_sk = f.date_sk
WHERE d.date_sk IS NULL;

SELECT COUNT(*) AS fakta_tanpa_dimensi_produk
FROM fact_penjualan f
LEFT JOIN dim_produk d ON d.product_sk = f.product_sk
WHERE d.product_sk IS NULL;

SELECT COUNT(*) AS fakta_tanpa_dimensi_pelanggan
FROM fact_penjualan f
LEFT JOIN dim_pelanggan d ON d.customer_sk = f.customer_sk
WHERE d.customer_sk IS NULL;

SELECT COUNT(*) AS jumlah_kategori FROM (SELECT DISTINCT kategori FROM dim_produk) k;

SELECT d.kategori,
       w.nama_bulan,
       w.bulan,
       w.tahun,
       SUM(f.total_penjualan) AS total_penjualan,
       SUM(f.qty) AS unit_terjual
FROM fact_penjualan f
JOIN dim_produk d ON d.product_sk = f.product_sk
JOIN dim_waktu w ON w.date_sk = f.date_sk
GROUP BY d.kategori, w.nama_bulan, w.bulan, w.tahun
ORDER BY w.tahun, w.bulan, d.kategori;

SELECT COUNT(*) AS fakta_surrogate_key_kosong
FROM fact_penjualan
WHERE date_sk IS NULL OR product_sk IS NULL OR customer_sk IS NULL;
