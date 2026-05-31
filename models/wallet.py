# models/wallet.py
# بخش ۱۰: Financial Layer - مدیریت پرداخت‌ها و کیف پول

from . import db
from datetime import datetime
from enum import Enum
import uuid

class Currency(Enum):
    IRR = 'IRR'  # ریال ایران
    USD = 'USD'  # دلار آمریکا
    EUR = 'EUR'  # یورو
    AED = 'AED'  # درهم امارات
    TRY = 'TRY'  # لیر ترکیه
    CNY = 'CNY'  # یوان چین

class WalletTransactionType(Enum):
    DEPOSIT = 'deposit'  # واریز
    WITHDRAWAL = 'withdrawal'  # برداشت
    PAYMENT = 'payment'  # پرداخت
    REFUND = 'refund'  # بازگشت وجه
    TRANSFER = 'transfer'  # انتقال
    ESCROW_HOLD = 'escrow_hold'  # بلوکه در حساب امانی
    ESCROW_RELEASE = 'escrow_release'  # آزادسازی از امانی
    FEE = 'fee'  # کارمزد
    CREDIT_CONVERSION = 'credit_conversion'  # تبدیل اعتبار به پول

class TransactionStatus(Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    REVERSED = 'reversed'

class PaymentMethod(Enum):
    BANK_TRANSFER = 'bank_transfer'  # انتقال بانکی
    ONLINE_GATEWAY = 'online_gateway'  # درگاه آنلاین
    CRYPTO = 'crypto'  # ارز دیجیتال
    CASH = 'cash'  # نقدی
    CREDIT = 'credit'  # اعتباری

class Wallet(db.Model):
    """
    کیف پول کاربر - بخش ۱۰
    """
    __tablename__ = 'wallets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True, index=True)
    
    # موجودی‌ها به تفکیک ارز
    balance_irr = db.Column(db.Numeric(20, 0), default=0)  # ریال
    balance_usd = db.Column(db.Numeric(15, 2), default=0)  # دلار
    balance_eur = db.Column(db.Numeric(15, 2), default=0)  # یورو
    balance_aed = db.Column(db.Numeric(15, 2), default=0)  # درهم
    
    # وضعیت
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)  # تأیید شده برای معاملات ارزی
    
    # محدودیت‌ها
    daily_withdrawal_limit = db.Column(db.Numeric(15, 2), default=10000)  # سقف برداشت روزانه (دلار)
    monthly_withdrawal_limit = db.Column(db.Numeric(15, 2), default=100000)  # سقف برداشت ماهانه
    
    # آمار
    total_deposited = db.Column(db.Numeric(20, 0), default=0)  # کل واریزی (ریال)
    total_withdrawn = db.Column(db.Numeric(20, 0), default=0)  # کل برداشتی (ریال)
    total_traded = db.Column(db.Numeric(20, 0), default=0)  # کل معاملات
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    user = db.relationship('User', backref=db.backref('wallet', uselist=False))
    transactions = db.relationship('WalletTransaction', backref='wallet', lazy='dynamic', cascade='all, delete-orphan')
    escrows = db.relationship('EscrowTransaction', backref='wallet', lazy='dynamic')
    
    def get_balance(self, currency='USD'):
        """دریافت موجودی بر اساس ارز"""
        if currency == 'IRR':
            return self.balance_irr or 0
        elif currency == 'USD':
            return self.balance_usd or 0
        elif currency == 'EUR':
            return self.balance_eur or 0
        elif currency == 'AED':
            return self.balance_aed or 0
        return 0
    
    def to_dict(self):
        return {
            'id': self.id,
            'balances': {
                'IRR': float(self.balance_irr) if self.balance_irr else 0,
                'USD': float(self.balance_usd) if self.balance_usd else 0,
                'EUR': float(self.balance_eur) if self.balance_eur else 0,
                'AED': float(self.balance_aed) if self.balance_aed else 0,
            },
            'is_verified': self.is_verified,
            'total_traded': float(self.total_traded) if self.total_traded else 0,
        }


