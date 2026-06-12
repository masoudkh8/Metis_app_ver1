from flask import current_app
import redis

# اتصال به Redis (در تولید، آدرس سرور Redis واقعی را بگذارید)
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


def increment_post_views_async(post_id):
    """
    افزایش بازدید پست در Redis و Sync دوره‌ای با دیتابیس
    """
    key = f'post:{post_id}:views'
    redis_client.incr(key)
    # تنظیم انقضا برای جلوگیری از انباشت کلیدهای بی‌استفاده (مثلاً ۷ روز)
    redis_client.expire(key, 604800)


def get_post_views(post_id):
    """
    دریافت تعداد بازدید (ترکیب Redis + دیتابیس)
    """
    key = f'post:{post_id}:views'
    redis_views = redis_client.get(key)

    if redis_views:
        return int(redis_views)

    # اگر در کش نبود، از دیتابیس بخوان
    from models.social import Post
    post = Post.query.get(post_id)
    return post.views_count if post else 0


def sync_views_to_db():
    """
    این تابع باید توسط Celery Beat هر ۵ دقیقه اجرا شود
    تا مقادیر Redis را در دیتابیس ذخیره کند.
    """
    # مثال ساده: پیدا کردن تمام کلیدهای views و به‌روزرسانی دیتابیس
    # (پیاده‌سازی کامل این بخش بستگی به تنظیمات Celery شما دارد)
    pass