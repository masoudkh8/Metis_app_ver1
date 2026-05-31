# 🌍 Global Trade Intelligence Platform - پلتفرم هوشمند تجارت بین‌المللی

## 📋 Overview / معرفی کلی
یک پلتفرم جامع و enterprise-grade برای تجارت بین‌المللی که با **Flask 2.3.3** و **Python 3.11** ساخته شده است. این سیستم شامل ۱۶ بخش کلیدی، ۶۰+ مدل داده‌ای، و ۵۰+ endpoint می‌باشد.

**A comprehensive enterprise-grade platform for international trade built with Flask 2.3.3 and Python 3.11, featuring 16 core modules, 60+ data models, and 50+ endpoints.**

---

## ✨ ویژگی‌های کلیدی / Key Features

### 👤 مدیریت پیشرفته کاربران / Advanced User Management
- **مدل کاربر غنی‌شده**: فیلدهای تخصصی بر اساس نقش (expertise_area, company_name, job_title, bio, website, social_links)
- **ثبت‌نام هوشمند ۳ مرحله‌ای**: فرم پویا با اعتبارسنجی پیشرفته و پسورد قوی
- **داشبورد نقش‌محور**: ویجت‌های سفارشی برای هر نقش (PRODUCER, INVESTOR, EXPERT, EXHIBITOR)
- **پروفایل پیشرفته**: ویرایش اطلاعات، آپلود مدارک، لینک‌های اجتماعی
- **سیستم امتیاز اعتماد (Trust Score)**: الگوریتم پویا با سطوح Bronze/Silver/Gold/Platinum
- **کنترل دسترسی (RBAC)**: دکوریتور @role_required برای محدودیت دسترسی
- **Rate Limiting**: محافظت در برابر سوءاستفاده (۵ درخواست در دقیقه)
- **آپلود امن مدارک**: اعتبارسنجی چندلایه (پسوند، MIME، حجم، نام امن)

### 🧠 هوش مصنوعی و تحلیل داده / AI & Data Intelligence
- **AI Core**: گفتگوی هوشمند، توصیه‌های تجاری، تولید محتوا
- **Smart Map**: اطلاعات گمرکی، تحلیل ریسک، مسیرهای تجاری
- **Data Intelligence**: پیش‌بینی تقاضا، تحلیل بازار، شناسایی فرصت‌ها

### 💼 ابزارهای تجاری / Business Tools
- **Marketplace**: مدیریت محصولات، درخواست‌ها، پیشنهادات
- **TradeCredit**: حساب‌های اعتباری تجاری
- **Consortium**: پروژه‌های انجمنی و قراردادهـا
- **CRM & Leads**: مدیریت مشتریان و کمپین‌ها

### 🎮 تعامل و یادگیری / Engagement & Learning
- **Gamification**: مدال‌ها، چالش‌ها، سیستم پیشرفت
- **Trust Stack**: امتیاز اعتماد چهارلایه‌ای
- **Learning Hub**: دوره‌ها، گواهینامه‌ها، مسیرهای یادگیری

### 🔐 امنیت و زیرساخت / Security & Infrastructure
- **Auth & RBAC**: احراز هویت پیشرفته، مدیریت نقش‌ها
- **Feature Flags**: سیستم هدف‌گیری پیشرفته
- **Rate Limiting & Caching**: مبتنی بر Redis
- **Monitoring**: endpointهای سلامت و متریک
- **i18n**: چندزبانه (فارسی و انگلیسی)

---

## 🏗️ معماری سیستم / System Architecture

| لایه | فناوری | توضیحات |
|------|--------|---------|
| **Backend** | Flask 2.3.3 + Python 3.11 | RESTful API، Jinja2 Templates |
| **Database** | PostgreSQL 15 | ۶۰+ مدل، روابط پیچیده |
| **Cache/Queue** | Redis 7 + Celery 5.4.0 | پردازش ناهمگام، کشینگ |
| **Frontend** | Tailwind CSS 4.3 + HTML5 | ۳۱ قالب responsive، PWA |
| **Containerization** | Docker + Docker Compose | ۶ سرویس مجزا |

---

## 🚀 راه‌اندازی سریع / Quick Setup

### روش ۱: Docker (توصیه شده) / Method 1: Docker (Recommended)
```bash
# کپی کردن فایل محیطی
cp .env.example .env

# اجرای تمام سرویس‌ها
docker-compose up -d

# مشاهده لاگ‌ها
docker-compose logs -f
```

### روش ۲: نصب محلی / Method 2: Local Installation

