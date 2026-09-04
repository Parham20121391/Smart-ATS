class ProxyRotationEngine:
    """
    موتور مدیریت و چرخش داینامیک پروکسی‌ها جهت عبور از سدهای امنیتی پلتفرم‌های هدف
    """
    # استخر پروکسی‌های دیتاسنتری و مسکونی
    PROXY_POOL = [
        "http://proxy_user:proxy_pass@residential_ip1:8000",
        "http://proxy_user:proxy_pass@residential_ip2:8000",
        "http://proxy_user:proxy_pass@datacenter_ip1:8080",
    ]