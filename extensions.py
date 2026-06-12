# extensions.py
import os
import redis
from flask import request
from flask_mail import Mail
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
import logging

# تعریف اشیاء سراسری
mail = Mail()
cache = Cache()
db = SQLAlchemy()
babel = Babel()

# دریافت آدرس Redis از متغیرهای محیطی
# REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
# RATELIMIT_STORAGE_URL = os.environ.get("RATELIMIT_STORAGE_URL", "redis://redis:6379/1")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
RATELIMIT_STORAGE_URL = os.environ.get("RATELIMIT_STORAGE_URL", "redis://localhost:6379/1")
# اتصال به Redis برای مسدودسازی IP و ذخیره آمار
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    # تست اتصال
    redis_client.ping()
    logging.info("[SUCCESS] Redis connection successful")
except Exception as e:
    logging.error(f"[ERROR] Redis connection failed: {e}")
    redis_client = None


def get_remote_address_safe():
    """
    دریافت IP واقعی کاربر با در نظر گرفتن Reverse Proxy (Nginx/Cloudflare)
    این تابع اول X-Forwarded-For را چک می‌کند، اگر نبود از IP مستقیم استفاده می‌کند
    """
    # چک کردن هدرهای مختلف که ممکن است توسط Proxy تنظیم شده باشند
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For ممکن است چند IP داشته باشد (زنجیره‌ای)
        # اولین IP، IP واقعی کاربر است
        return forwarded_for.split(",")[0].strip()

    # اگر Cloudflare استفاده می‌کنید
    cf_connecting_ip = request.headers.get("CF-Connecting-IP")
    if cf_connecting_ip:
        return cf_connecting_ip

    # در نهایت از IP مستقیم استفاده کن
    return request.remote_addr or "unknown"


# تعریف Limiter با تنظیمات صحیح
limiter = Limiter(
    key_func=get_remote_address_safe,  # استفاده از تابع امن
    default_limits=[
        "50 per hour",  # محدودیت پیش‌فرض: 100 درخواست در ساعت
        "200 per day"  # محدودیت روزانه: 1000 درخواست در روز
    ],
    storage_uri=RATELIMIT_STORAGE_URL,  # ✅ استفاده از Redis به جای memory
    strategy="moving-window",  # استراتژی پنجره متحرک (دقیق‌تر)
    headers_enabled=True,  # ارسال هدرهای X-RateLimit به کلاینت
    swallow_errors=False,  # اگر Redis قطع شد، خطا بده (برای دیباگ)
)
# --- ۲. تابع امن برای گرفتن IP واقعی (بسیار مهم!) ---
def get_client_ip():
    """
    IP واقعی کاربر را حتی در صورت وجود Proxy یا Load Balancer برمی‌گرداند.
    """
    # اولویت با هدرهایی است که پروکسی‌ها ست می‌کنند
    if request.headers.get("X-Forwarded-For"):
        # X-Forwarded-For لیستی از IPهاست، اولی IP واقعی کاربر است
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()
    elif request.headers.get("X-Real-IP"):
        return request.headers.get("X-Real-IP")
    # در غیر این صورت IP مستقیم را برمی‌گردانیم
    return request.remote_addr

