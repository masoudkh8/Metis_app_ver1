# راهنمای سیستم مجوزهای ماژولار (Modular Permission System)

## 📋 معرفی

این سیستم امکان مدیریت دسترسی‌های ریزدانه (Granular Permissions) را برای ۸ نقش کاربری مختلف فراهم می‌کند. شما می‌توانید تعیین کنید که هر گروه کاربری به کدام خدمات دسترسی داشته باشد و کاربران غیر احراز هویت فقط چه بخش‌هایی را ببینند.

---

## 🎯 ویژگی‌های کلیدی

### ۱. **مجوزهای مبتنی بر نقش (Role-Based Permissions)**
هر نقش کاربری به صورت پیش‌فرض مجموعه‌ای از مجوزها را دارد:

| نقش | مجوزهای پیش‌فرض |
|-----|-----------------|
| **Guest** (غیر احراز هویت) | مشاهده محصولات، درباره ما |
| **Buyer** | مشاهده/ثبت/لغو سفارش، کیف پول، داشبورد |
| **Producer** | مشاهده/ویرایش سفارش، لجستیک سفارش‌های خود، داشبورد |
| **Logistics** | مشاهده مأموریت‌ها، به‌روزرسانی وضعیت، اختصاص راننده |
| **Legal** | مشاهده قراردادها، تأیید/رد مدارک |
| **Tech Partner** | مشاهده بازرسی‌ها، ثبت گزارش فنی |
| **Investor** | مشاهده پورتفوی، سرمایه‌گذاری، کیف پول |
| **Corporate Agent** | مشاهده سفارش‌ها، قراردادهای حقوقی |
| **Broker** | مشاهده سفارش‌ها، کمیسیون‌ها، کیف پول |
| **Admin** | تمام مجوزها |

### ۲. **مجوزهای سفارشی (Custom Permissions)**
مدیر سیستم می‌تواند برای هر کاربر، مجوزهای خاصی را فعال یا غیرفعال کند. این مجوزها در فیلد `custom_permissions` در جدول `UserProfile` ذخیره می‌شوند.

### ۳. **داشبورد هوشمند**
داشبورد به صورت پویا بر اساس مجوزهای کاربر، کارت‌های خدمات مرتبط را نمایش می‌دهد.

---

## 🚀 نحوه استفاده

### الف) افزودن دکوریتور به Routeها

```python
from services.access_control import role_required, permission_required
from services.permissions import Permission

# روش ۱: محدودیت بر اساس نقش
@users_bp.route('/logistics/assign')
@login_required
@role_required(Role.LOGISTICS, Role.ADMIN)
def assign_driver():
    # فقط کاربران با نقش LOGISTICS یا ADMIN دسترسی دارند
    pass

# روش ۲: محدودیت بر اساس مجوز (انعطاف‌پذیرتر)
@users_bp.route('/order/create')
@login_required
@permission_required(Permission.ORDER_CREATE)
def create_order():
    # کاربر باید مجوز ORDER_CREATE را داشته باشد
    pass
```

### ب) بررسی دسترسی در Templateها

```html
<!-- نمایش لینک فقط برای کاربران دارای مجوز -->
{% if has_permission(current_user, Permission.ORDER_CREATE) %}
    <a href="/order/create" class="btn btn-primary">ثبت سفارش جدید</a>
{% endif %}

<!-- نمایش ماژول فقط در صورت فعال بودن -->
{% if service_module_enabled('logistics') %}
    <div class="card">
        <h3>خدمات لجستیک</h3>
        <!-- محتوای ماژول لجستیک -->
    </div>
{% endif %}
```

### ج) مدیریت مجوزهای سفارشی

1. وارد پنل مدیریت شوید
2. به مسیر `/users/profile/permissions` بروید
3. کاربر مورد نظر را انتخاب کنید
4. مجوزهای desired را فعال/غیرفعال کنید
5. تغییرات را ذخیره کنید

---

## 📁 ساختار فایل‌ها

```
/workspace
├── services/
│   ├── __init__.py              # صادرات توابع اصلی
│   ├── permissions.py           # تعریف Permission و DEFAULT_ROLE_PERMISSIONS
│   └── access_control.py        # دکوریتورها و توابع کمکی
├── models/
│   └── user.py                  # مدل UserProfile با فیلد custom_permissions
├── routes/users/
│   └── permissions_routes.py    # Routeهای مدیریت مجوزها و داشبورد
├── templates/users/
│   ├── manage_permissions.html  # فرم مدیریت مجوزها
│   └── dashboard.html           # داشبورد هوشمند (ادغام‌شده)
└── docs/
    └── PERMISSION_SYSTEM_GUIDE.md  # این فایل
```

---

## 🔧 لیست کامل مجوزها

### سفارشات (Order)
- `order.view` - مشاهده سفارش‌ها
- `order.create` - ثبت سفارش جدید
- `order.cancel` - لغو سفارش
- `order.edit` - ویرایش سفارش

### لجستیک (Logistics)
- `logistics.view_assigned` - مشاهده مأموریت‌های اختصاص یافته
- `logistics.update_status` - به‌روزرسانی وضعیت حمل
- `logistics.assign_driver` - اختصاص راننده

### حقوقی (Legal)
- `legal.view_contracts` - مشاهده قراردادها
- `legal.approve_docs` - تأیید مدارک
- `legal.reject_docs` - رد مدارک

### مالی (Finance)
- `finance.view_wallet` - مشاهده کیف پول
- `finance.withdraw` - برداشت وجه

### سرمایه‌گذاری (Investment)
- `investment.view_portfolio` - مشاهده پورتفوی
- `investment.commit` - ثبت سرمایه‌گذاری

### فنی (Technical)
- `tech.view_inspections` - مشاهده بازرسی‌ها
- `tech.submit_report` - ثبت گزارش فنی

### داشبورد و پروفایل
- `dashboard.view_stats` - مشاهده آمار داشبورد
- `profile.edit` - ویرایش پروفایل
- `profile.verify_identity` - درخواست احراز هویت

### عمومی (Public)
- `public.view_products` - مشاهده محصولات (بدون نیاز به ورود)
- `public.view_about` - مشاهده صفحه درباره ما

---

## 🎨 مثال عملی: محدود کردن کاربران غیر احراز هویت

برای اینکه کاربران غیر احراز هویت فقط بتوانند محصولات را ببینند:

```python
# در فایل permissions.py
DEFAULT_ROLE_PERMISSIONS = {
    'guest': [
        Permission.PUBLIC_VIEW_PRODUCTS,
        Permission.PUBLIC_VIEW_ABOUT,
    ],
    # ...
}

# در فایل routes/products.py
@products_bp.route('/products')
def list_products():
    # بدون دکوریتور login_required
    # اما با بررسی مجوز در داخل تابع
    from services.access_control import has_permission
    from flask_login import current_user
    
    if not has_permission(current_user, Permission.PUBLIC_VIEW_PRODUCTS):
        abort(403)
    
    # ادامه کد...
```

---

## 🔐 امنیت

- ✅ تمام Routeهای حساس با دکوریتور `@login_required` محافظت می‌شوند
- ✅ بررسی مجوزها هم در سطح Route و هم در سطح Template انجام می‌شود
- ✅ مجوزهای سفارشی فقط توسط Admin قابل تغییر هستند
- ✅ خطاهای دسترسی با پیام‌های واضح به کاربر نمایش داده می‌شوند

---

## 📞 پشتیبانی

برای سؤالات یا مشکلات مربوط به سیستم مجوزها، با تیم توسعه تماس بگیرید.
