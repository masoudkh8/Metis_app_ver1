# models/integration.py
# بخش ۱۱: Integration Layer - یکپارچه‌سازی با سرویس‌های خارجی

from . import db
from datetime import datetime, timedelta
from enum import Enum
import json

class IntegrationType(Enum):
    LINKEDIN = 'linkedin'
    WHATSAPP = 'whatsapp'
    TELEGRAM = 'telegram'
    INSTAGRAM = 'instagram'
    LOGISTICS_API = 'logistics_api'
    CUSTOMS_API = 'customs_api'
    EXCHANGE_RATE = 'exchange_rate'
    GEOPOLITICAL_DATA = 'geopolitical_data'
    EMAIL_SERVICE = 'email_service'
    SMS_SERVICE = 'sms_service'
    PAYMENT_GATEWAY = 'payment_gateway'
    ERP_SYSTEM = 'erp_system'
    CRM_SYSTEM = 'crm_system'

class IntegrationStatus(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    PENDING = 'pending'
    ERROR = 'error'
    SUSPENDED = 'suspended'

class WebhookEvent(Enum):
    ORDER_CREATED = 'order.created'
    ORDER_UPDATED = 'order.updated'
    PAYMENT_RECEIVED = 'payment.received'
    LEAD_CREATED = 'lead.created'
    MESSAGE_RECEIVED = 'message.received'
    PRODUCT_ADDED = 'product.added'
    USER_VERIFIED = 'user.verified'
    CONSORIUM_INVITE = 'consortium.invite'
    COURSE_COMPLETED = 'course.completed'

class ExternalIntegration(db.Model):
    """
    یکپارچه‌سازی با سرویس‌های خارجی - بخش ۱۱
    """
    __tablename__ = 'external_integrations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    integration_type = db.Column(db.Enum(IntegrationType), nullable=False)
    
    # اطلاعات اتصال
    access_token = db.Column(db.Text)  # توکن دسترسی (رمزنگاری‌شده)
    refresh_token = db.Column(db.Text)  # توکن تازه‌سازی
    token_expires_at = db.Column(db.DateTime)
    
    api_key = db.Column(db.String(200))  # کلید API
    api_secret = db.Column(db.Text)  # راز API (رمزنگاری‌شده)
    
    webhook_url = db.Column(db.String(500))  # URL وب‌هوک دریافتی
    
    # تنظیمات
    settings = db.Column(db.JSON)  # تنظیمات خاص هر интеграция
    is_enabled = db.Column(db.Boolean, default=True)
    
    # وضعیت
    status = db.Column(db.Enum(IntegrationStatus), default=IntegrationStatus.PENDING)
    last_sync_at = db.Column(db.DateTime)
    last_error = db.Column(db.Text)
    error_count = db.Column(db.Integer, default=0)
    
    # آمار
    total_calls = db.Column(db.Integer, default=0)
    successful_calls = db.Column(db.Integer, default=0)
    failed_calls = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    user = db.relationship('User', backref=db.backref('integrations', lazy='dynamic'))
    logs = db.relationship('IntegrationLog', backref='integration', lazy='dynamic', cascade='all, delete-orphan')
    webhooks = db.relationship('WebhookSubscription', backref='integration', lazy='dynamic', cascade='all, delete-orphan')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'integration_type', name='unique_user_integration'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'integration_type': self.integration_type.value,
            'status': self.status.value,
            'is_enabled': self.is_enabled,
            'last_sync_at': self.last_sync_at.isoformat() if self.last_sync_at else None,
            'total_calls': self.total_calls,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class IntegrationLog(db.Model):
    """
    لاگ عملیات یکپارچه‌سازی - بخش ۱۱
    """
    __tablename__ = 'integration_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    integration_id = db.Column(db.Integer, db.ForeignKey('external_integrations.id'), nullable=False, index=True)
    
    operation_type = db.Column(db.String(50))  # sync, send, receive, update
    endpoint = db.Column(db.String(300))  # endpoint فراخوانی‌شده
    
    request_data = db.Column(db.JSON)  # داده‌های ارسالی
    response_data = db.Column(db.JSON)  # داده‌های دریافتی
    
    status_code = db.Column(db.Integer)
    success = db.Column(db.Boolean, default=False)
    error_message = db.Column(db.Text)
    
    duration_ms = db.Column(db.Integer)  # مدت زمان اجرا (میلی‌ثانیه)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_log_integration_date', 'integration_id', 'created_at'),
    )


