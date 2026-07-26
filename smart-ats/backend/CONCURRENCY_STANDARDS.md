# استانداردهای مدیریت همزمانی و Race Condition

## قفل‌گذاری بدبینانه (Pessimistic Locking)
برای عملیات حساس بورد کانبان از SELECT ... FOR UPDATE استفاده می‌شود:

```sql
BEGIN;
SELECT * FROM applications 
WHERE id = :application_id 
FOR UPDATE;
-- انجام عملیات تغییر وضعیت
UPDATE applications SET current_status = :new_status WHERE id = :application_id;
COMMIT;
```

## تراکنش‌های ایزوله (MVCC)
برای جلوگیری از Dirty Read سطح ایزولاسیون REPEATABLE READ استفاده می‌شود:

```sql
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
-- عملیات
COMMIT;
```

## قانون کلی
- بورد کانبان: همیشه SELECT ... FOR UPDATE
- گزارش‌گیری: REPEATABLE READ
- عملیات عادی: READ COMMITTED (پیش‌فرض PostgreSQL)