# models/product.py
# بخش ۹: Marketplace Core - مدیریت محصولات و مارکت‌پلیس

from . import db
from datetime import datetime
from enum import Enum

class ProductStatus(Enum):
    DRAFT = 'draft'
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SOLD_OUT = 'sold_out'
    SUSPENDED = 'suspended'

class ProductCategory(Enum):
    AGRICULTURE = 'agriculture'  # کشاورزی
    FOOD = 'food'  # مواد غذایی
    PETROCHEMICAL = 'petrochemical'  # پتروشیمی
    MINERAL = 'mineral'  # معدنی
    TEXTILE = 'textile'  # نساجی
    HANDICRAFT = 'handicraft'  # صنایع دستی
    INDUSTRIAL = 'industrial'  # صنعتی
    TECHNOLOGY = 'technology'  # فناوری
    OTHER = 'other'  # سایر

class Product(db.Model):
    """
    محصول برای مارکت‌پلیس (بخش ۹)
    """
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    # اطلاعات پایه
    name_fa = db.Column(db.String(200), nullable=False)  # نام فارسی
    name_en = db.Column(db.String(200))  # نام انگلیسی
    name_ar = db.Column(db.String(200))  # نام عربی
    
    description_fa = db.Column(db.Text)  # توضیحات فارسی
    description_en = db.Column(db.Text)  # توضیحات انگلیسی
    description_ar = db.Column(db.Text)  # توضیحات عربی
    
    category = db.Column(db.Enum(ProductCategory), default=ProductCategory.OTHER)
    hs_code = db.Column(db.String(20))  # کد تعرفه گمرکی
    
    # قیمت‌گذاری
    price = db.Column(db.Numeric(15, 2))  # قیمت
    currency = db.Column(db.String(3), default='USD')  # ارز
    price_type = db.Column(db.String(50))  # مثلاً: per ton, per piece
    
    # موجودی و سفارش
    min_order_quantity = db.Column(db.Numeric(15, 2), default=1)  # حداقل سفارش
    max_order_quantity = db.Column(db.Numeric(15, 2))  # حداکثر سفارش
    available_quantity = db.Column(db.Numeric(15, 2))  # موجودی
    unit = db.Column(db.String(20), default='unit')  # واحد اندازه‌گیری
    
    # مشخصات فنی
    specifications = db.Column(db.JSON)  # مشخصات فنی به صورت JSON
    certifications = db.Column(db.JSON)  # گواهی‌نامه‌ها
    
    # رسانه
    images = db.Column(db.JSON)  # لیست تصاویر
    videos = db.Column(db.JSON)  # لیست ویدیوها
    catalog_file = db.Column(db.String(500))  # فایل کاتالوگ
    
    # وضعیت و زمان‌بندی
    status = db.Column(db.Enum(ProductStatus), default=ProductStatus.DRAFT)
    is_featured = db.Column(db.Boolean, default=False)  # محصول ویژه
    is_export_ready = db.Column(db.Boolean, default=False)  # آماده صادرات
    
    # بازارها
    target_markets = db.Column(db.JSON)  # لیست کشورهای هدف
    domestic_available = db.Column(db.Boolean, default=True)  # موجود در بازار داخلی
    international_available = db.Column(db.Boolean, default=False)  # موجود در بازار بین‌الملل
    
    # لجستیک
    packaging_details = db.Column(db.Text)  # جزئیات بسته‌بندی
    delivery_time_days = db.Column(db.Integer)  # زمان تحویل (روز)
    port_of_loading = db.Column(db.String(100))  # بندر بارگیری
    
    # آمار
    view_count = db.Column(db.Integer, default=0)
    inquiry_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    company = db.relationship('User', backref=db.backref('products', lazy='dynamic'))
    
    # ایندکس‌ها برای جستجو
    __table_args__ = (
        db.Index('idx_product_category', 'category'),
        db.Index('idx_product_status', 'status'),
        db.Index('idx_product_company', 'company_id'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name_fa': self.name_fa,
            'name_en': self.name_en,
            'category': self.category.value if self.category else None,
            'price': float(self.price) if self.price else None,
            'currency': self.currency,
            'status': self.status.value if self.status else None,
            'is_export_ready': self.is_export_ready,
            'target_markets': self.target_markets,
            'images': self.images[:3] if self.images else [],  # ۳ تصویر اول
            'company_name': self.company.company_name if self.company else None,
            'trust_score': self.company.trust_score.score if self.company and self.company.trust_score else None,
        }


class RFQ(db.Model):
    """
    درخواست خرید (Request for Quotation) - بخش ۹
    """
    __tablename__ = 'rfqs'
    
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    title_fa = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200))
    
    description = db.Column(db.Text, nullable=False)
    product_category = db.Column(db.Enum(ProductCategory))
    
    # جزئیات سفارش
    quantity = db.Column(db.Numeric(15, 2), nullable=False)
    unit = db.Column(db.String(20))
    target_price = db.Column(db.Numeric(15, 2))
    currency = db.Column(db.String(3), default='USD')
    
    # زمان‌بندی
    delivery_deadline = db.Column(db.Date)
    delivery_location = db.Column(db.String(200))  # محل تحویل
    
    # وضعیت
    status = db.Column(db.String(20), default='open')  # open, closed, in_negotiation, completed
    is_anonymous = db.Column(db.Boolean, default=False)  # عدم نمایش خریدار
    
    # مهلت پاسخ
    deadline = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    buyer = db.relationship('User', backref=db.backref('rfqs', lazy='dynamic'))
    proposals = db.relationship('RFQProposal', backref='rfq', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title_fa,
            'description': self.description,
            'quantity': float(self.quantity) if self.quantity else None,
            'target_price': float(self.target_price) if self.target_price else None,
            'status': self.status,
            'proposals_count': self.proposals.count(),
            'deadline': self.deadline.isoformat() if self.deadline else None,
        }


