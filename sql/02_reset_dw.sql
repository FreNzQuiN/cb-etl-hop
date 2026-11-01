TRUNCATE fakta_penjualan, dim_waktu, dim_produk, dim_pelanggan RESTART IDENTITY;
INSERT INTO dim_produk (produk_key, id_produk, nama_produk, kategori, merek)
VALUES (0, 'UNKNOWN', 'Tidak Diketahui', 'Tidak Diketahui', 'Tidak Diketahui');
INSERT INTO dim_pelanggan (pelanggan_key, id_pelanggan, nama, jenis_kelamin, kota, provinsi, telepon)
VALUES (0, 'UNKNOWN', 'Tidak Diketahui', NULL, 'Tidak Diketahui', 'Tidak Diketahui', NULL);