#### ۱. نصب پیش‌نیازها / Install Prerequisites
```bash
pip install -r requirements.txt
npm install
```

#### ۲. تنظیم دیتابیس PostgreSQL / Setup PostgreSQL Database
```bash
# ایجاد دیتابیس
sudo -u postgres psql -c "CREATE DATABASE ports_db;"
sudo -u postgres psql -c "CREATE USER postgres WITH PASSWORD 'postgres';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ports_db TO postgres;"
```

#### ۳. پیکربندی فایل `.env` / Configure `.env` File
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ports_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

#### ۴. اجرای Migrationها / Run Migrations
```bash
flask db upgrade
```

#### ۵. ساخت Tailwind CSS / Build Tailwind CSS
```bash
python build_tailwind.py
# یا
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify
```

#### ۶. بارگذاری داده‌های اولیه / Load Initial Data (Optional)
```bash
python init_postgres_db.py
python load_ports_to_postgres.py
```

#### ۷. اجرای برنامه / Run Application
```bash
# توسعه
python app.py

# Production
gunicorn wsgi:app -b 0.0.0.0:5000 --workers 4
```

---

## 📦 ماژول‌ها و مدل‌ها / Modules & Models

### مدل‌های اصلی / Core Models
- **User**: کاربران، نقش‌ها، پروفایل‌ها
- **Product**: محصولات، دسته‌بندی‌ها، موجودی
- **Order**: سفارشات، وضعیت‌ها، پرداخت‌ها
- **Wallet**: کیف پول، تراکنش‌ها، نرخ تبدیل
- **TrustScore**: امتیاز اعتماد چهارلایه‌ای
- **Gamification**: مدال‌ها، چالش‌ها، امتیازات

### مدل‌های تخصصی / Specialized Models
- **Port**: اطلاعات بنادر و گمرکات
- **SmartMap**: داده‌های جغرافیایی و ریسک
- **Consortium**: پروژه‌های انجمنی
- **TradeCredit**: اعتبارات تجاری
- **Course**: دوره‌های آموزشی
- **Magazine**: مقالات و مجلات
- **Lead**: سرنخ‌های تجاری
- **Message**: پیام‌ها و چت
- **Notification**: اعلان‌ها

---

## 🛠️ اسکریپت‌های کاربردی / Useful Scripts

| اسکریپت | کاربرد |
|---------|--------|
| `init_postgres_db.py` | ایجاد جداول خالی |
| `load_ports_to_postgres.py` | بارگذاری داده‌های بندر |
| `view_db.py` | مشاهده دیتابیس |
| `build_tailwind.py` | کامپایل Tailwind CSS |
| `compile_translations.py` | کامپایل ترجمه‌ها |
| `celery_app.py` | اجرای workerهای Celery |

---

## 🧪 تست و دیباگ / Testing & Debugging

```bash
# اجرای تست‌ها
pytest tests/ -v

# با پوشش کد
pytest tests/ --cov=app --cov-report=html

# مشاهده coverage
coverage html
```

---

## 📚 مستندات کامل / Full Documentation

| مستند | توضیحات |
|-------|---------|
| `ADVANCED_USER_FEATURES.md` | 🆕 مستندات ویژگی‌های پیشرفته کاربران (ثبت‌نام، پروفایل، داشبورد، Trust Score) |
| `POSTGRES_GUIDE.md` | راهنمای کامل PostgreSQL |
| `PRODUCTION_SETUP_GUIDE.md` | راهنمای استقرار در Production |
| `FEATURE_FLAG_CICD_GUIDE.md` | راهنمای Feature Flags |
| `API_DOCUMENTATION.md` | مستندات API |
| `IMPLEMENTATION_ROADMAP.md` | نقشه راه پیاده‌سازی |
| `MODELS_SUMMARY.md` | خلاصه مدل‌ها |
| `README_TRANSLATION.md` | راهنمای ترجمه و چندزبانه |
| `FALLBACK_MECHANISM.md` | مکانیزم fallback |
| `OFFLINE_MODE_SUMMARY.md` | حالت آفلاین |

---

## 🌐 Routes و Endpoints

### Users Routes
- `/` - Landing Page
- `/register` - ثبت‌نام
- `/login` - ورود
- `/profile` - پروفایل کاربری
- `/orders` - سفارشات
- `/chat` - چت

### Admin Routes
- `/admin/dashboard` - داشبورد مدیریت
- `/admin/users` - مدیریت کاربران
- `/admin/approvals` - تأییدیه‌ها

