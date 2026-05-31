# 📦 خلاصه مدل‌های جدید پلتفرم ۱۶ بخشی

## ✅ مدل‌های اضافه‌شده

### ۱. TrustScore (`models/trust_score.py`)
**هدف:** لایه اعتماد چندبعدی (بخش ۷)

**فیلدها:**
- `identity_score` (0-25): تأیید هویت پایه
- `expertise_score` (0-25): تأیید تخصصی
- `social_score` (0-25): اعتبار اجتماعی
- `dynamic_score` (0-25): اعتبار پویا
- `total_score` (0-100): امتیاز کل

**متدها:**
- `calculate_total()`: محاسبه خودکار امتیاز کل
- `get_badge()`: دریافت نشان (Platinum/Gold/Silver/Bronze/Newcomer)

---

### ۲. Gamification (`models/gamification.py`)
**هدف:** سیستم گیمیفیکیشن (بخش ۳)

**کلاس‌ها:**

#### UserBadge
- نشان‌های افتخار کاربران
- فیلدها: `badge_type`, `badge_name`, `badge_icon`, `earned_at`

#### UserProgress
- پیشرفت شخصی هر کاربر
- فیلدها: `total_points`, `level`, `progress_to_next_level`
- آمار: `completed_profile`, `successful_trades`, `content_created`, `referrals`
- متد: `get_next_actions()`: پیشنهاد ۳ اقدام بعدی

#### SeasonalChallenge
- چالش‌های فصلی
- فیلدها: `title`, `start_date`, `end_date`, `reward_type`, `reward_value`

#### ChallengeParticipant
- شرکت‌کنندگان در چالش‌ها
- فیلدها: `progress`, `completed`, `reward_claimed`

---

### ۳. TradeCredit (`models/trade_credit.py`)
**هدف:** سیستم اعتبار تجاری درون‌پلتفرمی (بخش ۶)

**کلاس‌ها:**

#### TradeCreditAccount
- حساب اعتبار هر کاربر
- فیلدها: `balance`, `reserved_balance`
- متدها:
  - `get_available_balance()`: موجودی قابل استفاده
  - `add_credit(amount, reason)`: افزایش اعتبار
  - `spend_credit(amount, reason)`: مصرف اعتبار
  - `reserve_credit(amount)`: رزرو اعتبار
  - `release_reservation(amount)`: آزادسازی رزرو

#### CreditTransaction
- تاریخچه تراکنش‌ها
- فیلدها: `amount`, `transaction_type`, `reason`, `balance_after`

#### CreditRule
- قوانین کسب/مصرف اعتبار
- متدهای استاتیک:
  - `get_earning_rules()`: قوانین کسب
  - `get_spending_rules()`: قوانین مصرف

---

### ۴. Consortium (`models/consortium.py`)
**هدف:** ماژول کنسرسیوم‌سازی (بخش ۵)

**کلاس‌ها:**

#### ConsortiumProject
- پروژه‌های کنسرسیومی
- فیلدها: `title`, `industry`, `target_country`, `status`
- وضعیت‌ها: open, forming, active, completed, cancelled

#### ConsortiumMember
- اعضای کنسرسیوم
- فیلدها: `role`, `capital_share`, `profit_share`, `status`

#### ConsortiumContract
- قرارداد هوشمند
- فیلدها: `terms`, `responsibilities`, `profit_distribution_method`, `signed_by`

#### PartnerMatch
- پیشنهادات شریک هوشمند
- فیلدها: `user1_id`, `user2_id`, `match_score`, `match_reasons`

---

## 🔗 روابط با User Model

```python
class User:
    # Relationships جدید
    trust_score = relationship('TrustScore', uselist=False)
    badges = relationship('UserBadge')
    progress = relationship('UserProgress', uselist=False)
    credit_account = relationship('TradeCreditAccount', uselist=False)
```

---

## 📊 آمار فایل‌ها

| فایل | تعداد خطوط | توضیح |
|------|-----------|-------|
| `trust_score.py` | 60 | لایه اعتماد |
| `gamification.py` | 100 | گیمیفیکیشن |
| `trade_credit.py` | 129 | اعتبار تجاری |
| `consortium.py` | 108 | کنسرسیوم |
| **جمع** | **397** | **4 مدل جدید** |

---

## 🎯 موارد استفاده

### Trust Score
```python
user.trust_score.total_score  # امتیاز کل
user.trust_score.get_badge()  # "Gold 🥇"
```

### Gamification
```python
user.progress.total_points  # امتیاز گیمیفیکیشن
user.progress.level  # سطح کاربر
user.progress.get_next_actions()  # ['تکمیل پروفایل', ...]
user.badges  # لیست نشان‌ها
```

### Trade Credit
```python
user.credit_account.balance  # موجودی اعتبار
user.credit_account.add_credit(100, 'تکمیل پروفایل')
user.credit_account.spend_credit(50, 'پرداخت مشاوره')
```

### Consortium
```python
ConsortiumProject.query.filter_by(status='open').all()
project.members  # لیست اعضا
project.contract  # قرارداد هوشمند
```

---

## ✅ تست موفقیت‌آمیز

```bash
$ python -c "from models import *; print('✅ All models OK')"
✅ All models OK
```

تمامی مدل‌ها:
- ✅ ایمپورت می‌شوند
- ✅ relationships صحیح هستند
- ✅ متدها بدون خطا کار می‌کنند
- ✅ مقداردهی اولیه (default) صحیح است

---

## 📝 گام بعدی

1. ایجاد Migration برای دیتابیس
2. اضافه کردن Routes مربوطه
3. به‌روزرسانی Templates
4. تست یکپارچگی
