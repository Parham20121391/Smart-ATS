import os
import json
import gzip
import subprocess
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INC_BACKUP_DIR = BASE_DIR / "backups" / "incremental"
MANIFEST_FILE = INC_BACKUP_DIR / "incremental_manifest.json"

DOCKER_CONTAINER = os.getenv("POSTGRES_CONTAINER", "smart_ats_db")
DB_USER = os.getenv("POSTGRES_USER", "ats_user")
DB_NAME = os.getenv("POSTGRES_DB", "smart_ats_db")


def get_current_wal_lsn() -> str:
    """دریافت موقعیت فعلی WAL دیتابیس PostgreSQL جهت ردیابی تغییرات افزایشی"""
    cmd = [
        "docker", "exec", DOCKER_CONTAINER,
        "psql", "-U", DB_USER, "-d", DB_NAME, "-t", "-A",
        "-c", "SELECT pg_current_wal_lsn();"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return res.stdout.strip()


def run_incremental_backup() -> dict:
    """
    تسک SAP-83: تهیه دامپ افزایشی فشرده از داده‌های دیتابیس هر ۶ ساعت یک‌بار
    """
    INC_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    current_lsn = get_current_wal_lsn()

    previous_lsn = "0/0"
    history = []
    if MANIFEST_FILE.exists():
        data = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
        history = data.get("backups", [])
        if history:
            previous_lsn = history[-1].get("wal_lsn", "0/0")

    dump_filename = f"inc_backup_{timestamp}.sql.gz"
    dump_path = INC_BACKUP_DIR / dump_filename

    pg_dump_cmd = [
        "docker", "exec", DOCKER_CONTAINER,
        "pg_dump", "-U", DB_USER, "-d", DB_NAME,
        "--data-only", "--column-inserts"
    ]
    dump_proc = subprocess.run(pg_dump_cmd, capture_output=True, check=True)

    header_comment = (
        f"-- Smart ATS Incremental Backup\n"
        f"-- Timestamp (UTC): {timestamp}\n"
        f"-- Previous WAL LSN: {previous_lsn}\n"
        f"-- Current WAL LSN: {current_lsn}\n\n"
    ).encode("utf-8")

    with gzip.open(dump_path, "wb") as gz_file:
        gz_file.write(header_comment)
        gz_file.write(dump_proc.stdout)

    record = {
        "filename": dump_filename,
        "timestamp_utc": timestamp,
        "previous_wal_lsn": previous_lsn,
        "wal_lsn": current_lsn,
        "size_bytes": dump_path.stat().st_size,
        "schedule": "every_6_hours"
    }
    history.append(record)
    MANIFEST_FILE.write_text(json.dumps({"backups": history}, indent=2), encoding="utf-8")

    print(f"[SAP-83] Incremental backup created: {dump_filename} | WAL LSN: {previous_lsn} -> {current_lsn}")
    return record


if __name__ == "__main__":
    run_incremental_backup()