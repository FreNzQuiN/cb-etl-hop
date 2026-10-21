import glob
import os
import shutil


def cari_hop():
    dari_env = os.environ.get("HOPHOME")
    if dari_env and os.path.exists(os.path.join(dari_env, "hop-run.bat")):
        return dari_env
    di_path = shutil.which("hop-run.bat")
    if di_path:
        return os.path.dirname(di_path)
    kandidat = [
        os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "Apache Hop"),
        os.path.join(os.environ.get("ProgramW6432", r"C:\Program Files"), "Apache Hop"),
        os.path.expanduser(r"~\Tools\hop"),
        os.path.expanduser(r"~\Downloads\apache-hop"),
    ]
    for kandidat in kandidat:
        if os.path.exists(os.path.join(kandidat, "hop-run.bat")):
            return kandidat
    return None


def cari_psql():
    dari_env = os.environ.get("PGBIN")
    if dari_env:
        kandidat = os.path.join(dari_env, "psql.exe")
        if os.path.exists(kandidat):
            return kandidat
    di_path = shutil.which("psql") or shutil.which("psql.exe")
    if di_path:
        return di_path
    pola = []
    for dasar in [
        os.environ.get("ProgramFiles", r"C:\Program Files"),
        os.environ.get("ProgramW6432", r"C:\Program Files"),
    ]:
        pola += glob.glob(os.path.join(dasar, "PostgreSQL", "*", "bin", "psql.exe"))
    pola += glob.glob(os.path.expanduser(r"~\Tools\PostgreSQL\*\bin\psql.exe"))
    pola += glob.glob("/usr/bin/psql")
    pola += glob.glob("/usr/local/bin/psql")
    return pola[0] if pola else None


def pesan_hop():
    return (
        "ERROR: Apache Hop tidak ditemukan.\n"
        "  Opsi 1: set variabel lingkungan HOPHOME ke folder instalasi Hop, contoh:\n"
        "    set HOPHOME=C:\\Tools\\hop\n"
        "  Opsi 2: letakkan folder hop-run.bat pada PATH."
    )


def pesan_psql():
    return (
        "ERROR: psql.exe tidak ditemukan.\n"
        "  Opsi 1: set variabel lingkungan PGBIN ke folder bin PostgreSQL, contoh:\n"
        "    set PGBIN=C:\\Program Files\\PostgreSQL\\18\\bin\n"
        "  Opsi 2: letakkan psql.exe pada PATH."
    )
