# راهنمای راه‌اندازی پروژه در PyCharm

## پیش‌نیازها

قبل از شروع، مطمئن شوید که نرم‌افزارهای زیر نصب شده‌اند:

### 1. Python (نسخه 3.8 یا بالاتر)
- دانلود از: [python.org](https://www.python.org/downloads/)
- بررسی نسخه: `python --version`

### 2. PostgreSQL (پایگاه داده)
- دانلود از: [postgresql.org](https://www.postgresql.org/download/)
- نسخه پیشنهادی: 14 یا بالاتر
- پس از نصب:
  - سرویس PostgreSQL را اجرا کنید
  - یک دیتابیس جدید بسازید (مثلاً: `international_trade`)
  - نام کاربری و رمز عبور را یادداشت کنید

### 3. Redis (برای Celery و Caching)
#### ویندوز:
- دانلود از: [GitHub Memurai](https://github.com/memurai/memurai) (جایگزین Redis برای ویندوز)
- یا استفاده از Docker: `docker run -d -p 6379:6379 redis:latest`

#### مک و لینوکس:
```bash
# مک
brew install redis

# لینوکس (Ubuntu/Debian)
sudo apt-get install redis-server
```

### 4. Git
- دانلود از: [git-scm.com](https://git-scm.com/downloads)

---

## مراحل راه‌اندازی در PyCharm

### مرحله 1: باز کردن پروژه
1. PyCharm را باز کنید
2. به منوی `File` → `Open` بروید
3. پوشه پروژه را انتخاب کنید

### مرحله 2: ساخت محیط مجازی (Virtual Environment)
1. به منوی `File` → `Settings` → `Project: <project_name>` → `Python Interpreter` بروید
2. روی آیکون چرخ‌دنده ⚙️ کلیک کنید
3. گزینه `Add...` را انتخاب کنید
4. `Virtualenv Environment` → `New environment` را انتخاب کنید
5. مسیر دلخواه را مشخص کنید (پیشنهاد: `.venv` در پوشه پروژه)
6. Python 3.8+ را انتخاب و OK کنید

### مرحله 3: نصب وابستگی‌ها
ترمینال PyCharm را باز کنید و دستورات زیر را اجرا کنید:

```bash
# فعال‌سازی virtualenv (در صورت نیاز)
# ویندوز:
.venv\Scripts\activate

# مک/لینوکس:
source .venv/bin/activate

# نصب تمام کتابخانه‌ها
pip install -r requirements.txt
```

### مرحله 4: تنظیم متغیرهای محیطی (.env)
یک فایل به نام `.env` در ریشه پروژه بسازید و مقادیر زیر را در آن قرار دهید:

```env
# تنظیمات اصلی
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-change-in-production

# پایگاه داده PostgreSQL
DATABASE_URL=postgresql://username:password@localhost:5432/international_trade

# Redis
REDIS_URL=redis://localhost:6379/0

# تنظیمات ایمیل (SMTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Kavenegar (پیامک)
KAVENEGAR_API_KEY=your-kavenegar-api-key

# سایر تنظیمات
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

**نکته مهم:** 
- `SECRET_KEY` باید یک رشته تصادفی و منحصر به فرد باشد
- برای تولید SECRET_KEY می‌توانید از این کد استفاده کنید:
```python
import secrets
print(secrets.token_hex(32))
```

### مرحله 5: پیکربندی Database در PyCharm
1. به منوی `View` → `Tool Windows` → `Database` بروید
2. روی `+` کلیک کرده و `Data Source` → `PostgreSQL` را انتخاب کنید
3. اطلاعات اتصال را وارد کنید:
   - Host: `localhost`
   - Port: `5432`
   - Database: `international_trade`
   - User: `postgres` (یا نام کاربری شما)
   - Password: رمز عبور شما
4. دکمه `Test Connection` را بزنید تا از صحت اتصال مطمئن شوید

### مرحله 6: اجرای Migration (ساخت جداول)
در ترمینال PyCharm دستورات زیر را اجرا کنید:

```bash
# فعال‌سازی virtualenv (اگر قبلاً فعال نکرده‌اید)
# ویندوز: .venv\Scripts\activate
# مک/لینوکس: source .venv/bin/activate

# ایجاد migration اولیه
flask db init

# ایجاد migration برای مدل‌های موجود
flask db migrate -m "Initial migration"

# اعمال migration روی دیتابیس
flask db upgrade
```

**نکته:** اگر خطایی دریافت کردید، مطمئن شوید که:
- PostgreSQL در حال اجراست
- DATABASE_URL در فایل .env صحیح است
- دیتابیس ساخته شده است

### مرحله 7: پیکربندی Run Configuration
1. به منوی `Run` → `Edit Configurations` بروید
2. روی `+` کلیک کرده و `Flask Server` را انتخاب کنید
3. تنظیمات زیر را انجام دهید:
   - Name: `Flask App`
   - Module name: `app`
   - FLASK_APP: `app.py`
   - FLASK_ENV: `development`
   - Environment variables: `FLASK_APP=app.py;FLASK_ENV=development`
4. OK را بزنید

### مرحله 8: اجرای برنامه
1. روی دکمه سبز رنگ ▶️ در کنار Run Configuration کلیک کنید
2. برنامه در آدرس `http://127.0.0.1:5000` اجرا می‌شود

---

## اجرای Celery Workers (برای پردازش‌های پس‌زمینه)

### در ویندوز:
```bash
celery -A celery_app worker --loglevel=info --pool=solo
```

### در مک/لینوکس:
```bash
celery -A celery_app worker --loglevel=info
```

**نکته:** این دستور را در یک ترمینال جداگانه اجرا کنید.

### اجرای Flower (مانیتورینگ Celery):
```bash
celery -A celery_app flower
```
سپس به آدرس `http://localhost:5555` مراجعه کنید.

---

## عیب‌یابی مشکلات رایج

### مشکل 1: خطای اتصال به PostgreSQL
```
sqlalchemy.exc.OperationalError: could not connect to server
```
**راه حل:**
- مطمئن شوید سرویس PostgreSQL در حال اجراست
- بررسی کنید DATABASE_URL در .env صحیح است
- نام کاربری و رمز عبور را بررسی کنید

### مشکل 2: خطای Redis
```
redis.exceptions.ConnectionError: Error connecting to localhost:6379
```
**راه حل:**
- Redis را اجرا کنید
- در ویندوز از Docker استفاده کنید: `docker run -d -p 6379:6379 redis:latest`

### مشکل 3: خطای Flask-Migrate
```
Error: No such command 'db'
```
**راه حل:**
- مطمئن شوید Flask-Migrate نصب شده: `pip install -r requirements.txt`
- در app.py از `Migrate(app, db)` استفاده شده باشد

### مشکل 4: خطای ImportError
```
ModuleNotFoundError: No module named '...'
```
**راه حل:**
- مطمئن شوید interpreter صحیح در PyCharm انتخاب شده
- به Settings → Project → Python Interpreter بروید
- interpreter مربوط به .venv را انتخاب کنید

---

## ساختار پروژه

```
/workspace
├── app.py                 # فایل اصلی برنامه
├── config.py              # تنظیمات پیکربندی
├── extensions.py          # افزونه‌های Flask
├── celery_app.py          # تنظیمات Celery
├── requirements.txt       # وابستگی‌های پروژه
├── .env                   # متغیرهای محیطی (بسازید)
├── models/                # مدل‌های دیتابیس
├── routes/                # مسیرهای API
├── templates/             # قالب‌های HTML
├── static/                # فایل‌های استاتیک
└── migrations/            # فایل‌های migration
```

---

## نکات امنیتی

1. **هرگز** فایل `.env` را در Git commit نکنید
2. در `.gitignore` مطمئن شوید موارد زیر وجود دارند:
   ```
   .env
   .venv/
   __pycache__/
   *.pyc
   uploads/
   instance/
   ```
3. برای production حتماً:
   - SECRET_KEY قوی و تصادفی استفاده کنید
   - DEBUG=False تنظیم کنید
   - از HTTPS استفاده کنید

---

## منابع بیشتر

- [مستندات Flask](https://flask.palletsprojects.com/)
- [مستندات SQLAlchemy](https://docs.sqlalchemy.org/)
- [مستندات Celery](https://docs.celeryq.dev/)
- [مستندات Flask-Migrate](https://flask-migrate.readthedocs.io/)

---

## پشتیبانی

در صورت بروز هرگونه مشکل:
1. لاگ‌های PyCharm را بررسی کنید
2. فایل `.env` را دوباره بررسی کنید
3. مطمئن شوید تمام پیش‌نیازها نصب شده‌اند
4. نسخه Python باید 3.8 تا 3.11 باشد
