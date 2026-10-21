# Pipeline ETL Data Warehouse TokoMaju (Apache Hop)

Project Apache Hop untuk membangun data warehouse penjualan ritel "TokoMaju" dari
tiga sumber data berbeda format: CSV, Excel, dan database PostgreSQL.

Project ini portabel: seluruh path di dalam folder project relatif, dan lokasi
instalasi Apache Hop, PostgreSQL, serta Python ditemukan otomatis. Folder project
boleh disalin ke perangkat lain dan langsung dijalankan.

## Isi project

```
hop-tokomaju/
  data/                      salinan sumber data tugas (CSV, Excel, SQL)
  pipelines/                 5 pipeline (.hpl)
  workflows/ETL_Tokomaju.hwf orkestrasi seluruh pipeline
  metadata/                  run configuration dan koneksi database PostgreSQL
  sql/                       skrip SQL pembuatan database, skema, dan verifikasi
  tools/                     generator file pipeline dan skrip verifikasi
  out/                       keluaran pipeline, berkas ditolak, log eksekusi
  docs/desain_pipeline.md    catatan desain pipeline
  project-config.json        konfigurasi project Hop
  setup_database.bat         membuat role, database, dan skema
  run_etl.bat                menjalankan workflow ETL lalu verifikasi
  README.md
```

## Prasyarat

| Kebutuhan | Versi | Catatan |
| --- | --- | --- |
| Apache Hop | 2.19.0 atau lebih baru | folder instalasi containing `hop-run.bat` |
| Java | 21 atau lebih baru | pada PC ini dipakai Oracle JDK 25.0.4 |
| PostgreSQL | 15 atau lebih baru | server lokal, dipakai lewat `localhost:5432` |
| Python | 3.8 atau lebih baru | dipakai untuk generator, verifikasi, dan pendaftaran project |
| Sistem operasi | Windows 10/11 | skrip `.bat` memakai cmd.exe |

## Cara menjalankan

Semua perintah dijalankan dari dalam folder project ini.

Langkah 1, sekali saja, untuk membuat role, database, dan skema:

```
setup_database.bat
```

Langkah 2, setiap kali data berubah:

```
run_etl.bat
```

`run_etl.bat` melakukan empat hal berurutan: mendaftarkan project ke konfigurasi
Hop, menjalankan workflow Apache Hop, menjalankan verifikasi rekonsiliasi, lalu
menjalankan query verifikasi SQL. Hasil rekonsiliasi disimpan di
`out\verifikasi.txt` dan hasil query SQL di `out\verifikasi_sql.txt`.

Pendaftaran project otomatis menulis satu entri `tokomaju` pada
`config\hop-config.json` milik instalasi Hop, dengan project home menunjuk ke
folder ini. Cara manualnya sama dengan yang dilakukan GUI: buka Hop GUI, pilih
Manage projects, lalu tambahkan folder project ini sebagai project `tokomaju`.

Perintah Hop yang dipakai di balik skrip tersebut, dijalankan dari folder
instalasi Hop:

```
hop-run.bat --project=tokomaju --file=workflows/ETL_Tokomaju.hwf --runconfig=local
```

Workflow boleh dijalankan berulang. Action "Kosongkan Data Warehouse" menjalankan
satu pernyataan `TRUNCATE TABLE ... RESTART IDENTITY` untuk keempat tabel
sekaligus, karena PostgreSQL menolak pengosongan tabel induk yang masih dirujuk
foreign key. Akibatnya jumlah baris, surrogate key, dan total penjualan hasil
setiap menjalankan selalu sama.

## Menjalankan di perangkat lain

Folder project bisa disalin ke PC lain tanpa perubahan. Yang perlu dilakukan di
PC tujuan:

1. Pasang Apache Hop, PostgreSQL, Java, dan Python.
2. Pastikan `psql.exe` dan `hop-run.bat` dapat ditemukan, atau set variabel
   lingkungan berikut sesuai lokasi instalasi di PC tujuan:

