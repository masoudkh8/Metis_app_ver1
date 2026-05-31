# مستند کامل سیستم چندزبانه (i18n) و پشتیبانی از زبان فارسی در پروژه Metisma

## فهرست مطالب
1. [معرفی سیستم](#معرفی-سیستم)
2. [راه‌اندازی و نصب](#راه‌اندازی-و-نصب)
3. [ساختار فایل‌ها](#ساختار-فایل‌ها)
4. [راهنمای توسعه‌دهنده](#راهنمای-توسعه‌دهنده)
5. [تنظیمات فرانت‌اند (RTL و فونت)](#تنظیمات-فرانت‌اند-rtl-و-فونت)
6. [تست و اعتبارسنجی](#تست-و-اعتبارسنجی)
7. [عیب‌یابی (Troubleshooting)](#عیب‌یابی-troubleshooting)

---

## معرفی سیستم

### معماری Flask-Babel
پروژه Metisma از کتابخانه **Flask-Babel** برای پیاده‌سازی سیستم بین‌المللی‌سازی (i18n) استفاده می‌کند. این کتابخانه بر پایه GNU Gettext ساخته شده و امکان ترجمه برنامه به زبان‌های مختلف را فراهم می‌کند.

#### ویژگی‌های کلیدی:
- پشتیبانی از چندین زبان همزمان
- تشخیص خودکار زبان کاربر از طریق HTTP Headers
- کش کردن ترجمه‌ها برای بهبود عملکرد
- یکپارچه‌سازی با Jinja2 Templates

### ساختار پوشه translations
```
project_root/
├── app/
│   ├── translations/
│   │   ├── fa/
│   │   │   └── LC_MESSAGES/
│   │   │       ├── messages.po    # فایل ترجمه فارسی (قابل ویرایش)
│   │   │       └── messages.mo    # فایل باینری کامپایل شده
│   │   ├── en/
│   │   │   └── LC_MESSAGES/
│   │   │       ├── messages.po
│   │   │       └── messages.mo
│   │   └── messages.pot           # قالب اصلی رشته‌ها
│   ├── __init__.py                # مقداردهی اولیه Babel
│   └── ...
├── babel.cfg                      # تنظیمات استخراج رشته‌ها
└── setup.py / pyproject.toml      # پیکربندی Babel
```

---

## راه‌اندازی و نصب

### پیش‌نیازها
```bash
pip install Flask-Babel
```

### مرحله ۱: مقداردهی اولیه در کد
در فایل `app/__init__.py`:

```python
from flask import Flask, request, session
from flask_babel import Babel, gettext as _

def create_app():
    app = Flask(__name__)
    
    # پیکربندی Babel
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
    
    # لیست زبان‌های پشتیبانی شده
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'fa': 'فارسی'
    }
    
    def get_locale():
        # اولویت‌بندی تشخیص زبان:
        # 1. زبان ذخیره شده در session
        # 2. زبان ارسال شده توسط کاربر در URL
        # 3. زبان مرورگر کاربر
        if 'lang' in session:
            return session['lang']
        
        lang = request.args.get('lang')
        if lang and lang in SUPPORTED_LANGUAGES:
            session['lang'] = lang
            return lang
        
        return request.accept_languages.best_match(SUPPORTED_LANGUAGES.keys())
    
    babel = Babel(app, locale_selector=get_locale)
    
    # متغیرهای کمکی برای قالب‌ها
    @app.context_processor
    def inject_vars():
        return {
            'supported_languages': SUPPORTED_LANGUAGES,
            'current_language': get_locale()
        }
    
    return app
```

### مرحله ۲: ایجاد ساختار دایرکتوری
```bash
# ایجاد پوشه translations
mkdir -p app/translations

# ایجاد فایل پیکربندی Babel
cat > babel.cfg << EOF
[python: **.py]
[jinja2: **/templates/**.html]
encoding = utf-8
EOF
```

### مرحله ۳: استخراج رشته‌های قابل ترجمه
```bash
# استخراج تمام رشته‌های علامت‌گذاری شده به فایل POT
pybabel extract -F babel.cfg -k _l -o app/translations/messages.pot .
```

### مرحله ۴: ایجاد فایل ترجمه برای زبان جدید
```bash
# برای زبان فارسی
pybabel init -i app/translations/messages.pot -d app/translations -l fa

# برای زبان انگلیسی (اگر نیاز است)
pybabel init -i app/translations/messages.pot -d app/translations -l en
```

### مرحله ۵: ترجمه فایل PO
فایل `app/translations/fa/LC_MESSAGES/messages.po` را باز کرده و ترجمه‌ها را وارد کنید:

```po
msgid "Hello"
msgstr "سلام"

msgid "Welcome to Metisma"
msgstr "به متیسم خوش آمدید"
```

### مرحله ۶: کامپایل فایل‌های MO
```bash
# کامپایل فایل‌های PO به فرمت باینری MO
pybabel compile -d app/translations

# خروجی مورد انتظار:
# compiling catalog app/translations/fa/LC_MESSAGES/messages.po to 
# app/translations/fa/LC_MESSAGES/messages.mo
```

### مرحله ۷: به‌روزرسانی ترجمه‌ها (پس از افزودن رشته‌های جدید)
```bash
# 1. استخراج مجدد رشته‌ها
pybabel extract -F babel.cfg -k _l -o app/translations/messages.pot .

# 2. به‌روزرسانی فایل‌های PO موجود
pybabel update -i app/translations/messages.pot -d app/translations

# 3. ترجمه رشته‌های جدید در فایل‌های PO

# 4. کامپایل مجدد
pybabel compile -d app/translations
```

---

## ساختار فایل‌ها

### فایل messages.pot (Portable Object Template)
- **هدف**: قالب اصلی شامل تمام رشته‌های قابل ترجمه
- **موقعیت**: `app/translations/messages.pot`
- **فرمت**: متن ساده
- **مثال**:
```po
# Translations template for PROJECT NAME.
# Copyright (C) 2024 ORGANIZATION
# This file is distributed under the same license as the PROJECT project.

#: app/routes.py:15
msgid "Hello World"
msgstr ""

#: app/templates/index.html:5
msgid "Welcome"
msgstr ""
```

### فایل messages.po (Portable Object)
- **هدف**: حاوی ترجمه‌های یک زبان خاص
- **موقعیت**: `app/translations/<lang>/LC_MESSAGES/messages.po`
- **فرمت**: متن ساده (قابل ویرایش)
- **مثال برای فارسی**:
```po
# Persian translations for Metisma.
# Copyright (C) 2024 Metisma
# This file is distributed under the same license as the Metisma project.
# FIRST AUTHOR <EMAIL@ADDRESS>, 2024.

msgid ""
msgstr ""
"Project-Id-Version: Metisma 1.0\n"
"Report-Msgid-Bugs-To: support@metisma.com\n"
"POT-Creation-Date: 2024-01-15 10:00+0330\n"
"PO-Revision-Date: 2024-01-15 12:00+0330\n"
"Last-Translator: Your Name <you@example.com>\n"
"Language: fa\n"
"Language-Team: Persian\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=2; plural=(n > 1);\n"

#: app/routes.py:15
msgid "Hello World"
msgstr "سلام دنیا"

#: app/templates/index.html:5
msgid "Welcome"
msgstr "خوش آمدید"

# مثال برای جمع‌بستن
#: app/models.py:30
msgid "%(count)d user"
msgid_plural "%(count)d users"
msgstr[0] "%(count)d کاربر"
msgstr[1] "%(count)d کاربران"
```

### فایل messages.mo (Machine Object)
- **هدف**: فایل باینری کامپایل شده برای استفاده در زمان اجرا
- **موقعیت**: `app/translations/<lang>/LC_MESSAGES/messages.mo`
- **فرمت**: باینری (غیرقابل ویرایش)
- **نکته**: این فایل باید پس از هر تغییر در فایل PO مجدداً کامپایل شود

---

## راهنمای توسعه‌دهنده

### نحوه علامت‌گذاری رشته‌ها در کد پایتون

#### 1. ترجمه فوری (Immediate Translation)
```python
from flask_babel import gettext as _

# استفاده در ویوها
@app.route('/hello')
def hello():
    message = _('Hello, welcome to Metisma!')
    return jsonify({'message': message})
```

#### 2. ترجمه تنبل (Lazy Translation)
برای مواردی که ترجمه باید در زمان رندر انجام شود (مثل مدل‌ها):

```python
from flask_babel import lazy_gettext as _l

class Product(db.Model):
    name = db.Column(db.String(100))
    category = db.Column(db.String(50), default=_l('General'))
```

#### 3. ترجمه با پارامترها
```python
from flask_babel import ngettext

# برای جمع‌بستن
count = 5
message = ngettext('%(count)d item', '%(count)d items', count) % {'count': count}
# خروجی فارسی: "5 آیتم"

# با پارامترهای متعدد
from flask_babel import gettext as _
message = _('Hello %(name)s, you have %(num)d messages.') % {
    'name': 'Ali',
    'num': 3
}
```

#### 4. ترجمه در کلاس‌ها و ماژول‌ها
```python
# در سطح ماژول
from flask_babel import lazy_gettext as _l

ERROR_MESSAGES = {
    'not_found': _l('Resource not found'),
    'unauthorized': _l('Access denied'),
    'server_error': _l('Internal server error')
}

# در کلاس‌ها
class FormError:
    def __init__(self):
        self.required = _l('This field is required')
        self.invalid = _l('Invalid input')
```

### نحوه استفاده در قالب‌های Jinja2

#### 1. استفاده پایه
```html+jinja
<!-- در قالب‌های HTML -->
<h1>{{ _('Welcome to Metisma') }}</h1>
<p>{{ _('Hello %(name)s', name=user.name) }}</p>
```

#### 2. استفاده با متغیرها
```html+jinja
{% set count = products|length %}
<p>{{ _('%(count)d product found', count=count) }}</p>

<!-- برای جمع‌بستن -->
<p>{{ _n('%(count)d product', '%(count)d products', count, count=count) }}</p>
```

#### 3. استفاده در اتریبیوت‌ها
```html+jinja
<input type="text" placeholder="{{ _('Search...') }}" />
<button title="{{ _('Click to submit') }}">{{ _('Submit') }}</button>
```

#### 4. بلوک‌های ترجمه
```html+jinja
{% trans %}
    <p>This is a paragraph with <strong>bold text</strong>.</p>
{% endtrans %}

{% trans user_name=user.name %}
    <p>Hello {{ user_name }}, welcome back!</p>
{% endtrans %}

{% trans count=items|length %}
    <p>There is {{ count }} item.</p>
{% pluralize %}
    <p>There are {{ count }} items.</p>
{% endtrans %}
```

### دستورالعمل استخراج و به‌روزرسانی رشته‌های جدید

#### چک‌لیست افزودن ترجمه جدید:

1. **علامت‌گذاری رشته در کد**:
```python
# قبل از commit، تمام رشته‌های جدید را با _() یا _l() علامت‌گذاری کنید
message = _('New feature added successfully')
```

2. **استخراج رشته‌ها**:
```bash
make extract-translations
# یا به صورت دستی:
pybabel extract -F babel.cfg -k _l -o app/translations/messages.pot .
```

3. **به‌روزرسانی فایل‌های PO**:
```bash
make update-translations
# یا به صورت دستی:
pybabel update -i app/translations/messages.pot -d app/translations
```

4. **ترجمه رشته‌های جدید**:
   - فایل‌های `.po` را باز کنید
   - رشته‌های جدید را پیدا کنید (معمولاً در انتهای فایل)
   - ترجمه‌ها را در `msgstr` وارد کنید
   - **نکته مهم**: برای زبان فارسی، حتماً از راست‌چین بودن و کاراکترهای صحیح استفاده کنید

5. **کامپایل**:
```bash
make compile-translations
# یا به صورت دستی:
pybabel compile -d app/translations
```

6. **تست**:
```bash
pytest tests/test_i18n.py
```

#### اسکریپت Makefile پیشنهادی:
```makefile
.PHONY: extract-translations update-translations compile-translations

extract-translations:
	pybabel extract -F babel.cfg -k _l -o app/translations/messages.pot .

update-translations:
	pybabel update -i app/translations/messages.pot -d app/translations

compile-translations:
	pybabel compile -d app/translations

translations: extract-translations update-translations compile-translations
```

---

## تنظیمات فرانت‌اند (RTL و فونت)

### پیاده‌سازی RTL (راست‌چین) برای زبان فارسی

#### 1. تشخیص جهت زبان در قالب پایه
```html+jinja
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="{{ current_language }}" dir="{{ 'rtl' if current_language == 'fa' else 'ltr' }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ _('Metisma') }}{% endblock %}</title>
    
    {% if current_language == 'fa' %}
        <link rel="stylesheet" href="{{ url_for('static', filename='css/rtl.css') }}">
        <link rel="stylesheet" href="{{ url_for('static', filename='fonts/vazirmatn.css') }}">
    {% else %}
        <link rel="stylesheet" href="{{ url_for('static', filename='css/ltr.css') }}">
    {% endif %}
    
    <style>
        html[lang="fa"] {
            font-family: 'Vazirmatn', Tahoma, Arial, sans-serif;
        }
    </style>
</head>
<body class="{{ 'rtl' if current_language == 'fa' else 'ltr' }}">
    <!-- محتوا -->
</body>
</html>
```

#### 2. فایل CSS برای RTL
```css
/* static/css/rtl.css */

/* تنظیمات پایه */
[dir="rtl"] {
    text-align: right;
    direction: rtl;
}

/* معکوس کردن margin و padding */
[dir="rtl"] .ml-1 { margin-left: 0; margin-right: 0.25rem; }
[dir="rtl"] .mr-1 { margin-right: 0; margin-left: 0.25rem; }
[dir="rtl"] .pl-1 { padding-left: 0; padding-right: 0.25rem; }
[dir="rtl"] .pr-1 { padding-right: 0; padding-left: 0.25rem; }

/* فلکس‌باکس */
[dir="rtl"] .flex-row { flex-direction: row-reverse; }

/* آیکون‌ها */
[dir="rtl"] .icon-arrow-left { transform: rotate(180deg); }
[dir="rtl"] .icon-arrow-right { transform: rotate(180deg); }

/* جدول‌ها */
[dir="rtl"] table { text-align: right; }

/* فرم‌ها */
[dir="rtl"] input,
[dir="rtl"] textarea,
[dir="rtl"] select {
    text-align: right;
    direction: rtl;
}

/* ناوبری */
[dir="rtl"] nav ul {
    padding-right: 0;
}

[dir="rtl"] nav li {
    float: right;
    margin-left: 1rem;
    margin-right: 0;
}

/* مدیا کوئری برای چاپ */
@media print {
    [dir="rtl"] {
        direction: rtl;
        text-align: right;
    }
}
```

#### 3. فونت وزیرمتن (Vazirmatn)
```css
/* static/fonts/vazirmatn.css */

@font-face {
    font-family: 'Vazirmatn';
    src: url('../fonts/Vazirmatn-Light.woff2') format('woff2');
    font-weight: 300;
    font-style: normal;
    font-display: swap;
}

@font-face {
    font-family: 'Vazirmatn';
    src: url('../fonts/Vazirmatn-Regular.woff2') format('woff2');
    font-weight: 400;
    font-style: normal;
    font-display: swap;
}

@font-face {
    font-family: 'Vazirmatn';
    src: url('../fonts/Vazirmatn-Medium.woff2') format('woff2');
    font-weight: 500;
    font-style: normal;
    font-display: swap;
}

@font-face {
    font-family: 'Vazirmatn';
    src: url('../fonts/Vazirmatn-Bold.woff2') format('woff2');
    font-weight: 700;
    font-style: normal;
    font-display: swap;
}

/* دانلود فونت از: https://github.com/rastikerdar/vazirmatn */
```

#### 4. انتخابگر زبان در UI
```html+jinja
<!-- templates/components/language_switcher.html -->
<div class="language-switcher">
    <form action="{{ url_for('set_language') }}" method="POST">
        <select name="lang" onchange="this.form.submit()">
            {% for code, name in supported_languages.items() %}
                <option value="{{ code }}" {% if current_language == code %}selected{% endif %}>
                    {{ name }}
                </option>
            {% endfor %}
        </select>
    </form>
</div>
```

```python
# در routes.py
@app.route('/set_language', methods=['POST'])
def set_language():
    lang = request.form.get('lang')
    if lang and lang in app.config['SUPPORTED_LANGUAGES']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))
```

#### 5. نکات مهم RTL
- از `margin-left` و `margin-right` به صورت منطقی استفاده کنید
- برای آیکون‌های جهت‌دار (فلش‌ها) از transform استفاده کنید
- تست کنید که dropdownها و منوها به درستی باز شوند
- اسکرول‌بارها باید در سمت چپ باشند (به صورت پیش‌فرض در RTL)
- تاریخ و اعداد باید به فرمت فارسی نمایش داده شوند (اختیاری)

---

## تست و اعتبارسنجی

### اجرای تست‌های خودکار i18n

#### 1. تست واحد برای ترجمه‌ها
```python
# tests/test_i18n.py
import pytest
from flask import session
from app import create_app
from flask_babel import gettext as _, force_locale

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    return app

@pytest.fixture
def client(app):
    return app.test_client()

class TestI18N:
    def test_english_translation(self, app):
        """تست ترجمه انگلیسی"""
        with app.app_context():
            with force_locale('en'):
                assert _('Hello') == 'Hello'
                assert _('Welcome to Metisma') == 'Welcome to Metisma'
    
    def test_persian_translation(self, app):
        """تست ترجمه فارسی"""
        with app.app_context():
            with force_locale('fa'):
                assert _('Hello') == 'سلام'
                assert _('Welcome to Metisma') == 'به متیسم خوش آمدید'
    
    def test_language_detection_from_header(self, client):
        """تست تشخیص زبان از هدر HTTP"""
        response = client.get('/', headers={'Accept-Language': 'fa'})
        assert response.status_code == 200
        # بررسی وجود متن فارسی در پاسخ
        assert 'سلام' in response.data.decode('utf-8') or 'خوش آمدید' in response.data.decode('utf-8')
    
    def test_language_switching_via_session(self, client):
        """تست تغییر زبان از طریق session"""
        with client.session_transaction() as sess:
            sess['lang'] = 'fa'
        
        response = client.get('/')
        assert response.status_code == 200
    
    def test_pluralization_in_english(self, app):
        """تست جمع‌بستن در انگلیسی"""
        from flask_babel import ngettext
        with app.app_context():
            with force_locale('en'):
                assert ngettext('%(count)d item', '%(count)d items', 1) % {'count': 1} == '1 item'
                assert ngettext('%(count)d item', '%(count)d items', 2) % {'count': 2} == '2 items'
    
    def test_pluralization_in_persian(self, app):
        """تست جمع‌بستن در فارسی"""
        from flask_babel import ngettext
        with app.app_context():
            with force_locale('fa'):
                # در فارسی معمولاً برای 1 و بیشتر از 1 تفاوت دارد
                result = ngettext('%(count)d item', '%(count)d items', 1) % {'count': 1}
                assert '1' in result
    
    def test_missing_translation_fallback(self, app):
        """تست fallback به زبان پیش‌فرض وقتی ترجمه وجود ندارد"""
        with app.app_context():
            with force_locale('fa'):
                # اگر ترجمه فارسی وجود نداشته باشد، باید انگلیسی نمایش داده شود
                result = _('NonExistentKey12345')
                assert result == 'NonExistentKey12345'  # کلید برگردانده می‌شود
    
    def test_template_translation(self, client):
        """تست ترجمه در قالب‌ها"""
        response = client.get('/')
        assert response.status_code == 200
        data = response.data.decode('utf-8')
        # بررسی وجود تگ‌های ترجمه شده
        assert 'lang=' in data
    
    def test_rtl_direction_for_persian(self, client):
        """تست جهت RTL برای زبان فارسی"""
        with client.session_transaction() as sess:
            sess['lang'] = 'fa'
        
        response = client.get('/')
        assert response.status_code == 200
        data = response.data.decode('utf-8')
        assert 'dir="rtl"' in data or 'dir=\'rtl\'' in data
    
    def test_ltr_direction_for_english(self, client):
        """تست جهت LTR برای زبان انگلیسی"""
        with client.session_transaction() as sess:
            sess['lang'] = 'en'
        
        response = client.get('/')
        assert response.status_code == 200
        data = response.data.decode('utf-8')
        assert 'dir="ltr"' in data or 'dir=\'ltr\'' in data

def test_all_translations_compiled(app):
    """تست کامپایل بودن تمام فایل‌های ترجمه"""
    import os
    from pathlib import Path
    
    translations_dir = Path(app.root_path) / 'translations'
    
    for lang_dir in translations_dir.iterdir():
        if lang_dir.is_dir() and lang_dir.name not in ['__pycache__', 'messages.pot']:
            mo_file = lang_dir / 'LC_MESSAGES' / 'messages.mo'
            assert mo_file.exists(), f"فایل کامپایل شده برای زبان {lang_dir.name} وجود ندارد"
```

#### 2. تست یکپارچگی
```python
# tests/integration/test_i18n_integration.py
import pytest

class TestI18NIntegration:
    def test_full_page_render_in_persian(self, client):
        """تست رندر کامل صفحه به زبان فارسی"""
        with client.session_transaction() as sess:
            sess['lang'] = 'fa'
        
        response = client.get('/')
        assert response.status_code == 200
        
        data = response.data.decode('utf-8')
        
        # بررسی المان‌های RTL
        assert 'dir="rtl"' in data
        
        # بررسی فونت فارسی
        assert 'Vazirmatn' in data or 'وزیر' in data
        
        # بررسی عدم وجود متن‌های ترجمه نشده
        assert 'msgid' not in data
    
    def test_api_response_localization(self, client):
        """تست محلی‌سازی پاسخ‌های API"""
        with client.session_transaction() as sess:
            sess['lang'] = 'fa'
        
        response = client.get('/api/status')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'message' in data
        # بررسی اینکه پیام به فارسی است
        assert any(ord(c) > 127 for c in data['message'])  # وجود کاراکتر غیر ASCII
    
    def test_error_messages_localization(self, client):
        """تست محلی‌سازی پیام‌های خطا"""
        with client.session_transaction() as sess:
            sess['lang'] = 'fa'
        
        response = client.get('/nonexistent-page')
        # پیام خطا باید به فارسی باشد
```

#### 3. تست اعتبارسنجی فایل‌های PO
```python
# tests/test_po_files.py
import polib
from pathlib import Path

def test_po_file_syntax():
    """تست صحت نحو فایل‌های PO"""
    translations_dir = Path('app/translations')
    
    for po_file in translations_dir.glob('**/messages.po'):
        try:
            po = polib.pofile(str(po_file))
            assert po.metadata is not None, f"فایل {po_file} متادیتا ندارد"
            assert 'Language' in po.metadata, f"فایل {po_file} فیلد Language ندارد"
            
            # بررسی ترجمه‌های خالی
            empty_translations = [entry.msgid for entry in po if not entry.msgstr]
            assert len(empty_translations) == 0, (
                f"ترجمه‌های خالی در {po_file}: {empty_translations[:5]}"
            )
        except Exception as e:
            pytest.fail(f"خطا در خواندن فایل {po_file}: {str(e)}")

def test_po_file_encoding():
    """تست انکدینگ فایل‌های PO"""
    translations_dir = Path('app/translations')
    
    for po_file in translations_dir.glob('**/messages.po'):
        with open(po_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # بررسی وجود کاراکترهای فارسی
            if 'fa' in str(po_file):
                assert any('\u0600' <= c <= '\u06FF' for c in content), \
                    f"فایل {po_file} فاقد کاراکتر فارسی است"
```

#### 4. اجرای تست‌ها
```bash
# اجرای تمام تست‌های i18n
pytest tests/test_i18n.py -v

# با coverage
pytest tests/test_i18n.py --cov=app --cov-report=html

# اجرای تست‌های مربوط به PO
pytest tests/test_po_files.py -v
```

---

## عیب‌یابی (Troubleshooting)

### مشکل ۱: ترجمه‌ها نمایش داده نمی‌شوند

**علائم**: متن‌ها به زبان اصلی (انگلیسی) نمایش داده می‌شوند.

**راه‌حل‌ها**:

1. **بررسی کامپایل فایل‌های MO**:
```bash
# مطمئن شوید فایل‌های .mo وجود دارند
ls -la app/translations/fa/LC_MESSAGES/messages.mo
ls -la app/translations/en/LC_MESSAGES/messages.mo

# اگر وجود ندارند، کامپایل کنید
pybabel compile -d app/translations
```

2. **بررسی کش Flask**:
```python
# در محیط توسعه، کش را غیرفعال کنید
app.config['BABEL_CACHE_DIR'] = None
```

3. **ری‌استارت سرور**:
```bash
# گاهی اوقات نیاز به ری‌استارت کامل است
# به ویژه در محیط production
systemctl restart metisma  # یا دستور معادل
```

4. **بررسی مسیر فایل‌ها**:
```python
# در کد، مسیر translations را بررسی کنید
import os
print(os.path.exists('app/translations/fa/LC_MESSAGES/messages.mo'))
```

### مشکل ۲: تغییر زبان اعمال نمی‌شود

**علائم**: با وجود تغییر زبان، محتوا همچنان به زبان قبلی است.

**راه‌حل‌ها**:

1. **بررسی session**:
```python
# مطمئن شوید session به درستی کار می‌کند
@app.before_request
def debug_session():
    print(f"Session lang: {session.get('lang')}")
    print(f"Accept-Language: {request.headers.get('Accept-Language')}")
```

2. **پاک کردن کش مرورگر**:
   - کوکی‌ها را پاک کنید
   - از حالت incognito استفاده کنید

3. **بررسی order در locale_selector**:
```python
# مطمئن شوید تابع get_locale به درستی پیاده‌سازی شده
def get_locale():
    print(f"Session: {session.get('lang')}")
    print(f"URL param: {request.args.get('lang')}")
    print(f"Browser: {request.accept_languages.best_match(['en', 'fa'])}")
    # ... ادامه کد
```

### مشکل ۳: فایل‌های PO به‌روزرسانی نمی‌شوند

**علائم**: رشته‌های جدید در فایل‌های PO ظاهر نمی‌شوند.

**راه‌حل‌ها**:

1. **بررسی babel.cfg**:
```ini
# مطمئن شوید الگوها صحیح هستند
[python: **.py]
[jinja2: **/templates/**.html]
encoding = utf-8
```

2. **بررسی نام تابع gettext**:
```python
# اگر از _l استفاده می‌کنید، باید در babel.cfg مشخص شود
# در babel.cfg:
[python: **.py]
extract_messages = _, _l, gettext, ngettext
```

3. **اجرای دستی extract**:
```bash
pybabel extract -F babel.cfg -k _ -k _l -k gettext -k ngettext \
    -o app/translations/messages.pot .
```

### مشکل ۴: کاراکترهای فارسی به درستی نمایش داده نمی‌شوند

**علائم**: کاراکترها به صورت ؟؟؟ یا مربع نمایش داده می‌شوند.

**راه‌حل‌ها**:

1. **بررسی encoding فایل‌ها**:
```bash
# بررسی encoding فایل‌های PO
file app/translations/fa/LC_MESSAGES/messages.po
# باید UTF-8 باشد

# اگر نیست، تبدیل کنید
iconv -f ISO-8859-1 -t UTF-8 input.po > output.po
```

2. **بررسی هدر Content-Type**:
```python
@app.after_request
def set_encoding(response):
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response
```

3. **بررسی متا تگ HTML**:
```html
<meta charset="UTF-8">
```

4. **بررسی فونت**:
```css
/* مطمئن شوید فونت فارسی لود می‌شود */
@font-face {
    font-family: 'Vazirmatn';
    src: url('../fonts/Vazirmatn-Regular.woff2') format('woff2');
}
```

### مشکل ۵: جمع‌بستن (Pluralization) کار نمی‌کند

**علائم**: متن جمع به درستی نمایش داده نمی‌شود.

**راه‌حل‌ها**:

1. **بررسی Plural-Forms در فایل PO**:
```po
# در فایل fa/LC_MESSAGES/messages.po باید باشد:
"Plural-Forms: nplurals=2; plural=(n > 1);\n"
```

2. **بررسی استفاده از ngettext**:
```python
# صحیح:
from flask_babel import ngettext
message = ngettext('%(count)d item', '%(count)d items', count) % {'count': count}

# غلط:
message = ngettext('%(count)d item', '%(count)d items') % {'count': count}  #缺少 count parameter
```

3. **بررسی ترجمه هر دو حالت**:
```po
msgid "%(count)d item"
msgid_plural "%(count)d items"
msgstr[0] "%(count)d آیتم"
msgstr[1] "%(count)d آیتم‌ها"
```

### مشکل ۶: عملکرد کند در محیط Production

**علائم**: ترجمه‌ها باعث کندی برنامه می‌شوند.

**راه‌حل‌ها**:

1. **فعال کردن کش Babel**:
```python
app.config['BABEL_CACHE_DIR'] = '/tmp/babel_cache'
app.config['BABEL_CACHE_ENABLED'] = True
```

2. **استفاده از Lazy Translation**:
```python
# در مدل‌ها و جاهایی که در import-time ارزیابی می‌شوند
from flask_babel import lazy_gettext as _l
```

3. **کامپایل بهینه فایل‌های MO**:
```bash
# از آخرین نسخه Werkzeug و Flask-Babel استفاده کنید
pip install --upgrade Flask-Babel
```

### ابزارهای دیباگ

#### 1. اسکریپت بررسی سلامت ترجمه‌ها
```python
# scripts/check_i18n_health.py
#!/usr/bin/env python3
import os
from pathlib import Path
from flask_babel import Babel

def check_translations():
    translations_dir = Path('app/translations')
    issues = []
    
    # بررسی وجود فایل‌های ضروری
    pot_file = translations_dir / 'messages.pot'
    if not pot_file.exists():
        issues.append("❌ فایل messages.pot وجود ندارد")
    
    # بررسی هر زبان
    for lang_dir in translations_dir.iterdir():
        if lang_dir.is_dir() and lang_dir.name not in ['__pycache__']:
            mo_file = lang_dir / 'LC_MESSAGES' / 'messages.mo'
            po_file = lang_dir / 'LC_MESSAGES' / 'messages.po'
            
            if not po_file.exists():
                issues.append(f"❌ فایل PO برای زبان {lang_dir.name} وجود ندارد")
            
            if not mo_file.exists():
                issues.append(f"⚠️ فایل MO برای زبان {lang_dir.name} وجود ندارد (نیاز به کامپایل)")
            
            # بررسی محتوای PO
            if po_file.exists():
                with open(po_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'Content-Type: text/plain; charset=utf-8' not in content:
                        issues.append(f"⚠️ encoding فایل {lang_dir.name} ممکن است مشکل داشته باشد")
    
    if issues:
        print("مشکلات یافت شده:")
        for issue in issues:
            print(issue)
        return False
    else:
        print("✅ تمام بررسی‌ها با موفقیت انجام شد")
        return True

if __name__ == '__main__':
    check_translations()
```

#### 2. لاگ‌گیری ترجمه‌ها
```python
# در app/__init__.py
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_locale():
    lang = session.get('lang') or request.args.get('lang') or \
           request.accept_languages.best_match(SUPPORTED_LANGUAGES.keys())
    
    logger.debug(f"Detected language: {lang}")
    logger.debug(f"Session: {session.get('lang')}")
    logger.debug(f"Accept-Language header: {request.headers.get('Accept-Language')}")
    
    return lang
```

---

## منابع اضافی

### لینک‌های مفید
- [مستندات رسمی Flask-Babel](https://flask-babel.tureus.com/)
- [مستندات GNU Gettext](https://www.gnu.org/software/gettext/manual/)
- [فونت وزیرمتن](https://github.com/rastikerdar/vazirmatn)
- [راهنمای RTL در CSS](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Logical_Properties)

### ابزارهای کمکی
- **Poedit**: ویرایشگر گرافیکی فایل‌های PO
- **Lokalize**: ابزار مدیریت ترجمه
- **gettext**: ابزارهای خط فرمان GNU

### بهترین روش‌ها
1. همیشه قبل از commit، فایل‌های MO را کامپایل کنید
2. از CI/CD برای بررسی خودکار ترجمه‌ها استفاده کنید
3. ترجمه‌ها را به صورت مداوم به‌روز نگه دارید
4. از مترجم‌های حرفه‌ای برای ترجمه متون مهم استفاده کنید
5. تست‌های i18n را در pipeline تست خود بگنجانید

---

## نتیجه‌گیری

این مستند راهنمای جامعی برای پیاده‌سازی و نگهداری سیستم چندزبانه در پروژه Metisma است. با دنبال کردن این راهنما، می‌توانید:

- ✅ سیستم i18n را به درستی راه‌اندازی کنید
- ✅ ترجمه‌های جدید را به راحتی اضافه کنید
- ✅ مشکلات رایج را عیب‌یابی کنید
- ✅ تجربه کاربری مناسبی برای کاربران فارسی‌زبان فراهم کنید

برای سوالات بیشتر، به تیم توسعه مراجعه کنید یا Issues مربوطه را در مخزن پروژه ثبت نمایید.

---

**نسخه مستند**: 1.0  
**تاریخ به‌روزرسانی**: 2024  
**نگارش شده برای**: پروژه Metisma
