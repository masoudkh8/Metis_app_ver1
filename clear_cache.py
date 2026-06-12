import redis

try:
    # اتصال به سرور ردیس لوکال شما
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    # پاک کردن کامل دیتابیس فعلی (شامل تمام کلیدهای blocked_ip و violations)
    r.flushdb()

    print("✅ کش ردیس با موفقیت پاک شد! حالا می‌توانید وارد سایت شوید.")
except redis.exceptions.ConnectionError:
    print("❌ خطا: سرور ردیس روی پورت 6379 در حال اجرا نیست. لطفاً سرویس ردیس ویندوز را استارت کنید.")