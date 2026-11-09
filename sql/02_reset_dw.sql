TRUNCATE fakta_penjualan, dim_waktu, dim_produk, dim_pelanggan, dim_metode_bayar RESTART IDENTITY;

INSERT INTO dim_produk (produk_key, id_produk, nama_produk, kategori, merek)
VALUES (0, 'UNKNOWN', 'Tidak Diketahui', 'Tidak Diketahui', 'Tidak Diketahui');

INSERT INTO dim_pelanggan (pelanggan_key, id_pelanggan, nama, jenis_kelamin, kota, provinsi)
VALUES (0, 'UNKNOWN', 'Tidak Diketahui', NULL, 'Tidak Diketahui', 'Tidak Diketahui');

INSERT INTO dim_metode_bayar (metode_bayar_key, metode_bayar)
VALUES (0, 'UNKNOWN');