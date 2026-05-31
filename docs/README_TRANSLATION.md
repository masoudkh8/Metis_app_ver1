# راهنمای استفاده از سیستم ترجمه فارسی در متیما

## ساختار فایل‌های ترجمه

این پروژه از دو سیستم ترجمه پشتیبانی می‌کند:

### 1. فایل‌های Babel (.po و .mo) - برای متن‌های مستقیم
- **فایل منبع**: `translations/fa/LC_MESSAGES/messages.po` (قابل ویرایش)
- **فایل کامپایل شده**: `translations/fa/LC_MESSAGES/messages.mo` (باینری)
- مناسب برای: تمام متن‌های نمایش داده شده به کاربر

### 2. فایل JSON - برای سازگاری با عقب
- **مسیر**: `translations/fa.json`
- مناسب برای: کلیدهای خاص و ساختارهای تودرتو

## نحوه اضافه کردن ترجمه جدید

### روش توصیه شده: استفاده از فایل PO

1. **ویرایش فایل `messages.po`**:
   ```bash
   nano translations/fa/LC_MESSAGES/messages.po
   ```

2. **اضافه کردن ورودی جدید**:
   ```po
   #: templates/your_template.html
   msgid "English text here"
   msgstr "متن فارسی اینجا"
   ```

3. **کامپایل فایل MO**:
   ```bash
   pybabel compile -i translations/fa/LC_MESSAGES/messages.po -o translations/fa/LC_MESSAGES/messages.mo
   ```

### استخراج خودکار متن‌ها از تمپلیت‌ها

برای استخراج تمام متن‌های جدید از تمپلیت‌ها:
```bash
python extract_texts.py
```

این دستور:
- تمام فایل‌های HTML را اسکن می‌کند
- متن‌های انگلیسی را استخراج می‌کند
- در فایل `texts_to_translate.txt` ذخیره می‌کند

## استفاده در تمپلیت‌ها

### در فایل‌های HTML/Jinja2:

```html
<!-- استفاده از تابع t() -->
<h1>{{ t('Login') }}</h1>
<p>{{ t('Manage orders') }}</p>
<button>{{ t('Register') }}</button>

<!-- متن‌های طولانی -->
<p>{{ t('Register, track, and confirm orders completely digitally and in real time.') }}</p>
```

### در فایل‌های Python (Routes):

```python
from utils.translations import t

@app.route('/login')
def login():
    flash(t('Please log in first.'))
    return render_template('login.html')
```

## لیست متن‌های ترجمه شده

### صفحه اصلی (index.html)
- ✅ Metisma → متیما
- ✅ Our services → خدمات ما
- ✅ Manage orders → مدیریت سفارشات
- ✅ Security and authentication → امنیت و احراز هویت
- ✅ 24/7 support → پشتیبانی ۲۴ ساعته
- ✅ System training video → ویدیو آموزشی سیستم
- ✅ Cooperation with reputable companies → همکاری با شرکت‌های معتبر
- ✅ Imazhe magazine → مجله ایماژه
- ✅ Cooperate with us → همکاری با ما

### پنل مدیریت
- ✅ Admin Panel → پنل مدیریت
- ✅ Management dashboard → داشبورد مدیریت
- ✅ Total users → کل کاربران
- ✅ Special requests → درخواست‌های ویژه
- ✅ User management → مدیریت کاربران
- ✅ Access denied → دسترسی رد شد

### پنل کاربران
- ✅ Edit profile → ویرایش پروفایل
- ✅ Orders → سفارشات
- ✅ View my orders → مشاهده سفارشات من
- ✅ Upgrade to special user → ارتقاء به کاربر ویژه
- ✅ You are a special user → شما یک کاربر ویژه هستید

### پیام‌های Flash
- ✅ Please log in first → لطفاً ابتدا وارد شوید
- ✅ Payment receipt received → فیش پرداخت دریافت شد
- ✅ Mobile number verified → شماره موبایل تأیید شد
- ❌ Username already taken → ❌ نام کاربری قبلاً گرفته شده است

## نکات مهم

1. **همیشه بعد از ویرایش فایل PO، آن را کامپایل کنید**
2. **از کاراکترهای فارسی در msgstr استفاده کنید**
3. **علایم نگارشی و ایموجی‌ها را حفظ کنید**
4. **برای اعداد از فرمت فارسی استفاده کنید (۱۲۳ نه 123)**

## عیب‌یابی

### ترجمه‌ها نمایش داده نمی‌شوند:
```bash
# بررسی کنید فایل MO وجود دارد
ls -la translations/fa/LC_MESSAGES/messages.mo

# دوباره کامپایل کنید
pybabel compile -i translations/fa/LC_MESSAGES/messages.po -o translations/fa/LC_MESSAGES/messages.mo
```

### خطا در بارگذاری:
```python
# تست دستی
from utils.translations import translator
print(translator.t('Login'))  # باید 'ورود' چاپ کند
```

## ابزارهای مفید

### مشاهده تمام ترجمه‌ها:
```bash
cat translations/fa/LC_MESSAGES/messages.po | grep -A 1 "msgid"
```

### شمارش تعداد ترجمه‌ها:
```bash
grep -c "^msgid" translations/fa/LC_MESSAGES/messages.po
```

---
**توسعه یافته برای پلتفرم متیما - ۱۴۰۳**
