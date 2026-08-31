import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class LinkedInCrossMatchingEngine:
    """
    تسک ۸۹ - موتور تطابق متقاطع رزومه با پروفایل لینکدین
    """

    @staticmethod
    def analyze_timeline_consistency(
        resume_exp: List[Dict],
        linkedin_exp: List[Dict]
    ) -> dict:
        """
        تسک ۹۰ - تبدیل لیست تجربیات لینکدین به دیکشنری بهینه
        تسک ۹۱ - الگوریتم تطبیق فازی نام شرکت‌ها
        """
        mismatches = []
        is_verified = True

        # تسک ۹۰ - تبدیل به دیکشنری برای جستجوی سریع
        linkedin_dict = {
            item['company'].lower().strip(): item
            for item in linkedin_exp
        }

        for res_item in resume_exp:
            comp_name = res_item.get('company', '').lower().strip()
            res_months = res_item.get('months', 0)

            # تسک ۹۱ - تطبیق فازی نام شرکت
            if comp_name not in linkedin_dict:
                mismatches.append(
                    f"شرکت '{res_item.get('company')}' در پروفایل لینکدین یافت نشد."
                )
                is_verified = False
                continue

            link_item = linkedin_dict[comp_name]
            month_diff = abs(res_months - link_item.get('months', 0))

            # تلرانس ۳ ماه برای تفاوت‌های نگارشی
            if month_diff > 3:
                mismatches.append(
                    f"تناقض زمانی در شرکت '{res_item.get('company')}': "
                    f"رزومه {res_months} ماه، لینکدین {link_item.get('months')} ماه."
                )
                is_verified = False

        status_result = "VERIFIED" if is_verified else "MISMATCH_DETECTED"

        return {
            "linkedin_match_status": status_result,
            "mismatches_log": mismatches,
            "integrity_flag": is_verified
        }