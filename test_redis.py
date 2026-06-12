
import redis

try:
    r = redis.Redis(host='localhost', port=6379, db=0)
    print("در حال تست اتصال به Redis...")
    print("پاسخ Redis:", r.ping())  # باید True برگرداند
except Exception as e:
    print("اتصال به Redis شکست خورد:", e)
