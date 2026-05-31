# 📚 مدل‌های نمایشگاه آنلاین و تالار معاملاتی متیما

## ✅ تفکیک‌سازی انجام شد

مدل‌های داده‌ای به دو بخش **کاملاً مستقل** تقسیم شدند:

```
models/
├── exhibition/          # نمایشگاه آنلاین
│   └── __init__.py     (۸ مدل - ۳۴۲ خط کد)
│
├── trading/            # تالار معاملاتی  
│   └── __init__.py     (۱۰ مدل - ۴۶۳ خط کد)
│
└── __init__.py         # فایل اصلی ایمپورت
```

---

## 🏛️ مدل‌های نمایشگاه آنلاین (Exhibition Hall)

### مدل‌های اصلی (۶ عدد):

| مدل | جدول | توضیح |
|-----|------|-------|
| `Exhibition` | exhibitions | نمایشگاه‌های کلی با زمان‌بندی و تنظیمات |
| `Booth` | booths | غرفه‌های مجازی با پشتیبانی از ۳D |
| `BoothVisit` | booth_visits | ثبت بازدید کاربران از غرفه‌ها |
| `BoothInteraction` | booth_interactions | تعاملات (پیام، استعلام، درخواست تماس) |
| `BoothAppointment` | booth_appointments | قرارهای ملاقات و جلسات |
| `ExhibitionVisit` | exhibition_visits | بازدید کلی از نمایشگاه |

### جداول Lookup (۲ عدد):

| مدل | جدول | مقادیر |
|-----|------|--------|
| `ExhibitionStatus` | exhibition_status_enum | draft, upcoming, active, paused, completed, cancelled |
| `BoothType` | booth_type_enum | standard, premium, vip, 3d, interactive |

### ویژگی‌های کلیدی:
- ✅ **Polymorphic Ownership**: غرفه می‌تواند متعلق به company، user یا brand باشد
- ✅ **موقعیت‌دهی ۲بعدی**: `location_x`, `location_y` برای چیدمان غرفه‌ها
- ✅ **پشتیبانی ۳D**: فیلدهای `model_3d_url`, `model_3d_config`
- ✅ **JSONB Fields**: برای ذخیره انعطاف‌پذیر گالری، محصولات، تنظیمات
- ✅ **سئو کامل**: `slug`, `seo_metadata`
- ✅ **آمارگیری**: `view_count`, `interaction_count`, `lead_count`

---

## 💹 مدل‌های تالار معاملاتی (Trading Hall)

### مدل‌های اصلی (۷ عدد):

| مدل | جدول | توضیح |
|-----|------|-------|
| `TradingPair` | trading_pairs | جفت‌های معاملاتی (BTC/USDT, GOLD/USD) |
| `TradingWallet` | trading_wallets | کیف پول چندارزی کاربران |
| `WalletTransaction` | wallet_transactions | تاریخچه تراکنش‌های کیف پول |
| `TradeOrder` | trade_orders | سفارش‌های خرید/فروش |
| `Trade` | trades | معاملات انجام‌شده (مچ شده) |
| `MarketData` | market_data | داده‌های کندل‌های قیمتی (OHLCV) |
| `TradingSetting` | trading_settings | تنظیمات سیستمی تالار |

### جداول Lookup (۳ عدد):

| مدل | جدول | مقادیر |
|-----|------|--------|
| `OrderType` | order_type_enum | market, limit, stop_limit, stop_market |
| `OrderSide` | order_side_enum | buy, sell |
| `OrderStatus` | order_status_enum | pending, partially_filled, filled, cancelled, rejected, expired |

### ویژگی‌های کلیدی:
- ✅ **انواع سفارش**: Market, Limit, Stop-Limit, Stop-Market
- ✅ **Time in Force**: GTC, IOC, FOK
- ✅ **مدیریت ریسک**: `daily_loss_limit`, `risk_level`
- ✅ **کارمزدها**: `maker_fee`, `taker_fee`
- ✅ **دقت بالا**: `Numeric(20, 8)` برای قیمت‌ها و مقادیر
- ✅ **داده‌های بازار**: OHLCV + VWAP برای نمودارها
- ✅ **Multi-asset Wallet**: JSONB balances برای چندین ارز

---

## 🔧 توابع مقداردهی اولیه

