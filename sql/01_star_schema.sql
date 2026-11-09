DROP TABLE IF EXISTS fakta_penjualan;
DROP TABLE IF EXISTS dim_metode_bayar;
DROP TABLE IF EXISTS dim_waktu;
DROP TABLE IF EXISTS dim_produk;
DROP TABLE IF EXISTS dim_pelanggan;

CREATE TABLE dim_waktu (
  waktu_key   INTEGER PRIMARY KEY,           -- format yyyymmdd, contoh 20250131
  tanggal     DATE NOT NULL UNIQUE,
  hari        VARCHAR(10),
  bulan       INTEGER,
  nama_bulan  VARCHAR(10),
  kuartal     INTEGER,
  tahun       INTEGER
);

CREATE TABLE dim_produk (
  produk_key   SERIAL PRIMARY KEY,           -- surrogate key
  id_produk    VARCHAR(10) NOT NULL UNIQUE,  -- natural key
  nama_produk  VARCHAR(100),
  kategori     VARCHAR(50),
  merek        VARCHAR(50)
);

CREATE TABLE dim_pelanggan (
  pelanggan_key  SERIAL PRIMARY KEY,         -- surrogate key
  id_pelanggan   VARCHAR(10) NOT NULL UNIQUE,-- natural key
  nama           VARCHAR(100),
  jenis_kelamin  CHAR(1),
  kota           VARCHAR(50),
  provinsi       VARCHAR(50)
);

CREATE TABLE dim_metode_bayar (
  metode_bayar_key  SERIAL PRIMARY KEY,      -- surrogate key
  metode_bayar      VARCHAR(20) NOT NULL UNIQUE  -- Tunai, QRIS, Debit, Transfer
);

CREATE TABLE fakta_penjualan (
  id_transaksi      VARCHAR(10) PRIMARY KEY,  -- PK (opsi 3), degenerate dimension
  waktu_key         INTEGER NOT NULL REFERENCES dim_waktu(waktu_key),
  produk_key        INTEGER NOT NULL REFERENCES dim_produk(produk_key),
  pelanggan_key     INTEGER NOT NULL REFERENCES dim_pelanggan(pelanggan_key),
  metode_bayar_key  INTEGER NOT NULL REFERENCES dim_metode_bayar(metode_bayar_key),
  qty               INTEGER,                  -- measure, additive
  harga_satuan      BIGINT,                   -- measure, non-additive
  total_penjualan   BIGINT                    -- measure, additive
);