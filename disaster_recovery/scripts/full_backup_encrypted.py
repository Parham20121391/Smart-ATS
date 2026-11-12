import os
import gzip
import hashlib
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from cryptography.fernet import Fernet

BASE_DIR = Path(__file__).resolve().parent.parent
FULL_BACKUP_DIR = BASE_DIR / "backups" / "full"
ISOLATED_CLOUD_VAULT = BASE_DIR / "isolated_cloud_vault"
KEY_FILE = BASE_DIR / ".backup_encryption.key"

DOCKER_CONTAINER = os.getenv("POSTGRES_CONTAINER", "smart_ats_db")
DB_USER = os.getenv("POSTGRES_USER", "ats_user")
DB_NAME = os.getenv("POSTGRES_DB", "smart_ats_db")


def get_or_create_encryption_key() -> bytes:
    """دریافت کلید رمزنگاری AES/Fernet از متغیر محیطی یا فایل امن محلی"""
    env_key = os.getenv("BACKUP_ENCRYPTION_KEY")
    if env_key:
        return env_key.encode("utf-8")

    if KEY_FILE.exists():
        return KEY_FILE.read_bytes().strip()

    new_key = Fernet.generate_key()
    KEY_FILE.write_bytes(new_key)
    return new_key


def upload_to_isolated_cloud(encrypted_file_path: Path, checksum_file_path: Path) -> str:
    """
    انتقال فایل بکاپ رمزنگاری شده به فضای ابری ایزوله (S3-Compatible یا Isolated Vault)
    """
    s3_bucket = os.getenv("DR_ISOLATED_S3_BUCKET")
    if s3_bucket:
        import boto3
        s3 = boto3.client(
            "s3",
            endpoint_url=os.getenv("DR_S3_ENDPOINT_URL"),
            aws_access_key_id=os.getenv("DR_S3_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("DR_S3_SECRET_KEY"),
        )
        s3.upload_file(str(encrypted_file_path), s3_bucket, f"full_backups/{encrypted_file_path.name}")
        s3.upload_file(str(checksum_file_path), s3_bucket, f"full_backups/{checksum_file_path.name}")
        return f"s3://{s3_bucket}/full_backups/{encrypted_file_path.name}"

    ISOLATED_CLOUD_VAULT.mkdir(parents=True, exist_ok=True)
    dest_file = ISOLATED_CLOUD_VAULT / encrypted_file_path.name
    dest_checksum = ISOLATED_CLOUD_VAULT / checksum_file_path.name
    shutil.copy2(encrypted_file_path, dest_file)
    shutil.copy2(checksum_file_path, dest_checksum)
    return str(dest_file)


def run_encrypted_full_backup() -> dict:
    """
    تسک SAP-84: تهیه بکاپ کامل دیتابیس، فشرده‌سازی، رمزنگاری متقارن و انتقال به فضای ایزوله هر ۲۴ ساعت
    """
    FULL_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    pg_dump_cmd = [
        "docker", "exec", DOCKER_CONTAINER,
        "pg_dump", "-U", DB_USER, "-d", DB_NAME,
        "--clean", "--if-exists"
    ]
    dump_proc = subprocess.run(pg_dump_cmd, capture_output=True, check=True)

    compressed_bytes = gzip.compress(dump_proc.stdout)

    key = get_or_create_encryption_key()
    cipher = Fernet(key)
    encrypted_bytes = cipher.encrypt(compressed_bytes)

    enc_filename = f"full_backup_{timestamp}.sql.gz.enc"
    enc_path = FULL_BACKUP_DIR / enc_filename
    enc_path.write_bytes(encrypted_bytes)

    sha256_hash = hashlib.sha256(encrypted_bytes).hexdigest()
    checksum_path = FULL_BACKUP_DIR / f"{enc_filename}.sha256"
    checksum_path.write_text(sha256_hash, encoding="utf-8")

    remote_location = upload_to_isolated_cloud(enc_path, checksum_path)

    print(f"[SAP-84] Encrypted Full Backup created & transferred: {enc_filename}")
    print(f"[SAP-84] SHA-256: {sha256_hash}")
    print(f"[SAP-84] Isolated Storage Location: {remote_location}")

    return {
        "filename": enc_filename,
        "sha256": sha256_hash,
        "remote_location": remote_location,
        "size_bytes": enc_path.stat().st_size,
        "schedule": "every_24_hours"
    }


if __name__ == "__main__":
    run_encrypted_full_backup()