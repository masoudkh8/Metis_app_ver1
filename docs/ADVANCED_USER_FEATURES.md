# 🚀 مستندات ویژگی‌های پیشرفته کاربران - Advanced User Features Documentation

## 📋 فهرست مطالب

1. [بررسی کلی](#بررسی-کلی)
2. [مدل کاربر پیشرفته](#مدل-کاربر-پیشرفته)
3. [سیستم ثبت‌نام چندمرحله‌ای](#سیستم-ثبت‌نام-چندمرحله‌ای)
4. [داشبورد هوشمند نقش‌محور](#داشبورد-هوشمند-نقش‌محور)
5. [پروفایل کاربری پیشرفته](#پروفایل-کاربری-پیشرفته)
6. [امنیت و کنترل دسترسی](#امنیت-و-کنترل-دسترسی)
7. [آپلود امن مدارک](#آپلود-امن-مدارک)
8. [سیستم امتیاز اعتماد](#سیستم-امتیاز-اعتماد)
9. [ترجمه و چندزبانه](#ترجمه-و-چندزبانه)
10. [API Endpoints](#api-endpoints)

---

## بررسی کلی

این مستندات ویژگی‌های پیشرفته مدیریت کاربران در پلتفرم هوشمند تجارت بین‌المللی Metisma را تشریح می‌کند. این ویژگی‌ها شامل:

- ✅ **مدل کاربر غنی‌شده** با فیلدهای تخصصی بر اساس نقش
- ✅ **ثبت‌نام هوشمند ۳ مرحله‌ای** با اعتبارسنجی پیشرفته
- ✅ **داشبورد نقش‌محور** با ویجت‌های سفارشی
- ✅ **پروفایل پیشرفته** با قابلیت ویرایش و آپلود مدارک
- ✅ **کنترل دسترسی مبتنی بر نقش (RBAC)**
- ✅ **Rate Limiting** برای محافظت در برابر سوءاستفاده
- ✅ **آپلود امن فایل** با اعتبارسنجی چندلایه
- ✅ **سیستم امتیاز اعتماد (Trust Score)**

---

## مدل کاربر پیشرفته

### ساختار مدل `User`

مدل کاربر در `models/user.py` با فیلدهای زیر توسعه یافته است:

#### فیلدهای پایه
| فیلد | نوع | توضیحات |
|------|-----|---------|
| `id` | Integer | کلید اصلی |
| `username` | String(80) | نام کاربری یکتا |
| `email` | String(120) | ایمیل یکتا |
| `phone` | String(20) | شماره تلفن |
| `password_hash` | String(256) | هش رمز عبور |
| `role` | Enum | نقش کاربر (PRODUCER, BUYER, INVESTOR, etc.) |
| `is_verified` | Boolean | وضعیت تأیید هویت |
| `is_active` | Boolean | وضعیت فعال بودن |
| `created_at` | DateTime | تاریخ ایجاد |

#### فیلدهای تخصصی (Professional Fields)
| فیلد | نوع | توضیحات |
|------|-----|---------|
| `expertise_area` | String(100) | حوزه تخصصی (برای متخصصین) |
| `company_name` | String(200) | نام شرکت |
| `job_title` | String(100) | عنوان شغلی |
| `bio` | Text | بیوگرافی و درباره من |
| `website` | String(255) | وب‌سایت شخصی/شرکتی |
| `social_links` | JSON | لینک‌های شبکه‌های اجتماعی |

#### سیستم اعتماد
| فیلد | نوع | توضیحات |
|------|-----|---------|
| `trust_score_value` | Integer | امتیاز اعتماد (0-100) |
| `verification_documents` | JSON | مدارک بارگذاری‌شده برای تأیید |

#### متدهای مهم
```python
# تبدیل به دیکشنری
user.to_dict()

# محاسبه امتیاز اعتماد
user.calculate_trust_score()

# بررسی نقش
user.has_role('PRODUCER')

# دریافت لینک‌های اجتماعی
user.get_social_links()
```

### نقش‌های کاربری (Role Enum)

```python
class Role(Enum):
    PRODUCER = 'producer'         # تولیدکننده
    BUYER = 'buyer'               # خریدار
    INVESTOR = 'investor'         # سرمایه‌گذار
    EXPERT = 'expert'             # متخصص
    EXHIBITOR = 'exhibitor'       # نمایشگاه‌دار
    TRADER = 'trader'             # تاجر
    LOGISTICS_PROVIDER = 'logistics_provider'  # ارائه‌دهنده لجستیک
    INSURANCE_PROVIDER = 'insurance_provider'  # ارائه‌دهنده بیمه
    ADMIN = 'admin'               # مدیر سیستم
```

---

## سیستم ثبت‌نام چندمرحله‌ای

### فرآیند ۳ مرحله‌ای

#### مرحله ۱: اطلاعات پایه
- انتخاب نقش کاربری
- نام کاربری
- ایمیل
- رمز عبور (با اعتبارسنجی قدرت)
- پذیرش قوانین

#### مرحله ۲: اطلاعات تماس
- شماره تلفن
- کد کشور
- تأییدیه SMS/Email (اختیاری)

#### مرحله ۳: اطلاعات تخصصی (بر اساس نقش)
- **برای PRODUCER/EXHIBITOR**: 
  - نام شرکت
  - حوزه تخصصی
  - وب‌سایت
- **برای EXPERT**:
  - عنوان شغلی
  - حوزه تخصصی
  - بیوگرافی
- **برای INVESTOR**:
  - نوع سرمایه‌گذاری
  - حوزه‌های مورد علاقه

### اعتبارسنجی رمز عبور

رمز عبور باید شرایط زیر را داشته باشد:
- حداقل ۸ کاراکتر
- شامل حروف بزرگ و کوچک
- شامل اعداد
- شامل کاراکترهای خاص (!@#$%^&*)

```python
def validate_password_strength(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain a number"
    if not re.search(r"[!@#$%^&*]", password):
        return False, "Password must contain special character"
    return True, "Password is strong"
```

### Rate Limiting روی ثبت‌نام

برای جلوگیری از سوءاستفاده، محدودیت نرخ اعمال شده است:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(app, key_func=get_remote_address)

@users_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    # منطق ثبت‌نام
    pass
```

**محدودیت‌ها:**
- ۵ درخواست در دقیقه از هر IP
- ۲۰ درخواست در ساعت از هر IP
- پیام خطای واضح هنگام تجاوز از محدودیت

### امتیاز اعتماد اولیه

تمام کاربران جدید با `trust_score_value = 50` شروع می‌کنند. این امتیاز بر اساس فعالیت‌های بعدی افزایش یا کاهش می‌یابد.

---

## داشبورد هوشمند نقش‌محور

### ویجت‌های اختصاصی بر اساس نقش

#### 🏭 تولیدکننده (PRODUCER)
- 📊 نمودار محصولات ثبت‌شده
- 📦 وضعیت سفارشات فعال
- 💰 درآمد ماهانه
- 🔔 درخواست‌های RFQ جدید
- ⭐ میانگین امتیاز اعتماد

#### 💼 سرمایه‌گذار (INVESTOR)
- 📈 فرصت‌های سرمایه‌گذاری پیشنهادی
- 💵 پرتفوی سرمایه‌گذاری
- 📊 بازدهی سرمایه‌گذاری‌ها
- 🔍 پروژه‌های کنسرسیومی فعال
- 📅 رویدادهای پیش‌رو

#### 🎨 نمایشگاه‌دار (EXHIBITOR)
- 👥 بازدیدکنندگان غرفه
- 💬 تعاملات با بازدیدکنندگان
- 📊 آمار بازدید از محصولات
- 🎫 بلیط‌های فروخته‌شده
- 📅 رویدادهای برنامه‌ریزی‌شده

#### 🔬 متخصص (EXPERT)
- 📝 مشاوره‌های فعال
- ⭐ امتیاز رضایت مشتریان
- 💰 درآمد از مشاوره
- 📚 مقالات منتشرشده
- 🎓 دوره‌های آموزشی

### نمودارهای تعاملی (Chart.js)

تمام داشبوردها از Chart.js برای نمایش داده‌ها استفاده می‌کنند:

```html
<canvas id="revenueChart"></canvas>
<script>
const ctx = document.getElementById('revenueChart');
new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
        datasets: [{
            label: 'Revenue',
            data: [1200, 1900, 3000, 5000, 2300],
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
        }]
    }
});
</script>
```

### لیست کارهای Pending

هر نقش لیست کارهای مخصوص به خود را دارد:

**تولیدکننده:**
- ⏳ تأیید مدارک شرکت
- ⏳ بررسی سفارشات جدید
- ⏳ پاسخ به RFQها

**سرمایه‌گذار:**
- ⏳ تکمیل پروفایل سرمایه‌گذاری
- ⏳ بررسی فرصت‌های پیشنهادی
- ⏳ امضای قراردادها

---

## پروفایل کاربری پیشرفته

### بخش‌های پروفایل

#### ۱. اطلاعات پایه (Basic Information)
- نام کاربری (غیرقابل تغییر)
- ایمیل (با تأیید مجدد)
- شماره تلفن
- عکس پروفایل

#### ۲. اطلاعات حرفه‌ای (Professional Information)
- نام شرکت
- عنوان شغلی
- حوزه تخصصی
- سال تأسیس شرکت (برای شرکت‌ها)
- تعداد کارکنان

#### ۳. درباره من (About Me)
- بیوگرافی متنی (حداکثر ۱۰۰۰ کاراکتر)
- مهارت‌های کلیدی (تگ‌ها)
- سوابق کاری

#### ۴. لینک‌های اجتماعی (Social Links)
- LinkedIn
- Twitter/X
- Instagram
- Facebook
- وب‌سایت شخصی/شرکتی

#### ۵. مدارک تأیید هویت (Verification Documents)
- کارت ملی/پاسپورت
- جواز کسب
- گواهی‌نامه‌های تخصصی
- سایر مدارک

### فرم ویرایش پروفایل

فرم ویرایش در `templates/users/profile_edit.html` شامل:

```html
<form method="POST" enctype="multipart/form-data">
    <!-- اطلاعات پایه -->
    <section id="basic-info">
        <input type="text" name="company_name" value="{{ user.company_name }}">
        <input type="text" name="job_title" value="{{ user.job_title }}">
        <textarea name="bio">{{ user.bio }}</textarea>
    </section>
    
    <!-- لینک‌های اجتماعی -->
    <section id="social-links">
        <input type="url" name="linkedin" value="{{ user.social_links.linkedin }}">
        <input type="url" name="twitter" value="{{ user.social_links.twitter }}">
    </section>
    
    <!-- آپلود مدارک -->
    <section id="documents">
        <input type="file" name="verification_doc" accept=".pdf,.jpg,.png">
    </section>
    
    <button type="submit">ذخیره تغییرات</button>
</form>
```

### نمایش عمومی پروفایل

پروفایل عمومی کاربران در `/profile/<username>` قابل مشاهده است و شامل:

- ✅ عکس پروفایل
- ✅ نام و عنوان شغلی
- ✅ نام شرکت
- ✅ بیوگرافی
- ✅ امتیاز اعتماد
- ✅ لینک‌های اجتماعی
- ✅ محصولات/خدمات (برای PRODUCER)
- ✅ نظرات و امتیازات

**طراحی ریسپانسیو:**
- Mobile-first approach
- سازگار با تمام دستگاه‌ها
- حالت تاریک (Dark Mode)

---

## امنیت و کنترل دسترسی

### دکوریتور @role_required

برای محدود کردن دسترسی به مسیرهای خاص بر اساس نقش:

```python
from functools import wraps
from flask import abort
from models.user import Role

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            
            if current_user.role not in roles:
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

### مثال استفاده

```python
@users_bp.route('/dashboard/producer')
@login_required
@role_required(Role.PRODUCER, Role.EXHIBITOR)
def producer_dashboard():
    return render_template('users/dashboard_producer.html')

@users_bp.route('/dashboard/investor')
@login_required
@role_required(Role.INVESTOR)
def investor_dashboard():
    return render_template('users/dashboard_investor.html')
```

### کدهای وضعیت HTTP

- `401 Unauthorized`: کاربر وارد نشده است
- `403 Forbidden`: کاربر اجازه دسترسی ندارد
- `404 Not Found`: مسیر وجود ندارد

---

## آپلود امن مدارک

### اعتبارسنجی چندلایه

#### ۱. اعتبارسنجی پسوند فایل
```python
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

#### ۲. اعتبارسنجی نوع MIME
```python
import magic

def validate_mime_type(file_stream):
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(file_stream.read(2048))
    allowed_mimes = [
        'application/pdf',
        'image/jpeg',
        'image/png'
    ]
    return file_type in allowed_mimes
```

#### ۳. محدودیت حجم فایل
```python
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def validate_file_size(file_stream):
    file_stream.seek(0, os.SEEK_END)
    size = file_stream.tell()
    file_stream.seek(0)
    return size <= MAX_FILE_SIZE
```

#### ۴. نام‌گذاری امن فایل
```python
import uuid
from werkzeug.utils import secure_filename

def generate_secure_filename(original_filename):
    ext = original_filename.rsplit('.', 1)[1].lower()
    unique_id = uuid.uuid4().hex
    return f"{unique_id}.{ext}"
```

### مسیر ذخیره‌سازی

```python
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads', 'verification_docs')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ذخیره فایل
filename = generate_secure_filename(file.filename)
file_path = os.path.join(UPLOAD_FOLDER, filename)
file.save(file_path)
```

### اسکن فایل‌های مخرب

در محیط Production توصیه می‌شود از ClamAV یا سرویس‌های مشابه برای اسکن فایل‌ها استفاده شود:

```python
import clamd

def scan_file_for_malware(file_path):
    cd = clamd.ClamdUnixSocket()
    result = cd.scan(file_path)
    return result['stream'][0] == 'OK'
```

---

## سیستم امتیاز اعتماد

### محاسبه امتیاز اولیه

تمام کاربران با `trust_score_value = 50` شروع می‌کنند.

### عوامل افزایش امتیاز

| عامل | امتیاز | توضیحات |
|------|--------|---------|
| تأیید ایمیل | +5 | پس از کلیک روی لینک تأیید |
| تأیید تلفن | +5 | پس از وارد کردن کد SMS |
| تکمیل پروفایل | +10 | پر کردن تمام فیلدهای پروفایل |
| آپلود مدارک | +15 | بارگذاری مدارک تأیید هویت |
| تأیید مدارک توسط ادمین | +20 | پس از بررسی و تأیید |
| اولین معامله موفق | +25 | تکمیل اولین سفارش |
| نظر مثبت از کاربر دیگر | +5 | هر نظر مثبت (حداکثر +50) |
| عضویت بیش از ۶ ماه | +10 | وفاداری به پلتفرم |
| تکمیل دوره آموزشی | +5 | هر دوره (حداکثر +20) |

### عوامل کاهش امتیاز

| عامل | امتیاز | توضیحات |
|------|--------|---------|
| لغو سفارش توسط کاربر | -10 | بدون دلیل موجه |
| نظر منفی از کاربر دیگر | -5 | هر نظر منفی |
| گزارش تخلف | -20 | پس از بررسی و تأیید |
| عدم فعالیت بیش از ۶ ماه | -10 | غیرفعال بودن طولانی |
| بازگشت چک/پرداخت | -30 | مشکلات مالی |

### سطوح اعتماد

| سطح | محدوده امتیاز | مزایا |
|-----|--------------|-------|
| 🟢 Bronze | 50-69 | دسترسی پایه |
| 🟡 Silver | 70-84 | دسترسی به RFQها |
| 🟠 Gold | 85-94 | نمایش ویژه در مارکت‌پلیس |
| 🟣 Platinum | 95-100 | پشتیبانی VIP، کارمزد کمتر |

### الگوریتم فید

امتیاز اعتماد در الگوریتم نمایش محتوا تأثیر دارد:

```python
def get_feed_content(user):
    # کاربران با trust_score بالاتر در اولویت نمایش هستند
    products = Product.query.order_by(
        Product.trust_score.desc(),
        Product.created_at.desc()
    ).limit(20)
    return products
```

---

## ترجمه و چندزبانه

### کلیدهای ترجمه جدید

بیش از ۵۰ کلید ترجمه جدید به فایل‌های `fa.json` و `en.json` اضافه شده است:

#### بخش ثبت‌نام
```json
{
  "user.register.step1": "مرحله ۱: اطلاعات پایه",
  "user.register.step2": "مرحله ۲: اطلاعات تماس",
  "user.register.step3": "مرحله ۳: اطلاعات تخصصی",
  "user.register.select_role": "نقش خود را انتخاب کنید",
  "user.register.password_strength": "قدرت رمز عبور",
  "user.register.terms_accept": "قوانین و مقررات را می‌پذیرم"
}
```

#### بخش پروفایل
```json
{
  "user.profile.basic_info": "اطلاعات پایه",
  "user.profile.professional_info": "اطلاعات حرفه‌ای",
  "user.profile.about_me": "درباره من",
  "user.profile.social_links": "لینک‌های اجتماعی",
  "user.profile.verification_docs": "مدارک تأیید هویت",
  "user.profile.edit": "ویرایش پروفایل",
  "user.profile.save_changes": "ذخیره تغییرات"
}
```

#### بخش اعتبارسنجی
```json
{
  "validation.email.required": "ایمیل الزامی است",
  "validation.email.invalid": "ایمیل نامعتبر است",
  "validation.password.weak": "رمز عبور ضعیف است",
  "validation.password.mismatch": "رمزهای عبور مطابقت ندارند",
  "validation.file.too_large": "حجم فایل بسیار بزرگ است",
  "validation.file.invalid_type": "نوع فایل مجاز نیست"
}
```

### استفاده در قالب‌ها

```html
<!-- فارسی -->
<h1>{{ t_('user.register.step1') }}</h1>

<!-- انگلیسی -->
<h1>{{ t_('user.register.step1') }}</h1>
```

---

## API Endpoints

### احراز هویت

| Method | Endpoint | توضیحات | Auth |
|--------|----------|---------|------|
| POST | `/api/users/register` | ثبت‌نام کاربر جدید | ❌ |
| POST | `/api/users/login` | ورود کاربر | ❌ |
| POST | `/api/users/logout` | خروج کاربر | ✅ |
| POST | `/api/users/verify_email` | تأیید ایمیل | ❌ |
| POST | `/api/users/verify_phone` | تأیید تلفن | ✅ |

### پروفایل کاربری

| Method | Endpoint | توضیحات | Auth |
|--------|----------|---------|------|
| GET | `/api/users/profile` | دریافت پروفایل | ✅ |
| PUT | `/api/users/profile` | ویرایش پروفایل | ✅ |
| POST | `/api/users/upload_document` | آپلود مدرک | ✅ |
| DELETE | `/api/users/document/<id>` | حذف مدرک | ✅ |
| GET | `/api/users/trust_score` | دریافت امتیاز اعتماد | ✅ |

### داشبورد

| Method | Endpoint | توضیحات | Auth | Roles |
|--------|----------|---------|------|-------|
| GET | `/api/dashboard/producer` | داشبورد تولیدکننده | ✅ | PRODUCER |
| GET | `/api/dashboard/investor` | داشبورد سرمایه‌گذار | ✅ | INVESTOR |
| GET | `/api/dashboard/expert` | داشبورد متخصص | ✅ | EXPERT |
| GET | `/api/dashboard/exhibitor` | داشبورد نمایشگاه‌دار | ✅ | EXHIBITOR |

### مدیریت کاربران (Admin)

| Method | Endpoint | توضیحات | Auth | Roles |
|--------|----------|---------|------|-------|
| GET | `/api/admin/users` | لیست کاربران | ✅ | ADMIN |
| GET | `/api/admin/users/<id>` | جزئیات کاربر | ✅ | ADMIN |
| PUT | `/api/admin/users/<id>/role` | تغییر نقش | ✅ | ADMIN |
| PUT | `/api/admin/users/<id>/verify` | تأیید هویت | ✅ | ADMIN |
| DELETE | `/api/admin/users/<id>` | حذف کاربر | ✅ | ADMIN |

---

## نمونه درخواست‌ها و پاسخ‌ها

### ثبت‌نام کاربر جدید

**درخواست:**
```http
POST /api/users/register
Content-Type: application/json

{
  "role": "PRODUCER",
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "phone": "+989123456789",
  "company_name": "Example Corp",
  "expertise_area": "Petrochemicals",
  "accept_terms": true
}
```

**پاسخ موفق:**
```json
{
  "success": true,
  "message": "Registration successful. Please verify your email.",
  "data": {
    "user_id": 123,
    "username": "john_doe",
    "role": "PRODUCER",
    "trust_score": 50,
    "verification_required": ["email", "phone"]
  }
}
```

**پاسخ خطا:**
```json
{
  "success": false,
  "error": "VALIDATION_ERROR",
  "details": {
    "password": ["Password must contain at least one special character"],
    "email": ["Email already registered"]
  }
}
```

### ویرایش پروفایل

**درخواست:**
```http
PUT /api/users/profile
Authorization: Bearer <token>
Content-Type: multipart/form-data

{
  "company_name": "Updated Corp",
  "job_title": "CEO",
  "bio": "Experienced professional in...",
  "website": "https://example.com",
  "social_links": {
    "linkedin": "https://linkedin.com/in/johndoe",
    "twitter": "https://twitter.com/johndoe"
  },
  "verification_document": <file>
}
```

**پاسخ:**
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "user_id": 123,
    "company_name": "Updated Corp",
    "job_title": "CEO",
    "trust_score": 65,
    "verification_status": "pending"
  }
}
```

---

## عیب‌یابی (Troubleshooting)

### مشکلات رایج

#### ۱. خطای "File type not allowed"
**علت:** پسوند فایل در لیست مجاز نیست.  
**راه‌حل:** فقط فایل‌های PDF، JPG، PNG آپلود کنید.

#### ۲. خطای "File too large"
**علت:** حجم فایل بیشتر از 5MB است.  
**راه‌حل:** فایل را فشرده کنید یا به چند قسمت تقسیم کنید.

#### ۳. خطای "Rate limit exceeded"
**علت:** تعداد درخواست‌ها از حد مجاز بیشتر شده.  
**راه‌حل:** ۱ دقیقه صبر کنید و دوباره تلاش کنید.

#### ۴. خطای "Insufficient permissions"
**علت:** کاربر نقش لازم برای دسترسی به مسیر را ندارد.  
**راه‌حل:** با نقش مناسب وارد شوید یا از ادمین درخواست تغییر نقش دهید.

#### ۵. خطای "Trust score too low"
**علت:** امتیاز اعتماد برای انجام عملیات کافی نیست.  
**راه‌حل:** پروفایل را تکمیل کنید، مدارک آپلود کنید و فعالیت مثبت داشته باشید.

---

## بهترین روش‌ها (Best Practices)

### برای کاربران

1. ✅ پروفایل خود را کامل تکمیل کنید
2. ✅ مدارک معتبر آپلود کنید
3. ✅ رمز عبور قوی انتخاب کنید
4. ✅ به‌طور منظم وارد حساب شوید
5. ✅ با سایر کاربران تعامل مثبت داشته باشید

### برای توسعه‌دهندگان

1. ✅ همیشه از دکوریتورهای احراز هویت استفاده کنید
2. ✅ ورودی‌ها را اعتبارسنجی کنید
3. ✅ از HTTPS در Production استفاده کنید
4. ✅ لاگ‌های امنیتی را بررسی کنید
5. ✅ به‌روزرسانی‌های امنیتی را اعمال کنید

---

## ضمیمه: فایل‌های مرتبط

| فایل | مسیر | توضیحات |
|------|------|---------|
| مدل کاربر | `models/user.py` | تعریف مدل User و فیلدها |
| Routes کاربران | `routes/users/routes.py` | endpointهای مربوط به کاربران |
| قالب ثبت‌نام | `templates/users/register_dynamic.html` | فرم ۳ مرحله‌ای ثبت‌نام |
| قالب ویرایش پروفایل | `templates/users/profile_edit.html` | فرم ویرایش پروفایل |
| قالب داشبورد | `templates/users/dashboard_*.html` | داشبوردهای نقش‌محور |
| ترجمه فارسی | `translations/fa.json` | کلیدهای ترجمه فارسی |
| ترجمه انگلیسی | `translations/en.json` | کلیدهای ترجمه انگلیسی |

---

## تاریخچه به‌روزرسانی

| نسخه | تاریخ | تغییرات |
|------|-------|---------|
| 1.0 | 2024-01-15 | ایجاد مستندات اولیه |
| 1.1 | 2024-01-20 | افزودن بخش Rate Limiting |
| 1.2 | 2024-01-25 | افزودن جزئیات آپلود امن فایل |
| 1.3 | 2024-01-30 | تکمیل بخش Trust Score |

---

<div align="center">

**مستندات ویژگی‌های پیشرفته کاربران - پلتفرم Metisma**

آخرین به‌روزرسانی: ژانویه ۲۰۲۴

</div>
