# 🚀 راه‌اندازی سریع زبان فارسی - Metisma

## ✅ وضعیت فعلی
زبان فارسی به‌طور کامل در پروژه Metisma راه‌اندازی شد و تمام ۱۶ تست مربوطه با موفقیت گذرانده شدند.

---

## 📋 خلاصه اقدامات

### فایل‌های ایجاد شده:
1. `translations/fa_IR/LC_MESSAGES/messages.po` - ۵۷۰+ کلید ترجمه
2. `translations/fa_IR/LC_MESSAGES/messages.mo` - فایل کامپایل شده
3. `routes/language.py` - مسیر تغییر زبان
4. `utils/language_switcher.py` - راهنما و کامپوننت
5. `tests/test_i18n.py` - ۱۶ تست کامل
6. `docs/PERSIAN_LANGUAGE_SETUP.md` - مستندات کامل

### فایل‌های تغییر یافته:
- `extensions.py` - اضافه شدن `babel`
- `config.py` - تنظیمات i18n
- `app.py` - یکپارچه‌سازی Flask-Babel

---

## 🎯 استفاده سریع

### ۱. افزودن Language Switcher به قالب
```html
<!-- در templates/base.html -->
<nav class="language-switcher">
    <a href="?lang=fa_IR" class="{{ 'active' if current_locale == 'fa_IR' else '' }}">
        🇮🇷 فارسی
    </a>
    <a href="?lang=en" class="{{ 'active' if current_locale == 'en' else '' }}">
        🇬🇧 English
    </a>
</nav>
```

### ۲. استفاده از ترجمه در قالب‌ها
```html
<h1>{{ _('Welcome to Metisma') }}</h1>
<p>{{ _('Login') }} | {{ _('Register') }}</p>
<button>{{ _('Save Changes') }}</button>
```

### ۳. تغییر زبان
```python
# در کد Python
session['lang'] = 'fa_IR'

# یا از طریق URL
/users/profile?lang=fa_IR

# یا از طریق route
/language/set_language/fa_IR
```

---

## 🧪 اجرای تست‌ها
```bash
# اجرای تست‌های i18n
pytest tests/test_i18n.py -v

# نتیجه مورد انتظار: 16 passed
```

---

## 📊 آمار ترجمه‌ها

| دسته‌بندی | تعداد کلیدها |
|-----------|-------------|
| احراز هویت | ۲۰+ |
| پروفایل و داشبورد | ۳۰+ |
| Trust Score | ۱۵+ |
| منو و ناوبری | ۴۰+ |
| عملیات | ۳۰+ |
| پیام‌ها | ۳۰+ |
| مالی | ۲۰+ |
| سایر | ۳۸۵+ |
| **جمع** | **۵۷۰+** |

---

## 🔧 دستورات مفید

```bash
# کامپایل ترجمه‌ها
pybabel compile -d /workspace/translations -l fa_IR

# افزودن کلید جدید به فایل ترجمه
# ویرایش فایل translations/fa_IR/LC_MESSAGES/messages.po
# سپس کامپایل مجدد

# اجرای اپلیکیشن
python app.py run
```

---

## ✨ ویژگی‌های کلیدی

✅ **پیش‌فرض فارسی**: زبان پیش‌فرض برنامه فارسی است  
✅ **تشخیص خودکار**: تشخیص زبان از session، URL، یا مرورگر  
✅ **RTL کامل**: پشتیبانی از راست‌چین  
✅ **توسعه‌پذیر**: افزودن آسان زبان‌های جدید  
✅ **مستندات کامل**: راهنمای فارسی و انگلیسی  
✅ **تست شده**: ۱۶ تست خودکار  

---

## 📞 پشتیبانی

- مستندات کامل: `docs/PERSIAN_LANGUAGE_SETUP.md`
- فایل ترجمه: `translations/fa_IR/LC_MESSAGES/messages.po`
- تست‌ها: `tests/test_i18n.py`

---

## 🎉 نتیجه‌گیری

زبان فارسی با موفقیت به پروژه Metisma اضافه شد. کاربران می‌توانند به راحتی بین فارسی و انگلیسی جابجا شوند.

**وضعیت:** ✅ آماده تولید  
**زبان پیش‌فرض:** فارسی  
**تست‌ها:** ۱۶/۱۶ موفق  