| Variabel | Isi | Contoh |
| --- | --- | --- |
| `HOPHOME` | folder instalasi Apache Hop | `set HOPHOME=C:\Tools\hop` |
| `PGBIN` | folder `bin` PostgreSQL | `set PGBIN=C:\Program Files\PostgreSQL\18\bin` |
| `ETL_PASSWORD` | kata sandi role `etl` | `set ETL_PASSWORD=kata_sandi_anda` |
| `PG_SUPERUSER` | nama role superuser PostgreSQL | `set PG_SUPERUSER=postgres` |
| `PGHOST`, `PGPORT`, `PGUSER` | alamat database target | `set PGHOST=localhost` |

Tanpa variabel tersebut, skrip mencari sendiri: `hop-run.bat` dan `psql.exe`
pada PATH, lalu di `%ProgramFiles%\Apache Hop`, `%USERPROFILE%\Tools\hop`, dan
`%ProgramFiles%\PostgreSQL\<versi>\bin`. Bila tetap tidak ditemukan, skrip
berhenti dengan pesan yang menyebutkan variabel yang harus diisi.

Kredensial bawaan pada project ini adalah `etl` dengan kata sandi `etl_tokomaju`
untuk kedua database, dan role `postgres` dengan kata sandi yang diberikan saat
instalasi server untuk pembuatan database. Kredensial bawaan ini khusus untuk
coursework lokal dan sebaiknya diganti bila project dibagikan atau
dipublikasikan. Script `sql\01_create_databases.sql` dan metadata
`metadata\rdbms\*.json` memuat kata sandi yang sama, jadi bila diganti, ubah di
keduanya.

## Sumber data

| File | Format | Isi | Masalah yang disisipkan |
| --- | --- | --- | --- |
| `data/penjualan.csv` | CSV, pemisah titik koma | 2445 baris transaksi | 4 format tanggal, 45 baris duplikat, 18 baris qty negatif, 6 baris qty nol, harga berawalan Rp dan berpemisah ribuan, 25 baris tanpa id pelanggan |
| `data/produk.xlsx` | Excel, sheet `Produk` | 43 baris master produk | 3 id produk kembar, nama kategori tidak konsisten, 1 kategori kosong |
| `data/pelanggan.sql` | SQL PostgreSQL/MySQL | 180 pelanggan | 32 kota kosong, nomor telepon enam format berbeda |

## Pipeline

| Pipeline | Transform | Fungsi |
| --- | --- | --- |
| P1_cleansing | CSV Input, Unique Rows (HashSet), SuperScript, Filter Rows, Dummy, Dummy, Select Values, Text File Output, Select Values, Text File Output | Buang transaksi kembar, seragamkan tanggal dan harga, hitung total penjualan, pisahkan baris sah dan baris ditolak |
| P2_dim_produk | Excel Input, Unique Rows (HashSet), SuperScript, Select Values, Table Output | Muat dimensi produk dengan kategori seragam |
| P3_dim_pelanggan | Table Input, SuperScript, Select Values, Table Output | Muat dimensi pelanggan dari database OLTP, isi kota kosong, seragamkan telepon |
| P4_dim_waktu | CSV Input, SuperScript, Unique Rows (HashSet), Select Values, Table Output | Bangun dimensi waktu beserta atribut kalender |
| P5_fact_penjualan | CSV Input, Database Lookup, Database Lookup, Database Lookup, SuperScript, Filter Rows, Dummy, Dummy, Select Values, Table Output, Select Values, Text File Output | Ambil surrogate key tiga dimensi, muat tabel fakta, karantina transaksi yang produknya tidak ada di master |

Urutan muat sesuai aturan data warehouse: dimensi lebih dahulu, lalu fakta.
Surrogate key setiap tabel dimensi memakai kolom `GENERATED BY DEFAULT AS IDENTITY`
di PostgreSQL, dan tabel fakta mengambil key tersebut lewat transform Database Lookup.

P1 dijalankan sebelum tabel data warehouse dikosongkan, sehingga kegagalan
cleansing tidak mengosongkan isi data warehouse.