```python
from models import init_exhibition_db, init_trading_db

# در app factory
def create_app():
    app = Flask(__name__)
    
    # ... config
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        # مقداردهی اولیه ENUMها و تنظیمات
        init_exhibition_db()
        init_trading_db()
    
    return app
```

---

## 📊 آمار مدل‌ها

| بخش | تعداد مدل | تعداد فیلد | ایندکس‌ها | روابط |
|-----|----------|-----------|----------|-------|
| نمایشگاه | ۸ | ~۸۵ | ۱۸ | ۱۲ |
| تالار | ۱۰ | ~۱۲۰ | ۲۵ | ۱۵ |
| **مجموع** | **۱۸** | **~۲۰۵** | **۴۳** | **۲۷** |

---

## 🎯 مزایای تفکیک‌سازی

### ۱. **جداسازی مسئولیت‌ها**
```python
# فقط ایمپورت مدل‌های مورد نیاز
from models.exhibition import Exhibition, Booth
from models.trading import TradeOrder, TradingWallet
```

### ۲. **مستقل‌سازی Migrationها**
```bash
# Migration نمایشگاه
flask db migrate -m "Add exhibition hall"

# Migration تالار  
flask db migrate -m "Add trading hall"
```

### ۳. **توسعه موازی**
- تیم A می‌تواند روی نمایشگاه کار کند
- تیم B می‌تواند روی تالار کار کند
- بدون تداخل در کد

### ۴. **دیباگ آسان‌تر**
- هر بخش فایل جداگانه دارد
- خطوط کمتر در هر فایل
- پیدا کردن سریع‌تر باگ‌ها

### ۵. **مقیاس‌پذیری**
- اگر هر بخش بزرگ شد، می‌توان به زیرماژول‌های بیشتر تقسیم کرد
- مثال: `trading/orders.py`, `trading/wallets.py`

---

## 🚀 شروع به کار

### مرحله ۱: ساخت جداول
```bash
flask db upgrade
```

### مرحله ۲: تست لود مدل‌ها
```bash
python -c "from models import Exhibition, TradingPair; print('✅ OK')"
```

### مرحله ۳: ایجاد داده‌های اولیه
```python
with app.app_context():
    init_exhibition_db()
    init_trading_db()
```

---

## 📝 نکات مهم طراحی

### ۱. UUID Primary Keys
- امنیت بهتر (قابل حدس نیستند)
- توزیع‌پذیری بالاتر
- ادغام راحت‌تر بین سیستم‌ها

### ۲. JSONB Fields
- انعطاف برای فیچرهای آینده
- بدون نیاز به ALTER TABLE
- کوئری‌پذیر در PostgreSQL

### ۳. Indexing Strategy
- ایندکس روی foreign keyها
- ایندکس ترکیبی برای کوئری‌های رایج
- ایندکس یکتا برای slugها و نمادها

### ۴. Multi-language Support
- فیلدهای `_fa` و `_en` برای عناوین
- آماده برای چندزبانه واقعی

### ۵. Audit Trail
- `created_at`, `updated_at` در تمام مدل‌ها
- قابلیت ردیابی تغییرات

---

## 🔮 مسیر توسعه آینده

### فاز ۱: MVP (هفته ۱-۲)
- [ ] CRUD نمایشگاه و غرفه
- [ ] سفارش‌گذاری ساده (Market/Limit)
- [ ] کیف پول پایه

### فاز ۲: حرفه‌ای (هفته ۳-۴)
- [ ] Matching Engine
- [ ] نمودارهای قیمتی
- [ ] تور مجازی نمایشگاه

### فاز ۳: پیشرفته (هفته ۵+)
- [ ] غرفه‌های ۳D
- [ ] سفارش‌های شرطی پیچیده
- [ ] API Real-time (WebSocket)

---

## 📞 پشتیبانی

برای هر سوال یا نیاز به تغییر در مدل‌ها:
1. بررسی فایل‌های `models/exhibition/__init__.py` و `models/trading/__init__.py`
2. مطالعه داکیومنت `EXHIBITION_TRADING_DEVELOPMENT_GUIDE.md`
3. تست با `flask shell`

---

**نسخه:** 1.0.0  
**تاریخ:** 2024  
**وضعیت:** ✅ آماده برای Migration
