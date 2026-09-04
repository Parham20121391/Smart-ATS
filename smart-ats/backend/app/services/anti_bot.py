import random

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

    @classmethod
    def get_random_proxy_config(cls) -> dict:
        """
        انتخاب تصادفی پروکسی و فرمت‌بندی برای Playwright
        """
        if not cls.PROXY_POOL:
            return None
        
        selected_proxy = random.choice(cls.PROXY_POOL)
        return {
            "server": selected_proxy
        }