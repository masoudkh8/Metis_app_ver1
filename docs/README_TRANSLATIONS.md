# راهنمای استفاده از سیستم ترجمه فارسی

## ساختار فایل‌ها

```
/workspace/
├── translations/
│   └── fa.json          # فایل ترجمه فارسی
├── utils/
│   └── translations.py  # ماژول مترجم
└── templates/
    └── *.html           # فایل‌های قالب
```

## نحوه استفاده در تمپلیت‌ها

### روش ۱: استفاده مستقیم از تابع t()

```python
# در routes/*.py
from utils.translations import t

@app.route('/login')
def login():
    flash(t('messages.login_success'))
    return render_template('users/login.html')
```

### روش ۲: اضافه کردن به context تمپلیت

```python
# در app.py یا routes/*.py
from utils.translations import translator

@app.context_processor
def inject_translator():
    return {'t': translator.t}
```

سپس در تمپلیت:
```html
<h1>{{ t('common.welcome') }}</h1>
<button>{{ t('common.login') }}</button>
```

### روش ۳: استفاده از Jinja2 custom filter

```python
# در app.py
from utils.translations import t
app.jinja_env.filters['t'] = t
```

سپس در تمپلیت:
```html
<h1>{{ 'common.welcome'|t }}</h1>
```

## کلیدهای ترجمه موجود

### عمومی (common)
- `common.login` → ورود
- `common.register` → ثبت‌نام
- `common.logout` → خروج
- `common.email` → ایمیل
- `common.password` → رمز عبور
- `common.username` → نام کاربری
- `common.welcome` → خوش آمدید

### نقش‌ها (roles)
- `roles.buyer` → خریدار
- `roles.seller` → فروشنده
- `roles.broker` → کارگزار
- `roles.admin` → مدیر
- `roles.special` → ویژه

### پیام‌ها (messages)
- `messages.login_success` → ✅ خوش آمدید!
- `messages.login_error` → ❌ ایمیل یا رمز عبور اشتباه است.
- `messages.register_success` → ✅ ثبت‌نام موفقیت‌آمیز بود!

### صفحات (pages)
- `pages.home` → صفحه اصلی
- `pages.dashboard` → داشبورد
- `pages.profile` → پروفایل

### برچسب‌ها (labels)
- `labels.company_name` → نام شرکت
- `labels.country` → کشور
- `labels.your_role` → نقش شما

## افزودن ترجمه جدید

۱. باز کردن `/workspace/translations/fa.json`
۲. اضافه کردن کلید جدید به بخش مربوطه
۳. ذخیره فایل
۴. استفاده در کد با `t('section.key')`

مثال:
```json
{
  "messages": {
    "new_message": "پیام جدید فارسی"
  }
}
```

## جایگزینی متغیرها

```python
t('messages.user_deleted', username='ali')
# خروجی: کاربر ali حذف شد.
```

در فایل JSON:
```json
{
  "user_deleted": "کاربر {username} حذف شد."
}
```
