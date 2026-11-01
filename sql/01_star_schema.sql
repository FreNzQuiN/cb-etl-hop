DROP TABLE IF EXISTS fakta_penjualan;
DROP TABLE IF EXISTS dim_waktu;
DROP TABLE IF EXISTS dim_produk;
DROP TABLE IF EXISTS dim_pelanggan;

CREATE TABLE dim_waktu (
  waktu_key   INTEGER PRIMARY KEY,          -- yyyymmdd, mis. 20250131
  tanggal     DATE NOT NULL UNIQUE,
  hari        VARCHAR(10),
  bulan       INTEGER,
  nama_bulan  VARCHAR(10),
  kuartal     INTEGER,
  tahun       INTEGER
);
CREATE TABLE dim_produk (
  produk_key   SERIAL PRIMARY KEY,          -- surrogate key
  id_produk    VARCHAR(10) NOT NULL UNIQUE, -- natural key
  nama_produk  VARCHAR(100),
  kategori     VARCHAR(50),
  merek        VARCHAR(50)
);
CREATE TABLE dim_pelanggan (
  pelanggan_key  SERIAL PRIMARY KEY,
  id_pelanggan   VARCHAR(10) NOT NULL UNIQUE,
  nama           VARCHAR(100),
  jenis_kelamin  CHAR(1),
  kota           VARCHAR(50),
  provinsi       VARCHAR(50),
  telepon        VARCHAR(20)
);
CREATE TABLE fakta_penjualan (
  id_transaksi     VARCHAR(10) PRIMARY KEY,
  waktu_key        INTEGER NOT NULL REFERENCES dim_waktu(waktu_key),
  produk_key       INTEGER NOT NULL REFERENCES dim_produk(produk_key),
  pelanggan_key    INTEGER NOT NULL REFERENCES dim_pelanggan(pelanggan_key),
  metode_bayar     VARCHAR(20),
  qty              INTEGER,
  harga_satuan     BIGINT,
  total_penjualan  BIGINT
);