### Magazine Routes
- `/magazine` - مجله
- `/magazine/subscribe` - اشتراک
- `/magazine/ads` - تبلیغات

---

## 🐳 Docker Services

| سرویس | پورت | توضیحات |
|-------|------|---------|
| `web` | 5000 | Flask Application |
| `celery` | - | Celery Worker |
| `redis` | 6379 | Redis Cache/Queue |
| `postgres` | 5432 | PostgreSQL Database |
| `pgadmin` | 5050 | مدیریت دیتابیس |
| `flower` | 5555 | مانیتورینگ Celery |

---

## 🎨 UI/UX Features

- **۳۱ قالب HTML** با طراحی responsive
- **Tailwind CSS 4.3** با custom configuration
- **Dark Mode** support
- **PWA** capabilities
- **Multi-language** (FA/EN)
- **Professional Color Palette** برای ۵ بخش خدماتی:
  - Trade & Finance: `#1e3a8a` (آبی تیره)
  - Logistics: `#0f766e` (فیروزه‌ای تیره)
  - Analytics & AI: `#4c1d95` (بنفش تیره)
  - Business Tools: `#065f46` (سبز تیره)
  - Learning & Engagement: `#9a3412` (نارنجی تیره)

---

## 📊 آمار پروژه / Project Statistics

- **۵۴ فایل Python** (+ مدل‌های پیشرفته کاربر)
- **۴۳ قالب HTML** (+ register_dynamic.html, profile_edit.html, dashboard_*.html)
- **۴۵ مستندات Markdown** (+ ADVANCED_USER_FEATURES.md)
- **۲۲ فایل مدل داده‌ای**
- **۱۰,۴۶۳+ خط کد Python**
- **۶۰+ مدل داده‌ای**
- **۵۰+ endpoint** (+ endpointهای کاربران، پروفایل، داشبورد)
- **~45MB حجم پروژه**

---

## 🔒 امنیت / Security

- ✅ CSRF Protection
- ✅ Password Hashing (bcrypt)
- ✅ Role-Based Access Control (RBAC) - **دکوریتور @role_required**
- ✅ Rate Limiting - **۵ درخواست در دقیقه روی ثبت‌نام**
- ✅ Input Validation - **اعتبارسنجی پیشرفته فرم‌ها**
- ✅ SQL Injection Prevention
- ✅ XSS Protection
- ✅ Secure File Upload - **اعتبارسنجی چندلایه مدارک**
- ✅ Trust Score System - **سیستم امتیاز اعتماد پویا**

---

## 🚀 Production Deployment

### الزامات / Requirements
- SSL/TLS Certificate
- Domain Configuration
- Backup Strategy (Daily/Weekly)
- Monitoring Setup (Prometheus/Grafana)
- Load Balancer (Nginx/HAProxy)

### دستورات استقرار / Deployment Commands
```bash
# Build Docker images
docker-compose build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose exec web flask db upgrade

# Restart services
docker-compose restart
```

---

## 🤝 مشارکت / Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 لایسنس / License

این پروژه تحت لایسنس خصوصی است.

---

## 📞 پشتیبانی / Support

برای سوالات و پشتیبانی:
- 📧 Email: support@example.com
- 📚 Documentation: `/docs` directory
- 🐛 Issues: GitHub Issues

---

## 🔄 به‌روزرسانی‌های اخیر / Recent Updates

- ✅ **ویژگی‌های پیشرفته کاربران**: مدل کاربر غنی‌شده، ثبت‌نام ۳ مرحله‌ای، داشبورد نقش‌محور، پروفایل پیشرفته
- ✅ **سیستم Trust Score**: امتیاز اعتماد پویا با سطوح Bronze/Silver/Gold/Platinum
- ✅ **امنیت**: Rate Limiting، دکوریتور @role_required، آپلود امن مدارک
- ✅ **مستندات جدید**: `ADVANCED_USER_FEATURES.md` با جزئیات کامل API و ویژگی‌ها
- ✅ **ترجمه**: بیش از ۵۰ کلید جدید برای بخش‌های ثبت‌نام، پروفایل و اعتبارسنجی
- ✅ افزودن رنگ‌بندی حرفه‌ای به ۵ بخش خدماتی در هدر
- ✅ بهبود UX/UI منوی همبرگر موبایل
- ✅ بهینه‌سازی Transitionها و Hover effects
- ✅ افزودن پشتیبانی از Dark Mode
- ✅ بهبود Performance با Caching

---

<div align="center">

**ساخته شده با ❤️ برای تجارت بین‌المللی**

**Built with ❤️ for Global Trade**

</div>
