# smart-ats/backend/app/services/auth.py
import os
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

# تنظیمات کلید امنیتی و الگوریتم JWT
SECRET_KEY = os.getenv("SECRET_KEY", "smart_ats_super_secret_jwt_key_2026_production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class AuthService:
    """سرویس احراز هویت، رمزنگاری و مدیریت توکن‌های JWT"""

    @classmethod
    def hash_password(cls, password: str) -> str:
        """تسک ۴۶: هش کردن امن رمز عبور با Bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """تسک ۴۶: بررسی تطابق پسورد خام با هش دیتابیس"""
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )

    @classmethod
    def create_access_token(
        cls,
        user_id: int,
        username: str,
        role: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """تسک ۴۷: تولید توکن JWT حاوی user_id, username و role"""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode: Dict[str, Any] = {
            "sub": username,
            "user_id": user_id,
            "role": role,
            "exp": expire,
            "iat": datetime.now(timezone.utc)
        }

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt


# تسک ۴۸ و ۴۹: تابع استخراج مشخصات کاربر و پرتاب ارور ۴۰۱
async def get_current_user_role(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """استخراج و بررسی توکن از هدر Authorization"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="توکن احراز هویت نامعتبر یا منقضی شده است.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        role: Optional[str] = payload.get("role")
        user_id: Optional[int] = payload.get("user_id")

        if username is None or role is None or user_id is None:
            raise credentials_exception

        return {
            "user_id": user_id,
            "username": username,
            "role": role
        }
    except JWTError:
        raise credentials_exception


# تسک ۵۰، ۵۱ و ۵۵: کنترلر سطوح دسترسی مبتنی بر نقش (RoleChecker)
class RoleChecker:
    """
    تسک ۵۱: بررسی لیست نقش‌های مجاز (Allowed Roles)
    تسک ۵۵: بازگرداندن خطای ۴۰۳ (Forbidden) در صورت عدم تطابق نقش
    """
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: Dict[str, Any] = Depends(get_current_user_role)) -> Dict[str, Any]:
        user_role = current_user.get("role")
        
        # تسک ۵۲: دسترسی کامل ادمین سیستم به تمامی بخش‌ها
        if user_role == "Admin":
            return current_user

        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="شما سطح دسترسی لازم برای انجام این عملیات را ندارید."
            )
        return current_user


# تسک ۵۲، ۵۳، ۵۴: تعاریف آماده گاردهای امنیتی سیستم
require_admin = RoleChecker(["Admin"])
require_hr_or_admin = RoleChecker(["Admin", "HR Manager"])
require_tech_or_admin = RoleChecker(["Admin", "Tech Lead"])
require_candidate_or_admin = RoleChecker(["Admin", "Candidate"])