Seluruh file pipeline memakai variabel `${PROJECT_HOME}`, sehingga folder project
boleh dipindah ke mana saja tanpa menyunting XML.

## Mutu data yang ditangani

| Kasus | Penanganan | Ada di data sumber |
| --- | --- | --- |
| Tanggal `2025-01-12` | Dibaca dan dinormalisasi ke format `YYYY-MM-DD` | ya |
| Tanggal `12/01/2025` | Dibaca dengan pola hari/bulan/tahun | ya |
| Tanggal `13-01-2025` | Dibaca dengan pola hari-bulan-tahun | ya |
| Tanggal `21 Sep 2025` | Dibaca dengan nama bulan Indonesia | ya |
| Tanggal `21 September 2025` | Nama bulan penuh juga dikenali | aturan, tidak ada di data |
| Tanggal di luar kalender, misalnya `30/02/2025` | Ditolak, alasan `tanggal tidak valid` | aturan, tidak ada di data |
| Transaksi kembar | Dibuang oleh Unique Rows (HashSet) memakai kunci `id_transaksi` | ya |
| Qty negatif | Ditolak, alasan `jumlah terjual negatif` | ya |
| Qty nol | Ditolak, alasan `jumlah terjual nol` | ya |
| Qty bukan bilangan | Ditolak, alasan `jumlah terjual tidak valid` | aturan, tidak ada di data |
| Harga `Rp85.000` | Dibaca menjadi 85000 | ya |
| Harga `179.600` | Dibaca menjadi 179600 | aturan, tidak ada di data |
| Harga bukan bilangan bulat | Ditolak, alasan `harga satuan tidak valid` | aturan, tidak ada di data |
| Id pelanggan kosong | Ditolak, alasan `id pelanggan kosong` | ya |
| Id transaksi, id produk, atau metode bayar kosong | Ditolak dengan alasan masing-masing | aturan, tidak ada di data |
| Kategori `elektronik `, `ELEKTRONIK` | Diseragamkan menjadi `Elektronik` | ya |
| Kategori `Kesehatan dan Kecantikan` | Diseragamkan menjadi `Kesehatan & Kecantikan` | ya |
| Kategori kosong | Diisi `Tidak Diketahui` | ya |
| Produk kembar di master | Dibuang oleh Unique Rows (HashSet) memakai kunci `id_produk` | ya |
| Produk tidak ada di master | Transaksi dikarantina ke `out\transaksi_produk_tidak_dikenal.csv` | ya |
| Kota kosong atau NULL | Diisi `Tidak Diketahui` | ya |
| Telepon `(0899) 72837929` | Diseragamkan menjadi `089972837929` | ya |
| Telepon `+62 897 9780 2520` | Diseragamkan menjadi `089797782520` | ya |

Baris bertanda "aturan, tidak ada di data" diuji memakai data sementara khusus
regresi dan tidak disertakan dalam data sumber.

Berkas `out\transaksi_ditolak.csv` memuat seluruh kolom sumber apa adanya
beserta kolom `alasan`, sehingga setiap baris yang ditolak dapat ditelusuri
kembali ke baris asalnya.

## Skema bintang

```
dim_waktu(date_sk, tanggal, hari, nama_hari, bulan, nama_bulan, kuartal, tahun)
dim_produk(product_sk, id_produk, nama_produk, kategori, merek)
dim_pelanggan(customer_sk, id_pelanggan, nama, jenis_kelamin, kota, provinsi, telepon)

fact_penjualan(fact_sk, id_transaksi, tanggal, date_sk, id_produk, product_sk,
               id_pelanggan, customer_sk, qty, harga_satuan, total_penjualan,
               metode_bayar)
```

Dimensi memakai kunci alami dan surrogate key. Tabel fakta memakai surrogate key
dimensi sebagai foreign key, sekaligus mempertahankan kunci alami sebagai atribut
degenerat agar penelusuran ke sumber tetap mudah. Kunci asing dideklarasikan di
`sql\03_ddl_dw.sql` dan diverifikasi setiap kali pipeline dijalankan.

