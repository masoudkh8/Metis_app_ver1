# راهنمای کامل راه‌اندازی شبکه اجتماعی متیسما

## 📋 فهرست مطالب
1. [معرفی](#معرفی)
2. [زیرساخت‌های فنی](#زیرساختهای-فنی)
3. [راه‌اندازی اولیه](#راه‌اندازی-اولیه)
4. [سیستم اعلان‌ها](#سیستم-اعلانها)
5. [سیستم اشتراک‌گذاری](#سیستم-اشتراکگذاری)
6. [الگوریتم فید](#الگوریتم-فید)
7. [دستورات Celery](#دستورات-celery)
8. [داده‌های اولیه (Seed)](#داده‌های-اولیه-seed)
9. [تنظیمات امنیتی](#تنظیمات-امنیتی)
10. [عیب‌یابی](#عیب‌یابی)

---

## معرفی

بخش شبکه اجتماعی پلتفرم متیسما شامل قابلیت‌های زیر است:

- ✅ پروفایل عمومی کاربران
- ✅ سیستم فالو/آنفالو
- ✅ فید اخبار شخصی‌سازی شده
- ✅ ایجاد و مدیریت پست‌ها
- ✅ لایک و کامنت (با پشتیبانی از پاسخ به کامنت‌ها)
- ✅ اشتراک‌گذاری پست‌ها
- ✅ اعلان‌های لحظه‌ای (Real-time Notifications)
- ✅ الگوریتم فید مبتنی بر TrustScore

---

## زیرساخت‌های فنی

### ۱. Flask-SocketIO (برای اعلان‌های لحظه‌ای)
```bash
pip install Flask-SocketIO==5.3.6 python-engineio==4.9.1 python-socketio==5.11.0
```

**کاربرد:** ارسال اعلان‌ها به صورت Push Notification درون برنامه‌ای

### ۲. Celery + Redis (برای پردازش پس‌زمینه)
```bash
# Celery و Redis قبلاً در requirements.txt هستند
celery==5.4.0
redis==5.2.1
```

**کاربرد:** 
- ارسال اعلان‌ها به صورت ناهمگام
- پردازش محاسبات سنگین فید
- تسک‌های زمان‌بندی شده

### ۳. PostgreSQL (پایگاه داده)
```bash
# اطمینان حاصل کنید DATABASE_URL تنظیم شده باشد
export DATABASE_URL="postgresql://user:password@localhost:5432/metisma_db"
```

---

## راه‌اندازی اولیه

### مرحله ۱: نصب وابستگی‌ها
```bash
pip install -r requirements.txt
```

### مرحله ۲: تنظیم Redis
```bash
# نصب Redis (Ubuntu/Debian)
sudo apt-get install redis-server

# شروع سرویس Redis
sudo systemctl start redis
sudo systemctl enable redis

# تست Redis
redis-cli ping
# باید PONG برگرداند
```

### مرحله ۳: تنظیم متغیرهای محیطی
```bash
# فایل .env را ایجاد یا ویرایش کنید
cat >> .env << EOL

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CACHE_REDIS_URL=redis://localhost:6379/0
RATELIMIT_STORAGE_URL=redis://localhost:6379/1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/metisma_db
EOL
```

### مرحله ۴: مهاجرت دیتابیس
```bash
# ایجاد جداول جدید
flask db migrate -m "Add social network features"
flask db upgrade
```

---

## سیستم اعلان‌ها

### انواع اعلان‌ها
| نوع | توضیح | کلید ترجمه |
|-----|-------|-----------|
| `follow` | دنبال کردن کاربر | `social.new_follower_notification` |
| `like` | لایک پست/کامنت | `social.new_like_notification` |
| `comment` | نظر روی پست | `social.new_comment_notification` |
| `comment_reply` | پاسخ به کامنت | `social.new_reply_notification` |
| `share` | اشتراک‌گذاری پست | `social.new_share_notification` |

### نحوه کار
1. **ذخیره در دیتابیس:** تمام اعلان‌ها در جدول `notifications` ذخیره می‌شوند
2. **ارسال لحظه‌ای:** از طریق WebSocket به کاربر متصل ارسال می‌شود
3. **صفحه اعلان‌ها:** کاربر می‌تواند از `/social/notifications` مشاهده کند

### کلیدهای SocketIO برای فرانت‌اند
```javascript
// اتصال به WebSocket
const socket = io();

// دریافت اعلان جدید
socket.on('new_notification', (data) => {
    console.log('New notification:', data);
    // نمایش notification در UI
});

// دریافت تعداد اعلان‌های خوانده نشده
socket.on('unread_count', (data) => {
    console.log('Unread count:', data.count);
    // بروزرسانی badge
});

// علامت‌گذاری به عنوان خوانده شده
socket.emit('mark_notification_read', {
    notification_id: 123
});

// علامت‌گذاری همه به عنوان خوانده شده
socket.emit('mark_all_read', {});
```

---

## سیستم اشتراک‌گذاری

### انواع اشتراک‌گذاری
1. **اشتراک در فید:** پست در فید کاربر کپی می‌شود
2. **کپی لینک:** لینک پست کپی می‌شود
3. **اشتراک خارجی:** Telegram, WhatsApp, LinkedIn, Twitter

### API Endpoint
```http
POST /social/post/<post_id>/share
Content-Type: application/x-www-form-urlencoded

share_type=feed&platform=telegram
```

### پارامترها
| پارامتر | مقدار پیش‌فرض | توضیح |
|---------|--------------|-------|
| `share_type` | `feed` | `feed`, `copy_link`, `external` |
| `platform` | - | `telegram`, `whatsapp`, `linkedin`, `twitter` |

---

## الگوریتم فید

### فرمول امتیازدهی
```python
score = TrustScore_نویسنده + (تعداد_لایک * 2) + (تعداد_کامنت * 3)
```

### عوامل موثر
1. **TrustScore نویسنده:** اعتبار کاربر تولیدکننده محتوا
2. **تعاملات:** لایک و کامنت‌های دریافتی
3. **زمان انتشار:** پست‌های جدیدتر اولویت بالاتری دارند
4. **رابطه فالو:** پست‌های کاربران فالوشده اولویت دارند

### بهینه‌سازی
```bash
# اجرای تسک محاسبه امتیاز فید برای هر کاربر
celery -A celery_app worker --loglevel=info

# یا اجرای دوره‌ای با Celery Beat
celery -A celery_app beat --loglevel=info
```

---

## دستورات Celery

### شروع Worker
```bash
# Worker ساده
celery -A celery_app worker --loglevel=info

# Worker با concurrency بالا
celery -A celery_app worker --loglevel=info --concurrency=4

# Worker با eventlet (برای I/O bound tasks)
celery -A celery_app worker --loglevel=info --pool=eventlet
```

### شروع Scheduler (Beat)
```bash
# Celery Beat برای تسک‌های زمان‌بندی شده
celery -A celery_app beat --loglevel=info
```

### مانیتورینگ با Flower
```bash
# نصب Flower
pip install flower

# شروع Flower
celery -A celery_app flower --port=5555
```
دسترسی به داشبورد: http://localhost:5555

### تسک‌های موجود
| تسک | توضیح | فراخوانی |
|-----|-------|----------|
| `send_notification_task` | ارسال اعلان ناهمگام | `.delay(user_id, data)` |
| `cleanup_old_notifications` | پاکسازی اعلان‌های قدیمی | `.delay(days_old=30)` |
| `calculate_feed_score_for_user` | محاسبه امتیاز فید | `.delay(user_id)` |
| `send_email_task` | ارسال ایمیل | `.delay(recipient, subject, body)` |
| `send_sms_task` | ارسال پیامک | `.delay(phone_number, message)` |

---

## داده‌های اولیه (Seed)

### اهمیت Seed Data
برای کارکرد صحیح الگوریتم فید و نمایش محتوای نمونه، نیاز به داده‌های اولیه دارید:

### اجرای اسکریپت Seed
```bash
# اجرای seed برای بخش exhibition trading
python scripts/seed_exhibition_trading.py

# ایجاد کاربران نمونه (اگر وجود ندارد)
flask shell
>>> from models import User, db
>>> user = User(username='test_user', phone='09123456789')
>>> db.session.add(user)
>>> db.session.commit()
```

### محتوای پیشنهادی برای Seed
1. **حداقل ۱۰ کاربر فعال** با TrustScore متفاوت
2. **حداقل ۵۰ پست** با موضوعات مختلف
3. **رابطه‌های فالو** بین کاربران
4. **کامنت و لایک** برای شبیه‌سازی تعاملات

### نمونه کوئری برای بررسی
```sql
-- بررسی تعداد پست‌ها
SELECT COUNT(*) FROM posts;

-- بررسی رابطه‌های فالو
SELECT COUNT(*) FROM follows;

-- بررسی اعلان‌ها
SELECT notification_type, COUNT(*) FROM notifications GROUP BY notification_type;
```

---

## تنظیمات امنیتی

### ۱. محدودیت‌های دسترسی (Rate Limiting)
```python
# در routes/social/routes.py اعمال شده است
@limiter.limit("30 per minute")  # برای کاربران عادی
@limiter.limit("100 per minute")  # برای کاربران احراز هویت شده
```

### ۲. محافظت CSRF
```python
# در فرم‌ها حتماً از توکن CSRF استفاده کنید
<form method="POST">
    {{ form.hidden_tag() }}
    <!-- فیلدهای فرم -->
</form>
```

### ۳. اعتبارسنجی ورودی‌ها
```python
# همیشه ورودی‌ها را اعتبارسنجی کنید
content = request.form.get('content', '').strip()
if not content or len(content) > 5000:
    flash('محتوا نامعتبر است', 'error')
    return redirect(...)
```

### ۴. مجوزهای دسترسی
```python
# فقط نویسنده یا ادمین می‌تواند پست را حذف کند
if post.author_id != current_user.id and not current_user.is_admin_or_moderator:
    flash(t_('messages.access_denied'), 'error')
    return redirect(...)
```

### ۵. محافظت در برابر XSS
```html
<!-- در قالب‌ها از escape خودکار Jinja2 استفاده کنید -->
{{ post.content }}  <!-- خودکار escape می‌شود -->
{{ post.content|safe }}  <!-- فقط اگر مطمئن هستید استفاده کنید -->
```

---

## عیب‌یابی

### مشکل: اعلان‌های لحظه‌ای کار نمی‌کنند
```bash
# بررسی وضعیت Redis
redis-cli ping

# بررسی لاگ‌های SocketIO
tail -f logs/app.log | grep socketio

# اطمینان از اتصال کلاینت به WebSocket
# در کنسول مرورگر:
console.log(socket.connected);  # باید true باشد
```

### مشکل: Celery Tasks اجرا نمی‌شوند
```bash
# بررسی وضعیت Worker
celery -A celery_app inspect active

# بررسی لاگ‌های Celery
tail -f logs/celery.log

# تست یک تسک ساده
celery -A celery_app call tasks.social_notifications.cleanup_old_notifications --args='[30]'
```

### مشکل: خطای Migration
```bash
# حذف migration‌های مشکل‌ساز
rm migrations/versions/<problematic_file>.py

# ایجاد migration جدید
flask db migrate -m "Fix social tables"
flask db upgrade
```

### مشکل: TrustScore صفر است
```bash
# بررسی ستون trust_score در دیتابیس
psql -d metisma_db -c "SELECT id, username, trust_score FROM user LIMIT 10;"

# بروزرسانی TrustScore
flask shell
>>> from models import User, db
>>> for user in User.query.all():
...     user.trust_score = 50  # مقدار پیش‌فرض
>>> db.session.commit()
```

---

## چک‌لیست نهایی قبل از Production

- [ ] Redis نصب و پیکربندی شده است
- [ ] Celery Worker در حال اجرا است
- [ ] Celery Beat برای تسک‌های زمان‌بندی شده فعال است
- [ ] Flask-SocketIO با Eventlet/Gevent پیکربندی شده
- [ ] متغیر `DATABASE_URL` به PostgreSQL اشاره می‌کند
- [ ] داده‌های Seed اجرا شده‌اند
- [ ] Rate Limiting فعال است
- [ ] SSL/TLS برای WebSocket پیکربندی شده
- [ ] CORS برای SocketIO محدود شده است
- [ ] لاگ‌گیری و مانیتورینگ فعال است

---

## منابع اضافی

- [مستندات Flask-SocketIO](https://flask-socketio.readthedocs.io/)
- [مستندات Celery](https://docs.celeryq.dev/)
- [مستندات Redis](https://redis.io/documentation)

---

**تهیه شده توسط تیم توسعه متیسما**  
**آخرین بروزرسانی:** 2024
