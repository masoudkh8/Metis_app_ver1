# Language Switcher Component for Metisma
# Add this to your base template to enable language switching

"""
نحوه استفاده در قالب‌ها:

1. افزودن سوئیچر زبان به template/base.html یا هر قالب دیگری:

```html
<!-- Language Switcher -->
<div class="language-switcher">
    <a href="?lang=fa_IR" class="{{ 'active' if current_locale == 'fa_IR' else '' }}">
        🇮🇷 فارسی
    </a>
    <a href="?lang=en" class="{{ 'active' if current_locale == 'en' else '' }}">
        🇬🇧 English
    </a>
</div>
```

2. استفاده از تابع ترجمه در قالب‌ها:

```html
<h1>{{ _('Welcome to Metisma') }}</h1>
<p>{{ _('Login') }} | {{ _('Register') }}</p>
```

3. تغییر زبان در کد Python:

```python
from flask import session
session['lang'] = 'fa_IR'  # یا 'en'
```

"""

# نمونه کد برای افزودن به templates/base.html
LANGUAGE_SWITCHER_HTML = """
<!-- Language Switcher - Start -->
<nav class="language-switcher" dir="rtl">
    <style>
        .language-switcher {
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 1000;
            display: flex;
            gap: 8px;
            background: rgba(255, 255, 255, 0.9);
            padding: 8px 12px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .language-switcher a {
            text-decoration: none;
            padding: 6px 12px;
            border-radius: 4px;
            font-weight: 500;
            transition: all 0.3s ease;
            color: #333;
        }
        
        .language-switcher a:hover {
            background: #f0f0f0;
        }
        
        .language-switcher a.active {
            background: #007bff;
            color: white;
        }
        
        /* RTL Support */
        [dir="rtl"] {
            direction: rtl;
            text-align: right;
        }
        
        [dir="ltr"] {
            direction: ltr;
            text-align: left;
        }
    </style>
    
    <a href="?lang=fa_IR" 
       class="{{ 'active' if current_locale == 'fa_IR' else '' }}"
       title="Persian">
       🇮🇷 فارسی
    </a>
    <a href="?lang=en" 
       class="{{ 'active' if current_locale == 'en' else '' }}"
       title="English">
       🇬🇧 English
    </a>
</nav>
<!-- Language Switcher - End -->
"""

# نمونه استفاده در Flask routes
ROUTE_EXAMPLE = """
@users_bp.route('/set_language/<lang>')
def set_language(lang):
    '''Change user language'''
    if lang in ['fa_IR', 'en']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('users.profile'))
"""
