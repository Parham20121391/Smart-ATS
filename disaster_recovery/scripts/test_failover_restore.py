import os
import time
import gzip
import hashlib
import subprocess
from pathlib import Path
from cryptography.fernet import Fernet

BASE_DIR = Path(__file__).resolve().parent.parent
ISOLATED_CLOUD_VAULT = BASE_DIR / "isolated_cloud_vault"
KEY_FILE = BASE_DIR / ".backup_encryption.key"

DOCKER_CONTAINER = os.getenv("POSTGRES_CONTAINER", "smart_ats_db")
DB_USER = os.getenv("POSTGRES_USER", "ats_user")
VERIFY_DB_NAME = "smart_ats_dr_failover_test"


def run_failover_restore_drill() -> dict:
    """
    تسک SAP-85: تست عملیاتی رمزگشایی، اعتبارسنجی یکپارچگی و بازگردانی کامل دیتابیس
    با هدف تکمیل فرآیند در کمتر از ۱ ساعت (RTO < 3600s)
    """
    start_time = time.perf_counter()

    encrypted_backups = sorted(ISOLATED_CLOUD_VAULT.glob("full_backup_*.sql.gz.enc"))
    if not encrypted_backups:
        raise FileNotFoundError("هیچ نسخه پشتیبان رمزنگاری‌شده‌ای در فضای ابری ایزوله یافت نشد.")

    latest_backup = encrypted_backups[-1]
    checksum_file = ISOLATED_CLOUD_VAULT / f"{latest_backup.name}.sha256"

    actual_sha256 = hashlib.sha256(latest_backup.read_bytes()).hexdigest()
    expected_sha256 = checksum_file.read_text(encoding="utf-8").strip()
    assert actual_sha256 == expected_sha256, "خطای یکپارچگی فایل بکاپ (SHA-256 Mismatch)!"

    env_key = os.getenv("BACKUP_ENCRYPTION_KEY")
    key = env_key.encode("utf-8") if env_key else KEY_FILE.read_bytes().strip()
    cipher = Fernet(key)
    decrypted_compressed = cipher.decrypt(latest_backup.read_bytes())
    sql_bytes = gzip.decompress(decrypted_compressed)

    subprocess.run(
        ["docker", "exec", DOCKER_CONTAINER, "psql", "-U", DB_USER, "-d", "postgres",
         "-c", f"DROP DATABASE IF EXISTS {VERIFY_DB_NAME};"],
        check=True, capture_output=True
    )
    subprocess.run(
        ["docker", "exec", DOCKER_CONTAINER, "psql", "-U", DB_USER, "-d", "postgres",
         "-c", f"CREATE DATABASE {VERIFY_DB_NAME};"],
        check=True, capture_output=True
    )

    try:
        subprocess.run(
            ["docker", "exec", "-i", DOCKER_CONTAINER, "psql", "-U", DB_USER, "-d", VERIFY_DB_NAME],
            input=sql_bytes,
            check=True,
            capture_output=True
        )

        check_tables_cmd = [
            "docker", "exec", DOCKER_CONTAINER,
            "psql", "-U", DB_USER, "-d", VERIFY_DB_NAME, "-t", "-A",
            "-c", "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';"
        ]
        tables_count = int(subprocess.run(check_tables_cmd, capture_output=True, text=True, check=True).stdout.strip())
        assert tables_count >= 4, f"تعداد جداول بازگردانی شده ناکافی است: {tables_count}"

    finally:
        subprocess.run(
            ["docker", "exec", DOCKER_CONTAINER, "psql", "-U", DB_USER, "-d", "postgres",
             "-c", f"DROP DATABASE IF EXISTS {VERIFY_DB_NAME};"],
            check=True, capture_output=True
        )

    elapsed_seconds = round(time.perf_counter() - start_time, 3)
    assert elapsed_seconds < 3600, "زمان بازیابی از سقف ۱ ساعت عبور کرد!"

    print(f"[SAP-85] Failover Restore Drill Passed! Restored Tables: {tables_count} | Elapsed Time: {elapsed_seconds}s (Target < 3600s)")
    return {
        "backup_file": latest_backup.name,
        "restored_tables_count": tables_count,
        "elapsed_seconds": elapsed_seconds,
        "rto_compliant": elapsed_seconds < 3600
    }


if __name__ == "__main__":
    run_failover_restore_drill()