class RFQProposal(db.Model):
    """
    پیشنهاد قیمت برای RFQ - بخش ۹
    """
    __tablename__ = 'rfq_proposals'
    
    id = db.Column(db.Integer, primary_key=True)
    rfq_id = db.Column(db.Integer, db.ForeignKey('rfqs.id'), nullable=False, index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    # پیشنهاد
    offered_price = db.Column(db.Numeric(15, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    quantity_offered = db.Column(db.Numeric(15, 2))
    
    # شرایط
    delivery_time_days = db.Column(db.Integer)
    payment_terms = db.Column(db.Text)  # شرایط پرداخت
    additional_notes = db.Column(db.Text)
    
    # ضمیمه‌ها
    product_catalog = db.Column(db.String(500))
    certificates = db.Column(db.JSON)
    
    # وضعیت
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected, withdrawn
    is_winner = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    supplier = db.relationship('User', backref=db.backref('rfq_proposals', lazy='dynamic'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'offered_price': float(self.offered_price) if self.offered_price else None,
            'currency': self.currency,
            'delivery_time_days': self.delivery_time_days,
            'status': self.status,
            'supplier_name': self.supplier.company_name if self.supplier else None,
            'supplier_trust_score': self.supplier.trust_score.score if self.supplier and self.supplier.trust_score else None,
        }


class ProductComparison(db.Model):
    """
    مقایسه محصولات - بخش ۹
    """
    __tablename__ = 'product_comparisons'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    products = db.Column(db.JSON, nullable=False)  # لیست ID محصولات برای مقایسه
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('comparisons', lazy='dynamic'))


class FavoriteProduct(db.Model):
    """
    محصولات مورد علاقه - بخش ۹
    """
    __tablename__ = 'favorite_products'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='unique_favorite'),)
    
    user = db.relationship('User', backref=db.backref('favorites', lazy='dynamic'))
    product = db.relationship('Product', backref=db.backref('favorited_by', lazy='dynamic'))