class WebhookSubscription(db.Model):
    """
    اشتراک وب‌هوک - بخش ۱۱
    """
    __tablename__ = 'webhook_subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    integration_id = db.Column(db.Integer, db.ForeignKey('external_integrations.id'))
    
    # URL مقصد
    webhook_url = db.Column(db.String(500), nullable=False)
    
    # رویدادهای مشترک‌شده
    events = db.Column(db.JSON, nullable=False)  # لیست WebhookEvent
    
    # امنیت
    secret_key = db.Column(db.String(64), unique=True)  # کلید امضای وب‌هوک
    signature_algorithm = db.Column(db.String(20), default='HMAC-SHA256')
    
    # وضعیت
    is_active = db.Column(db.Boolean, default=True)
    
    # آمار
    total_deliveries = db.Column(db.Integer, default=0)
    successful_deliveries = db.Column(db.Integer, default=0)
    failed_deliveries = db.Column(db.Integer, default=0)
    last_delivery_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('webhook_subscriptions', lazy='dynamic'))
    deliveries = db.relationship('WebhookDelivery', backref='subscription', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'webhook_url': self.webhook_url,
            'events': self.events,
            'is_active': self.is_active,
            'total_deliveries': self.total_deliveries,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class WebhookDelivery(db.Model):
    """
    تحویل وب‌هوک - بخش ۱۱
    """
    __tablename__ = 'webhook_deliveries'
    
    id = db.Column(db.Integer, primary_key=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey('webhook_subscriptions.id'), nullable=False, index=True)
    
    event_type = db.Column(db.String(100), nullable=False)
    payload = db.Column(db.JSON, nullable=False)
    
    # وضعیت تحویل
    status = db.Column(db.String(20), default='pending')  # pending, success, failed, retrying
    attempts = db.Column(db.Integer, default=0)
    max_attempts = db.Column(db.Integer, default=5)
    
    # پاسخ
    response_status = db.Column(db.Integer)
    response_body = db.Column(db.Text)
    
    # زمان‌بندی
    scheduled_at = db.Column(db.DateTime, default=datetime.utcnow)
    delivered_at = db.Column(db.DateTime)
    next_retry_at = db.Column(db.DateTime)
    
    error_message = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'event_type': self.event_type,
            'status': self.status,
            'attempts': self.attempts,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
        }


class LinkedInProfile(db.Model):
    """
    پروفایل لینکدین همگام‌سازی‌شده - بخش ۱۱
    """
    __tablename__ = 'linkedin_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True, index=True)
    
    linkedin_id = db.Column(db.String(50), unique=True)
    linkedin_url = db.Column(db.String(300))
    
    # اطلاعات پروفایل
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    headline = db.Column(db.String(300))
    summary = db.Column(db.Text)
    industry = db.Column(db.String(100))
    
    # شرکت
    company_name = db.Column(db.String(200))
    company_linkedin_url = db.Column(db.String(300))
    position = db.Column(db.String(100))
    
    # شبکه
    connections_count = db.Column(db.Integer)
    followers_count = db.Column(db.Integer)
    
    # مهارت‌ها
    skills = db.Column(db.JSON)
    
    # آخرین همگام‌سازی
    last_synced_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('linkedin_profile', uselist=False))
    posts = db.relationship('LinkedInPost', backref='profile', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'linkedin_url': self.linkedin_url,
            'headline': self.headline,
            'company_name': self.company_name,
            'position': self.position,
            'connections_count': self.connections_count,
            'last_synced_at': self.last_synced_at.isoformat() if self.last_synced_at else None,
        }


class LinkedInPost(db.Model):
    """
    پست‌های لینکدین - بخش ۱۱
    """
    __tablename__ = 'linkedin_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('linkedin_profiles.id'), nullable=False, index=True)
    
    post_id = db.Column(db.String(50))  # ID پست در لینکدین
    post_url = db.Column(db.String(500))
    
    content = db.Column(db.Text)
    media_urls = db.Column(db.JSON)  # تصاویر/ویدیوها
    
    # آمار
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    shares_count = db.Column(db.Integer, default=0)
    impressions = db.Column(db.Integer, default=0)
    
    published_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'post_url': self.post_url,
            'content': self.content[:200] + '...' if len(self.content) > 200 else self.content,
            'likes_count': self.likes_count,
            'comments_count': self.comments_count,
            'published_at': self.published_at.isoformat() if self.published_at else None,
        }


