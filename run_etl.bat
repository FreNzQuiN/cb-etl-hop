@echo off
setlocal

call :deteksi_hop
if not defined HOPHOME (
  echo ERROR: Apache Hop tidak ditemukan.
  echo Set HOPHOME ke folder instalasi Hop, contoh: set HOPHOME=C:\Tools\hop
  exit /b 1
)
call :deteksi_pg
if not defined PGBIN (
  echo ERROR: psql.exe tidak ditemukan.
  echo Set PGBIN ke folder bin PostgreSQL, contoh: set PGBIN=C:\Program Files\PostgreSQL\18\bin
  exit /b 1
)
call :deteksi_python
if not defined PYTHON (
  echo ERROR: Python tidak ditemukan. Install Python 3 atau set PYTHON.
  exit /b 1
)
if not defined ETL_PASSWORD set ETL_PASSWORD=etl_tokomaju
if not defined PG_SUPERUSER set PG_SUPERUSER=postgres
set PROJECT=%~dp0
if not exist "%PROJECT%out\logs" mkdir "%PROJECT%out\logs"

echo [1/4] Mendaftarkan project Apache Hop
"%PYTHON%" "%PROJECT%tools\register_project.py"
if errorlevel 1 goto gagal

echo [2/4] Menjalankan workflow ETL Apache Hop
cd /d "%HOPHOME%"
call hop-run.bat --project=tokomaju --file=workflows/ETL_Tokomaju.hwf --runconfig=local > "%PROJECT%out\workflow_run.log" 2>&1
if errorlevel 1 goto gagal

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set STAMP=%%i
copy /y "%PROJECT%out\workflow_run.log" "%PROJECT%out\logs\workflow_run_%STAMP%.log" >nul

echo [3/4] Verifikasi rekonsiliasi data
set PGPASSWORD=%ETL_PASSWORD%
"%PYTHON%" "%PROJECT%tools\verify_etl.py" > "%PROJECT%out\verifikasi.txt" 2>&1
if errorlevel 1 goto gagal
type "%PROJECT%out\verifikasi.txt"

echo [4/4] Verifikasi query SQL
"%PGBIN%\psql.exe" -U etl -d tokomaju_dw -f "%PROJECT%sql\04_verifikasi.sql" > "%PROJECT%out\verifikasi_sql.txt" 2>&1
if errorlevel 1 goto gagal

echo.
echo Selesai.
echo Log   : %PROJECT%out\logs
echo Hasil : %PROJECT%out\verifikasi.txt
exit /b 0

:gagal
echo.
echo Pipeline gagal. Periksa log: %PROJECT%out\workflow_run.log
exit /b 1

:deteksi_hop
if not defined HOPFULL for /f "delims=" %%p in ('where hop-run.bat 2^>nul') do set "HOPFULL=%%p"
if not defined HOPHOME if defined HOPFULL set "HOPHOME=%HOPFULL:~0,-12%"
set "HOPFULL="
if defined HOPHOME if exist "%HOPHOME%hop-run.bat" exit /b 0
set "HOPHOME="
if exist "%ProgramFiles%\Apache Hop\hop-run.bat" set "HOPHOME=%ProgramFiles%\Apache Hop"
if not defined HOPHOME if exist "%USERPROFILE%\Tools\hop\hop-run.bat" set "HOPHOME=%USERPROFILE%\Tools\hop"
if not defined HOPHOME if exist "%USERPROFILE%\Downloads\apache-hop\hop-run.bat" set "HOPHOME=%USERPROFILE%\Downloads\apache-hop"
if not defined HOPHOME if exist "%USERPROFILE%\Downloads\apache-hop\bin\hop-run.bat" set "HOPHOME=%USERPROFILE%\Downloads\apache-hop\bin"
exit /b 0

:deteksi_pg
if not defined PGFULL for /f "delims=" %%p in ('where psql.exe 2^>nul') do set "PGFULL=%%p"
if not defined PGBIN if defined PGFULL set "PGBIN=%PGFULL:~0,-8%"
set "PGFULL="
if defined PGBIN if exist "%PGBIN%psql.exe" exit /b 0
set "PGBIN="
for /d %%d in ("%ProgramFiles%\PostgreSQL\*") do if exist "%%d\bin\psql.exe" set "PGBIN=%%d\bin"
exit /b 0

:deteksi_python
if not defined PYTHON for /f "delims=" %%p in ('where py.exe 2^>nul') do set "PYTHON=%%p"
if not defined PYTHON for /f "delims=" %%p in ('where python.exe 2^>nul') do set "PYTHON=%%p"
if defined PYTHON "%PYTHON%" -c "import sys" >nul 2>&1
if errorlevel 1 set "PYTHON="
exit /b 0