class WalletTransaction(db.Model):
    """
    تراکنش‌های کیف پول - بخش ۱۰
    """
    __tablename__ = 'wallet_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False, index=True)
    
    # شناسه یکتا
    transaction_id = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True)
    
    # نوع تراکنش
    type = db.Column(db.Enum(WalletTransactionType), nullable=False)
    payment_method = db.Column(db.Enum(PaymentMethod))
    
    # مبلغ و ارز
    amount = db.Column(db.Numeric(20, 0), nullable=False)  # مبلغ اصلی
    currency = db.Column(db.Enum(Currency), nullable=False)
    
    # مبلغ معادل ریالی (برای گزارش‌گیری)
    amount_irr_equivalent = db.Column(db.Numeric(20, 0))
    exchange_rate = db.Column(db.Numeric(15, 2))  # نرخ ارز لحظه‌ای
    
    # وضعیت
    status = db.Column(db.Enum(TransactionStatus), default=TransactionStatus.PENDING)
    
    # توضیحات
    description_fa = db.Column(db.Text)
    description_en = db.Column(db.Text)
    reference_number = db.Column(db.String(100))  # شماره پیگیری
    
    # اطلاعات پرداخت
    gateway_response = db.Column(db.JSON)  # پاسخ درگاه پرداخت
    bank_details = db.Column(db.JSON)  # اطلاعات بانکی
    
    # کارمزد
    fee_amount = db.Column(db.Numeric(15, 2), default=0)
    fee_currency = db.Column(db.String(3), default='IRR')
    
    # زمان‌بندی
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # متادیتا اضافی
    extra_data = db.Column(db.JSON)  # داده‌های اضافی
    
    # روابط - Foreign Key columns
    related_order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True, index=True)
    related_escrow_id = db.Column(db.Integer, db.ForeignKey('escrow_transactions.id'), nullable=True, index=True)
    
    related_order = db.relationship('Order', backref='wallet_transaction', uselist=False)
    related_escrow = db.relationship('EscrowTransaction', backref='wallet_transaction', uselist=False)
    
    __table_args__ = (
        db.Index('idx_transaction_type', 'type'),
        db.Index('idx_transaction_status', 'status'),
        db.Index('idx_transaction_date', 'requested_at'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'type': self.type.value,
            'amount': float(self.amount) if self.amount else None,
            'currency': self.currency.value,
            'status': self.status.value,
            'requested_at': self.requested_at.isoformat() if self.requested_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'reference_number': self.reference_number,
        }


class EscrowTransaction(db.Model):
    """
    حساب امانی (Escrow) برای ضمانت معامله - بخش ۱۰
    """
    __tablename__ = 'escrow_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # طرفین معامله
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False, index=True)
    
    # مرتبط با سفارش
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, unique=True, index=True)
    
    # مبلغ
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    currency = db.Column(db.Enum(Currency), nullable=False)
    
    # وضعیت امانی
    escrow_status = db.Column(db.String(20), default='held')  # held, released, refunded, disputed
    
    # شرایط آزادسازی
    release_conditions = db.Column(db.JSON)  # شرایط لازم برای آزادسازی
    auto_release_date = db.Column(db.Date)  # تاریخ آزادسازی خودکار
    
    # مستندات
    shipping_documents = db.Column(db.JSON)  # اسناد حمل
    customs_documents = db.Column(db.JSON)  # اسناد گمرکی
    inspection_report = db.Column(db.Text)  # گزارش بازرسی
    
    # اختلافات
    has_dispute = db.Column(db.Boolean, default=False)
    dispute_reason = db.Column(db.Text)
    dispute_resolution = db.Column(db.Text)
    
    # زمان‌بندی
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    released_at = db.Column(db.DateTime)
    
    # روابط
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref=db.backref('escrows_as_buyer', lazy='dynamic'))
    seller = db.relationship('User', foreign_keys=[seller_id], backref=db.backref('escrows_as_seller', lazy='dynamic'))
    order = db.relationship('Order', backref=db.backref('escrow', uselist=False))
    
    def to_dict(self):
        return {
            'id': self.id,
            'amount': float(self.amount) if self.amount else None,
            'currency': self.currency.value,
            'escrow_status': self.escrow_status,
            'has_dispute': self.has_dispute,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'released_at': self.released_at.isoformat() if self.released_at else None,
        }


class ExchangeRate(db.Model):
    """
    نرخ ارز لحظه‌ای - بخش ۱۰
    """
    __tablename__ = 'exchange_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    
    currency_from = db.Column(db.String(3), nullable=False)  # ارز مبدا
    currency_to = db.Column(db.String(3), nullable=False)  # ارز مقصد
    
    rate = db.Column(db.Numeric(15, 6), nullable=False)  # نرخ تبدیل
    source = db.Column(db.String(50))  # منبع نرخ (مثلاً: central_bank, market)
    
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('currency_from', 'currency_to', name='unique_currency_pair'),
        db.Index('idx_currency_from', 'currency_from'),
    )
    
    @classmethod
    def get_rate(cls, from_currency, to_currency):
        """دریافت نرخ تبدیل"""
        if from_currency == to_currency:
            return 1.0
        
        rate_record = cls.query.filter_by(
            currency_from=from_currency,
            currency_to=to_currency,
            is_active=True
        ).order_by(cls.updated_at.desc()).first()
        
        return float(rate_record.rate) if rate_record else None


class FinancialReport(db.Model):
    """
    گزارش‌های مالی - بخش ۱۰
    """
    __tablename__ = 'financial_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    report_type = db.Column(db.String(50), nullable=False)  # monthly, yearly, transaction_history
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    
    # خلاصه گزارش
    total_income = db.Column(db.Numeric(20, 0), default=0)
    total_expense = db.Column(db.Numeric(20, 0), default=0)
    net_balance = db.Column(db.Numeric(20, 0), default=0)
    
    # فایل گزارش
    file_path = db.Column(db.String(500))  # مسیر فایل PDF/Excel
    file_format = db.Column(db.String(10), default='pdf')  # pdf, excel
    
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('financial_reports', lazy='dynamic'))
