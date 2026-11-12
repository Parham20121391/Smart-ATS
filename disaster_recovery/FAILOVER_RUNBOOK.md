# دستورالعمل جامع بازیابی از فاجعه و بازگردانی داده‌ها (Failover & Disaster Recovery Runbook)

## ۱. اهداف بازیابی (SLA Targets)
- **RTO (Recovery Time Objective):** کمتر از **۶۰ دقیقه (۱ ساعت)** برای بازگردانی کامل سرویس و پایگاه داده.
- **RPO (Recovery Point Objective):** حداکثر **۶ ساعت** (مبتنی بر چرخه دامپ افزایشی `SAP-83` و دامپ کامل رمزنگاری شده `SAP-84`).

## ۲. معماری پشتیبان‌گیری
1. **پشتیبان افزایشی (Incremental Backup - SAP-83):** اجرای خودکار هر ۶ ساعت از طریق Cron (`disaster_recovery/crontab.txt`) با ثبت موقعیت `WAL LSN` در `incremental_manifest.json`.
2. **پشتیبان کامل رمزنگاری شده (Encrypted Full Backup - SAP-84):** اجرای خودکار هر ۲۴ ساعت، فشرده‌سازی با GZIP، رمزنگاری با استاندارد `Fernet (AES + HMAC-SHA256)` و انتقال به فضای ابری ایزوله همراه با امضای `SHA-256`.

## ۳. مراحل عملیاتی بازگردانی اضطراری (Failover Procedure)
1. **بازیابی زیرساخت کانتینری:**
   ```bash
   docker-compose up -d postgres_db redis qdrant