class WhatsAppContact(db.Model):
    """
    مخاطبان واتس‌اپ - بخش ۱۱
    """
    __tablename__ = 'whatsapp_contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    phone_number = db.Column(db.String(20), nullable=False)
    display_name = db.Column(db.String(100))
    
    whatsapp_business_id = db.Column(db.String(50))
    
    # وضعیت
    is_verified = db.Column(db.Boolean, default=False)
    last_message_at = db.Column(db.DateTime)
    
    # تگ‌ها
    tags = db.Column(db.JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'phone_number', name='unique_whatsapp_contact'),)
    
    user = db.relationship('User', backref=db.backref('whatsapp_contacts', lazy='dynamic'))


class LogisticsProvider(db.Model):
    """
    ارائه‌دهندگان خدمات لجستیک - بخش ۱۱
    """
    __tablename__ = 'logistics_providers'
    
    id = db.Column(db.Integer, primary_key=True)
    
    name_fa = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200))
    
    provider_type = db.Column(db.String(50))  # shipping, freight_forwarder, customs_broker, warehouse
    
    api_endpoint = db.Column(db.String(500))
    api_key = db.Column(db.String(200))
    
    supported_countries = db.Column(db.JSON)  # کشورهای تحت پوشش
    supported_services = db.Column(db.JSON)  # خدمات قابل ارائه
    
    # تنظیمات
    settings = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    quotes = db.relationship('LogisticsQuote', backref='provider', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name_fa': self.name_fa,
            'provider_type': self.provider_type,
            'supported_countries': self.supported_countries,
            'is_active': self.is_active,
        }


class LogisticsQuote(db.Model):
    """
    استعلام قیمت لجستیک - بخش ۱۱
    """
    __tablename__ = 'logistics_quotes'
    
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('logistics_providers.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    # مسیر
    origin_country = db.Column(db.String(50), nullable=False)
    origin_city = db.Column(db.String(100))
    destination_country = db.Column(db.String(50), nullable=False)
    destination_city = db.Column(db.String(100))
    
    # محموله
    weight_kg = db.Column(db.Numeric(10, 2))
    volume_m3 = db.Column(db.Numeric(10, 2))
    cargo_type = db.Column(db.String(50))  # container, bulk, pallet, etc.
    
    # خدمات
    service_type = db.Column(db.String(50))  # sea, air, land, rail
    incoterms = db.Column(db.String(10))  # FOB, CIF, EXW, etc.
    
    # قیمت
    base_price = db.Column(db.Numeric(12, 2))
    additional_fees = db.Column(db.JSON)  # هزینه‌های اضافی
    total_price = db.Column(db.Numeric(12, 2))
    currency = db.Column(db.String(3), default='USD')
    
    # زمان
    estimated_days = db.Column(db.Integer)  # روزهای تخمینی
    valid_until = db.Column(db.DateTime)
    
    # وضعیت
    status = db.Column(db.String(20), default='quoted')  # quoted, booked, cancelled
    booking_reference = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('logistics_quotes', lazy='dynamic'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'provider_name': self.provider.name_fa if self.provider else None,
            'route': f"{self.origin_country} → {self.destination_country}",
            'total_price': float(self.total_price) if self.total_price else None,
            'currency': self.currency,
            'estimated_days': self.estimated_days,
            'status': self.status,
        }


class APICache(db.Model):
    """
    کش داده‌های API خارجی - بخش ۱۱
    """
    __tablename__ = 'api_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    
    cache_key = db.Column(db.String(200), unique=True, nullable=False)
    source = db.Column(db.String(50))  # منبع داده
    
    data = db.Column(db.JSON, nullable=False)
    
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.Index('idx_cache_expires', 'expires_at'),)
    
    @classmethod
    def get_valid(cls, key):
        """دریافت داده معتبر از کش"""
        record = cls.query.filter_by(cache_key=key).first()
        if record and record.expires_at > datetime.utcnow():
            return record.data
        return None
