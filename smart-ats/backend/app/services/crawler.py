from playwright.sync_api import sync_playwright
import logging

logger = logging.getLogger(__name__)


class WebCrawlerService:
    """
    تسک ۹۷ - سرویس خزش وب با Playwright و مرورگر هدلس Chromium
    """

    @staticmethod
    async def crawl_job_page(target_url: str) -> str:
        """
        تسک ۹۸، ۹۹، ۱۰۰، ۱۰۱ - خزش صفحه هدف و استخراج محتوا
        """
        import asyncio
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            WebCrawlerService._sync_crawl,
            target_url
        )
        return result

    @staticmethod
    def _sync_crawl(target_url: str) -> str:
        with sync_playwright() as p:
            # تسک ۹۸ - راه‌اندازی مرورگر با تنظیمات بهینه حافظه
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage"
                ]
            )

            context = None
            try:
                # تسک ۹۹ - شبیه‌سازی مرورگر واقعی با User-Agent
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                               "AppleWebKit/537.36 (KHTML, like Gecko) "
                               "Chrome/120.0.0.0 Safari/537.36"
                )
                page = context.new_page()

                # تسک ۱۰۰ - ناوبری با مدیریت timeout
                logger.info(f"Crawling: {target_url}")
                page.goto(
                    target_url,
                    wait_until="networkidle",
                    timeout=30000
                )

                page_content = page.content()
                logger.info(f"Crawled {len(page_content)} characters from {target_url}")
                return page_content

            except Exception as e:
                logger.error(f"Crawl error for {target_url}: {str(e)}")
                return f"CRAWL_ERROR: {str(e)}"

            finally:
                # تسک ۱۰۱ - بسته شدن context و browser
                if context:
                    context.close()
                browser.close()