import random
import asyncio

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

    @classmethod
    def generate_stealth_headers(cls) -> dict:
        """
        تولید هدرهای فریبنده و پویا جهت شبیه‌سازی هویت مرورگرهای معتبر
        """
        accept_languages = ["en-US,en;q=0.9", "fa-IR,fa;q=0.8,en;q=0.7", "en-GB;q=0.6"]
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": random.choice(accept_languages),
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        }

    @staticmethod
    async def apply_random_delay(min_sec: float = 1.0, max_sec: float = 4.0):
        """
        ایجاد تاخیر تصادفی بین درخواست‌ها جهت شبیه‌سازی رفتار انسانی
        """
        delay = random.uniform(min_sec, max_sec)
        await asyncio.sleep(delay)
        return round(delay, 2)