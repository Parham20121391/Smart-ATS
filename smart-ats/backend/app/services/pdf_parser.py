import pdfplumber
import io
from fastapi import HTTPException, status


class PDFParserService:
    """
    سرویس استخراج متن خام از فایل‌های PDF رزومه
    جهت آماده‌سازی داده برای پایپ‌لاین هوش مصنوعی
    """

    @staticmethod
    def extract_text_from_bytes(file_bytes: bytes) -> str:
        """
        استخراج متن خام از بایت‌های فایل PDF با بالاترین دقت
        """
        try:
            text_pages = []

            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page_number, page in enumerate(pdf.pages, start=1):
                    page_text = page.extract_text()
                    if page_text:
                        text_pages.append(f"--- صفحه {page_number} ---\n{page_text}")

            if not text_pages:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="متنی از فایل PDF استخراج نشد. فایل ممکن است اسکن‌شده یا خالی باشد."
                )

            full_text = "\n\n".join(text_pages)
            return full_text

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"خطا در پردازش فایل PDF: {str(e)}"
            )

    @staticmethod
    def get_text_stats(text: str) -> dict:
        """
        آمار متن استخراج‌شده برای لاگینگ و مانیتورینگ
        """
        return {
            "total_characters": len(text),
            "total_words": len(text.split()),
            "total_lines": len(text.splitlines())
        }