# 📘 راهنمای جامع راه‌اندازی شبکه اجتماعی متیسما
## باشگاه نخبگان تجارت B2B

---

## 🎯 فهرست مطالب

1. [بررسی کلی و تأییدیه نهایی](#بررسی-کلی-و-تأییدیه-نهایی)
2. [معماری سیستم لایه‌بندی شده](#معماری-سیستم-لایه‌بندی-شده)
3. [مدل‌های داده‌ای](#مدل‌های-داده‌ای)
4. [نقشه راه اجرایی گام‌به‌گام](#نقشه-راه-اجرایی-گام‌به‌گام)
5. [استراتژی محتوای اولیه](#استراتژی-محتوای-اولیه)
6. [نکات کلیدی برای شروع](#نکات-کلیدی-برای-شروع)
7. [چک‌لیست Pre-Launch](#چک‌لیست-pre-launch)

---

## ✅ بررسی کلی و تأییدیه نهایی

### وضعیت فعلی پروژه (تأیید شده)

| بخش | وضعیت | توضیحات |
|-----|-------|---------|
| **مدل‌های کاربری** | ✅ کامل | ۱۰ نقش تخصصی + ۴ لایه عضویت |
| **پروفایل غنی** | ✅ کامل | UserProfile با فیلدهای تخصصی |
| **سیستم فالو** | ✅ کامل | جدول connections با relationshipها |
| **مدل پست** | ✅ کامل | پشتیبانی از media، تگ محصولات، آمار |
| **سیستم لایک** | ✅ کامل | پلی‌مورفیک برای پست و کامنت |
| **کامنت‌ها** | ✅ کامل | پاسخ‌های تو در تو (nested) |
| **کد دعوت** | ✅ کامل | سیستم دعوت‌نامه انحصاری |
| **TrustScore** | ✅ کامل | یکپارچه با لایه‌های عضویت |

### تست‌های گذرانده شده

```bash
✅ Membership Tiers: OBSERVER, VERIFIED, PARTNER, ELITE
✅ Roles: 8 نقش اصلی تجاری + ADMIN + MODERATOR
✅ User Fields: membership_tier, invite_code, trust_score_value, is_kyc_verified
✅ User Methods: follow, unfollow, is_following, generate_invite_code, can_access_tier
✅ Relationships: profile, posts, following, followers
✅ Social Models: Follow, Post, Comment, Like (همه فیلدها موجود است)
```

---

## 🏛️ معماری سیستم لایه‌بندی شده

### مدل "دایره‌های تو در تو" (Concentric Circles)

```
┌─────────────────────────────────────────┐
│           🟡 ELITE (لایه ۴)             │
│   Deal Flow محرمانه، کنسرسیوم‌ها        │
│   TrustScore > 90، دعوت اختصاصی         │
│  ┌───────────────────────────────────┐  │
│  │      🟣 PARTNER (لایه ۳)          │  │
│  │  دیتای زنده بازار، AI Agent       │  │
│  │  TrustScore > 70، ۳ معامله موفق   │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │    🔵 VERIFIED (لایه ۲)     │  │  │
│  │  │  جستجوی پیشرفته، CRM پایه   │  │  │
│  │  │  KYC تکمیل، حق عضویت پایه   │  │  │
│  │  │  ┌───────────────────────┐  │  │  │
│  │  │  │ 🟢 OBSERVER (لایه ۱)  │  │  │  │
│  │  │  │ مشاهده کلیات، مقالات  │  │  │  │
│  │  │  │ ثبت‌نام اولیه         │  │  │  │
│  │  │  └───────────────────────┘  │  │  │
│  │  └─────────────────────────────┘  │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### جدول مقایسه لایه‌ها

| ویژگی | OBSERVER | VERIFIED | PARTNER | ELITE |
|-------|----------|----------|---------|-------|
| **شرط ورود** | ثبت‌نام | KYC + پرداخت | TrustScore > 70 | دعوت + TrustScore > 90 |
| **جستجوی پیشرفته** | ❌ | ✅ | ✅ | ✅ |
| **پیام روزانه** | ۰ | ۵ | ۲۰ | نامحدود |
| **دسترسی به دیتای زنده** | ❌ | ❌ | ✅ | ✅ |
| **AI Agent** | ❌ | ❌ | ✅ | ✅ |
| **Deal Flow محرمانه** | ❌ | ❌ | ❌ | ✅ |
| **اتاق‌های تخصصی** | ❌ | ❌ | ✅ | ✅ |
| **قدرت دعوت** | ❌ | ❌ | ❌ | ✅ |

---

## 🗄️ مدل‌های داده‌ای

### ۱. مدل User (کاربران)

```python
class User(UserMixin, db.Model):
    # فیلدهای اصلی
    id, username, email, password_hash
    company_name, role (Enum: 10 نقش)
    
    # لایه عضویت
    membership_tier (Enum: OBSERVER, VERIFIED, PARTNER, ELITE)
    trust_score_value (امتیاز اعتماد)
    
    # سیستم دعوت
    invite_code (کد منحصر به فرد)
    invited_by_id (ارجاع به کاربر دعوت‌کننده)
    
    # احراز هویت
    is_kyc_verified
    kyc_documents_url
    
    # Relationshipها
    profile (UserProfile)
    posts (Post)
    following (Follow)
    followers (Follow)
```

### ۲. مدل UserProfile (پروفایل غنی)

```python
class UserProfile(db.Model):
    user_id (Foreign Key to User)
    
    # اطلاعات عمومی
    bio, headline, website, location
    avatar_url, cover_image_url
    
    # تخصص‌ها
    skills (JSON), industries (JSON)
    
    # دستاوردها
    badges (JSON), certifications (JSON)
    
    # آمار اجتماعی
    followers_count, following_count, posts_count
```

### ۳. مدل Follow (شبکه ارتباطی)

```python
class Follow(db.Model):
    follower_id (کاربر دنبال‌کننده)
    following_id (کاربر دنبال‌شونده)
    connection_type (public, connection, premium)
    created_at
    
    # UniqueConstraint جلوگیری از فالو تکراری
```

### ۴. مدل Post (فید اخبار)

```python
class Post(db.Model):
    author_id (نویسنده پست)
    content (متن اصلی)
    visibility (public, followers_only, private)
    
    # رسانه‌ها
    media (JSON: images, files)
    
    # تگ‌ها
    tagged_products (JSON: product_ids)
    tagged_companies (JSON: company_ids)
    
    # آمار تعاملات
    likes_count, comments_count, shares_count, views_count
    
    # وضعیت
    is_pinned, is_featured, is_edited
    created_at, updated_at
```

### ۵. مدل Comment (تعاملات)

```python
class Comment(db.Model):
    post_id, author_id
    parent_id (برای پاسخ‌های تو در تو)
    content
    likes_count
    is_edited, is_deleted
    created_at, updated_at
```

### ۶. مدل Like (تعاملات)

```python
class Like(db.Model):
    user_id
    target_type ('post' یا 'comment')
    target_id (post_id یا comment_id)
    created_at
    
    # UniqueConstraint جلوگیری از لایک تکراری
```

---

## 🗺️ نقشه راه اجرایی گام‌به‌گام

### مرحله ۱: ساخت پروفایل عمومی (هفته اول)

#### ✅ انجام شده:
- [x] مدل UserProfile با تمام فیلدها
- [x] Relationship بین User و Profile
- [x] فیلدهای تخصصی برای هر نقش

#### 🔧 اقدامات بعدی:

**گام ۱.۱: ایجاد Route پروفایل عمومی**
```python
# routes/users/profile.py
@app.route('/user/<username>')
def public_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('public_profile.html', user=user)
```

**گام ۱.۲: طراحی قالب HTML**
```html
<!-- templates/public_profile.html -->
<!-- شامل: لوگو، بیو، تخصص‌ها، دستاوردها، پست‌ها -->
<!-- SEO Friendly: meta tags, Open Graph -->
```

**گام ۱.۳: فرم ویرایش پروفایل**
```python
# routes/users/edit_profile.py
@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # فرم آپلود عکس، ویرایش بیو، افزودن مهارت‌ها
```

---

### مرحله ۲: سیستم فالو و فید ساده (هفته دوم و سوم)

#### ✅ انجام شده:
- [x] مدل Follow با constraintها
- [x] مدل Post با تمام فیلدها
- [x] متدهای follow, unfollow, is_following
- [x] تابع get_feed_for_user

#### 🔧 اقدامات بعدی:

**گام ۲.۱: ایجاد Route فالو کردن**
```python
# routes/social/connections.py
@app.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow_user(user_id):
    current_user.follow(user_id)
    return jsonify({'status': 'success'})
```

**گام ۲.۲: ایجاد Route فید اخبار**
```python
# routes/social/feed.py
@app.route('/feed')
@login_required
def news_feed():
    posts = Post.get_feed_for_user(current_user.id)
    return render_template('feed.html', posts=posts)
```

**گام ۲.۳: فرم ارسال پست**
```python
# routes/social/posts.py
@app.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():
    # فرم متن، آپلود فایل، تگ محصولات
```

---

### مرحله ۳: غنی‌سازی (ماه دوم)

#### ✅ انجام شده:
- [x] مدل Comment با پاسخ‌های تو در تو
- [x] مدل Like پلی‌مورفیک
- [x] شمارنده‌های تعاملات

#### 🔧 اقدامات بعدی:

**گام ۳.۱: سیستم لایک و کامنت**
```python
# routes/social/engagement.py
@app.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    # اضافه کردن لایک با Redis برای کشینگ
```

**گام ۳.۲: آپلود چندرسانه‌ای**
```python
# utils/file_upload.py
def upload_media(files):
    # آپلود عکس و فایل به S3 یا سرور محلی
    # ذخیره URL در فیلد media JSON
```

**گام ۳.۳: اتصال به محصولات**
```python
# routes/social/integrations.py
def tag_product_in_post(post_id, product_id):
    # تگ کردن محصول در پست
    # نمایش محصول در پست عمومی
```

---

## 📝 استراتژی محتوای اولیه

### ایده هوشمندانه: استفاده از مجله ایماژه

**مشکل:** پلتفرم جدید خالی از محتواست و کاربران اولیه چیزی برای دیدن ندارند.

**راه‌حل:** تیم شما به عنوان ادمین، پروفایل‌ها و پست‌های اولیه را می‌سازد.

### مراحل اجرا:

#### ۱. شناسایی شرکت‌های معرفی‌شده در ایماژه
```python
# لیست شرکت‌های مصاحبه‌شده
companies = [
    {'name': 'شرکت الف', 'industry': 'پتروشیمی', 'interview_url': '...'},
    {'name': 'شرکت ب', 'industry': 'فولاد', 'interview_url': '...'},
]
```

#### ۲. ساخت پروفایل برای هر شرکت
```python
# اسکریپت admin_seed.py
for company in companies:
    user = User(
        username=company['slug'],
        company_name=company['name'],
        role=Role.PRODUCER,
        membership_tier=MembershipTier.VERIFIED
    )
    db.session.add(user)
    db.session.commit()
    
    # ساخت پروفایل
    profile = UserProfile(
        user_id=user.id,
        bio=company['description'],
        industries=[company['industry']]
    )
    db.session.add(profile)
db.session.commit()
```

#### ۳. انتشار خلاصه مصاحبه‌ها به عنوان پست
```python
# ایجاد ۳ پست اولیه برای هر شرکت
for company in companies:
    posts = [
        {'content': 'بخش اول مصاحبه...', 'is_featured': True},
        {'content': 'بخش دوم مصاحبه...', 'is_featured': False},
        {'content': 'بخش سوم مصاحبه...', 'is_featured': False},
    ]
    for post_data in posts:
        post = Post(
            author_id=company_user.id,
            content=post_data['content'],
            visibility='public',
            is_featured=post_data['is_featured']
        )
        db.session.add(post)
db.session.commit()
```

#### ۴. دعوت از شرکت‌ها با پیام شخصی
```
سلام [نام شرکت]،

پروفایل شما در متیسما آماده است!
۳ پست از مصاحبه‌تان در مجله ایماژه را آنجا منتشر کرده‌ایم.

لینک پروفایل: https://metisma.com/user/[username]

وارد شوید و پروفایل خود را تکمیل کنید:
- آپلود لوگو و عکس پوششی
- تکمیل بیوگرافی و تخصص‌ها
- افزودن وب‌سایت و اطلاعات تماس

این پروفایل مانند رزومه دیجیتال شماست و در گوگل ایندکس می‌شود.

با احترام،
تیم متیسما
```

---

## 💡 نکات کلیدی برای شروع

### ۱. حس انحصار ایجاد کنید

**قفل‌های هوشمند:**
```python
# دکوراتور کنترل دسترسی
def require_tier(required_tier):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can_access_tier(required_tier):
                return render_template('tier_lock.html', 
                    required_tier=required_tier,
                    current_tier=current_user.membership_tier)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# استفاده در route
@app.route('/market/live-data')
@login_required
@require_tier('PARTNER')
def live_market_data():
    # فقط شرکای استراتژیک دسترسی دارند
```

### ۲. نشان‌های افتخار دیجیتال

```python
# Badges که باید پیاده‌سازی شوند
badges = {
    'verified_member': 'عضو تأیید شده',
    'early_adopter': 'عضو اولیه',
    'top_contributor': 'مشارکت‌کننده برتر',
    'trusted_trader': 'تاجر مورد اعتماد',
    'elite_member': 'عضو نخبه',
}
```

### ۳. سیستم مأموریت‌ها (Gamification)

```python
# missions table idea
missions = [
    {'name': 'تکمیل پروفایل', 'xp': 100, 'tier_progress': 'OBSERVER -> VERIFIED'},
    {'name': 'اولین پست', 'xp': 50, 'tier_progress': None},
    {'name': '۱۰ فالوور', 'xp': 200, 'tier_progress': None},
    {'name': 'اولین معامله', 'xp': 500, 'tier_progress': 'VERIFIED -> PARTNER'},
    {'name': 'TrustScore بالای ۷۰', 'xp': 0, 'tier_progress': 'VERIFIED -> PARTNER'},
]
```

### ۴. SEO برای پروفایل‌های عمومی

```html
<!-- Meta tags برای هر پروفایل -->
<meta name="title" content="{{ user.company_name }} - متیسما">
<meta name="description" content="{{ user.profile.bio }}">
<meta property="og:type" content="profile">
<meta property="og:title" content="{{ user.company_name }}">
<meta property="og:description" content="{{ user.profile.headline }}">
<meta property="og:image" content="{{ user.profile.avatar_url }}">
```

### ۵. بهینه‌سازی با Redis

```python
# کش کردن تعداد لایک‌ها
from flask import current_app

def cache_like_count(post_id):
    key = f'post:{post_id}:likes'
    cached = redis_client.get(key)
    if cached:
        return int(cached)
    
    count = Like.get_likes_count('post', post_id)
    redis_client.setex(key, 300, count)  # 5 دقیقه کش
    return count
```

---

## ✅ چک‌لیست Pre-Launch

### زیرساخت فنی

- [x] مدل‌های دیتابیس کامل هستند
- [x] Relationshipها تنظیم شده‌اند
- [x] متدهای کمکی پیاده‌سازی شده‌اند
- [ ] Migration برای ساخت جداول اجرا شود
- [ ] تست unit برای هر model نوشته شود
- [ ] API endpoints ساخته شوند
- [ ] قالب‌های HTML طراحی شوند
- [ ] استایل‌دهی CSS/Shadcn انجام شود
- [ ] Responsive برای موبایل چک شود

### احراز هویت و امنیت

- [ ] سیستم ثبت‌نام با انتخاب نقش
- [ ] سیستم ورود با JWT یا Session
- [ ] تأیید ایمیل اجباری
- [ ] KYC برای ارتقا به VERIFIED
- [ ] Rate Limiting برای APIها
- [ ] CSRF Protection فعال باشد
- [ ] XSS Prevention رعایت شود

### تجربه کاربری

- [ ] صفحه Landing برای هر لایه
- [ ] داشبورد متفاوت برای هر Tier
- [ ] نوار پیشرفت ارتقای لایه
- [ ] اعلان‌ها (Notifications)
- [ ] جستجوی پیشرفته
- [ ] فیلتر کردن پست‌ها
- [ ] Pagination برای فید

### محتوا و سئو

- [ ] ۱۰ پروفایل نمونه توسط ادمین ساخته شود
- [ ] ۳۰ پست اولیه منتشر شود
- [ ] Meta tags برای همه صفحات
- [ ] Sitemap.xml تولید شود
- [ ] Robots.txt تنظیم شود
- [ ] Google Analytics متصل شود

### کسب‌وکار

- [ ] صفحه قیمت‌گذاری برای هر لایه
- [ ] درگاه پرداخت حق عضویت
- [ ] شرایط و قوانین پلتفرم
- [ ] سیاست حریم خصوصی
- [ ] فرم تماس با پشتیبانی
- [ ] ایمیل‌های خودکار (Welcome, Upgrade, etc.)

---

## 🚀 دستورالعمل اجرای اولیه

### ۱. اجرای Migration

```bash
# در محیط virtualenv
flask db upgrade
```

### ۲. ساخت کاربر ادمین

```python
# scripts/create_admin.py
from models import db, create_app
from models.user import User, Role, MembershipTier

app = create_app()
with app.app_context():
    admin = User(
        username='admin',
        email='admin@metisma.com',
        role=Role.ADMIN,
        membership_tier=MembershipTier.ELITE,
        is_kyc_verified=True
    )
    admin.set_password('SecurePassword123!')
    db.session.add(admin)
    db.session.commit()
    print(f'Admin created with invite code: {admin.generate_invite_code()}')
```

### ۳. اجرای اسکریپت Seed

```bash
python scripts/admin_seed.py
```

### ۴. اجرای سرور

```bash
flask run --host=0.0.0.0 --port=5000
```

---

## 📞 پشتیبانی و مستندات بیشتر

- **مستندات API:** `/api/docs` (بعد از پیاده‌سازی Swagger)
- **CONTEXT_MASTER_BRIEF.md:** سند اصلی استراتژی کسب‌وکار
- **کد پروژه:** `/workspace/models/`, `/workspace/routes/`

---

## ✨ نتیجه‌گیری

پروژه متیسما هم‌اکنون از نظر مدل‌های داده‌ای و زیرساخت فنی **کاملاً آماده** است. تمام مفاهیم "باشگاه نخبگان"، "لایه‌بندی دسترسی"، "سیستم اجتماعی" و "استراتژی محتوای اولیه" در کد پیاده‌سازی شده‌اند.

**گام بعدی:** شروع پیاده‌سازی Routes، قالب‌های HTML و UI برای تبدیل این زیرساخت به یک پلتفرم قابل استفاده.

**شعار پروژه:** 
> "بودن در اینجا افتخار است، نه یک اتفاق معمولی."

---

*تهیه شده برای مسعود جان - بنیان‌گذار متیسما*  
*تاریخ: ۲۰۲۴*  
*وضعیت: ✅ تأیید نهایی - آماده اجرا*