## Hasil eksekusi terakhir

| Tabel | Jumlah baris |
| --- | --- |
| dim_waktu | 363 |
| dim_produk | 40 |
| dim_pelanggan | 180 |
| fact_penjualan | 2342 |

Rekonsiliasi jumlah baris dari sumber sampai data warehouse:

| Tahap | Jumlah baris |
| --- | --- |
| Baris pada `penjualan.csv` | 2445 |
| Setelah 45 baris kembar dibuang | 2400 |
| Setelah 49 baris ditolak pada cleansing | 2351 |
| Setelah 9 baris dikarantina karena produk tidak ada di master | 2342 baris fakta |

Total penjualan pada sumber 461.823.200 dan pada data warehouse 459.188.700.
Selisih 2.634.500 berasal dari baris yang ditolak dan dikarantina, yang tercatat
lengkap pada `out\transaksi_ditolak.csv` dan `out\transaksi_produk_tidak_dikenal.csv`.

Pemeriksaan integritas referensial: 0 fakta tanpa pasangan dimensi waktu, 0 fakta
tanpa pasangan dimensi produk, 0 fakta tanpa pasangan dimensi pelanggan, 0 id
transaksi kembar pada tabel fakta, dan 0 baris dengan `total_penjualan` berbeda
dari `qty x harga_satuan`. Pipeline dijalankan dua kali berturut-turut dan
menghasilkan jumlah baris, surrogate key, dan total penjualan yang identik.

Kategori pada dimensi produk setelah dinormalisasi: Elektronik 8 produk,
Fashion 7, Rumah Tangga 6, Makanan & Minuman 8, Olahraga 5,
Kesehatan & Kecantikan 5, dan Tidak Diketahui 1. Master produk memuat 14 ejaan
kategori yang berbeda, termasuk singkatan Mamin yang dipetakan ke Makanan &
Minuman, sehingga dimensi produk berisi tujuh kategori.

## Verifikasi

```
python tools\verify_etl.py
```

Skrip menghitung ulang hasil ETL dari berkas sumber dengan aturan yang sama
dengan pipeline, lalu membandingkannya dengan isi database: jumlah baris, total
penjualan, dan integritas referensial. Bila ada selisih, skrip keluar dengan
kode 1 sehingga `run_etl.bat` berhenti dan menandai kegagalan.

Query verifikasi SQL tersedia terpisah di `sql\04_verifikasi.sql` dan dijalankan
oleh `run_etl.bat` pada langkah keempat.

## Catatan instalasi

Apache Hop 2.19.0 mensyaratkan Java 21 sebagai versi minimum. Bukti: kelas pada
`hop-core-2.19.0.jar` dikompilasi untuk bytecode Java 21, dan halaman unduhan
resmi Hop menyebut "requires Java 21". Java 21 juga merupakan versi yang
resmi diuji oleh proyek Hop.

Project ini tidak mengunci versi JVM tertentu. Pemilihannya diambil Apache Hop
dari `JAVA_HOME`, atau `HOP_JAVA_HOME` bila ingin menunjuk JRE khusus untuk Hop
saja tanpa mengubah milik sistem. Pipelines yang dipakai di sini hanya
memerlukan transform bawaan Hop (CSV Input, Excel Input, Database Lookup,
Table Input, Table Output, Text File Output, Unique Rows, Filter Rows,
Select Values, Dummy, dan SuperScript bermesin JavaScript). Mesin JavaScript
tersebut adalah GraalVM Polyglot 25.0.3 yang disertakan Hop, dan mendukung
Java 21 ke atas.

Peralat yang dipakai untuk menyusun laporan ini memakai Oracle JDK 25.0.4 dan
seluruh pipeline berjalan tanpa kendala pada versi tersebut, sehingga Java 21
dan Java 25 sama-sama dapat dipakai.

Bila memilih JRE, gunakan Oracle JDK atau Microsoft OpenJDK 21. Dokumentasi Hop
mencantumkan Adoptium sebagai JVM yang memiliki masalah yang pernah
dikonfirmasi.
