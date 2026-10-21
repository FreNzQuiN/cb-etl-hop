@echo off
setlocal

call :deteksi_pg
if not defined PGBIN (
  echo ERROR: psql.exe tidak ditemukan.
  echo Set PGBIN ke folder bin PostgreSQL, contoh: set PGBIN=C:\Program Files\PostgreSQL\18\bin
  exit /b 1
)
if not defined PG_SUPERUSER set PG_SUPERUSER=postgres
if not defined ETL_PASSWORD set ETL_PASSWORD=etl_tokomaju
set PROJECT=%~dp0

echo [1/3] Membuat role dan database
set PGPASSWORD=%PG_SUPERUSER%
"%PGBIN%\psql.exe" -U %PG_SUPERUSER% -d postgres -v ON_ERROR_STOP=1 -f "%PROJECT%sql\01_create_databases.sql"
if errorlevel 1 goto gagal

echo [2/3] Memuat tabel pelanggan ke database OLTP
"%PGBIN%\psql.exe" -U %PG_SUPERUSER% -d tokomaju_oltp -v ON_ERROR_STOP=1 -f "%PROJECT%sql\02_oltp_pelanggan.sql"
if errorlevel 1 goto gagal

echo [3/3] Membuat star schema data warehouse
set PGPASSWORD=%ETL_PASSWORD%
"%PGBIN%\psql.exe" -U etl -d tokomaju_dw -v ON_ERROR_STOP=1 -f "%PROJECT%sql\03_ddl_dw.sql"
if errorlevel 1 goto gagal

echo.
echo Database siap. Jalankan run_etl.bat untuk menjalankan ETL.
exit /b 0

:gagal
echo.
echo Gagal menyiapkan database. Periksa pesan di atas.
exit /b 1

:deteksi_pg
if not defined PGFULL for /f "delims=" %%p in ('where psql.exe 2^>nul') do set "PGFULL=%%p"
if not defined PGBIN if defined PGFULL set "PGBIN=%PGFULL:~0,-8%"
set "PGFULL="
if defined PGBIN if exist "%PGBIN%psql.exe" exit /b 0
set "PGBIN="
for /d %%d in ("%ProgramFiles%\PostgreSQL\*") do if exist "%%d\bin\psql.exe" set "PGBIN=%%d\bin"
exit /b 0
