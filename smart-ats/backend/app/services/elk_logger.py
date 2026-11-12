import os
import json
import socket
import logging
import traceback
from datetime import datetime, timezone
from typing import Optional

LOGSTASH_HOST = os.getenv("LOGSTASH_HOST", "127.0.0.1")
LOGSTASH_PORT = int(os.getenv("LOGSTASH_PORT", "5000"))
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")


class TCPLogstashHandler(logging.Handler):
    """
    هندلر اختصاصی ارسال مستقیم و غیرمسدودکننده لاگ‌ها و رویدادهای خطا به Logstash (تسک SAP-77)
    """

    def __init__(self, host: str = LOGSTASH_HOST, port: int = LOGSTASH_PORT, service_name: str = "smart-ats-backend"):
        super().__init__()
        self.host = host
        self.port = port
        self.service_name = service_name

    def emit(self, record: logging.LogRecord) -> None:
        try:
            log_payload = {
                "@timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "service": self.service_name,
                "environment": ENVIRONMENT,
                "logger": record.name,
                "module": record.module,
                "funcName": record.funcName,
                "lineNo": record.lineno,
                "message": record.getMessage(),
            }

            if record.exc_info:
                log_payload["exception"] = "".join(traceback.format_exception(*record.exc_info))

            data = (json.dumps(log_payload, ensure_ascii=False) + "\n").encode("utf-8")

            with socket.create_connection((self.host, self.port), timeout=1.5) as sock:
                sock.sendall(data)
        except Exception:
            # Fail-safe: عدم توقف سرویس‌های FastAPI یا Celery در صورت در دسترس نبودن موقت Logstash
            pass


def setup_centralized_logging(service_name: str = "smart-ats-backend", level: int = logging.INFO) -> logging.Logger:
    """
    پیکربندی یکپارچه لاگر کنسول و ارسال متمرکز به Logstash برای بک‌اند و ورکرهای هوش مصنوعی
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # جلوگیری از افزودن هندلر تکراری
    for handler in root_logger.handlers:
        if isinstance(handler, TCPLogstashHandler) and handler.service_name == service_name:
            return root_logger

    if not any(isinstance(h, logging.StreamHandler) and not isinstance(h, TCPLogstashHandler) for h in root_logger.handlers):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        root_logger.addHandler(console_handler)

    logstash_handler = TCPLogstashHandler(service_name=service_name)
    logstash_handler.setLevel(level)
    root_logger.addHandler(logstash_handler)

    return root_logger