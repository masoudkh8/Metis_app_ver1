# models/i18n.py
# بخش ۱۳: چندزبانه و بومی‌سازی (i18n & Localization)

from . import db
from datetime import datetime
import json

class JSONB(db.TypeDecorator):
    """Platform-independent JSON type that uses JSONB for PostgreSQL and JSON for others."""
    impl = db.JSON
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if dialect.name == 'postgresql':
            return json.dumps(value) if value else None
        return value
    
    def process_result_value(self, value, dialect):
        if isinstance(value, str):
            return json.loads(value) if value else None
        return value

class Language(db.Model):
    """اطلاعات زبان‌های پشتیبانی‌شده"""
    __tablename__ = 'languages'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), nullable=False, unique=True)
    
    name_fa = db.Column(db.String(100))
    name_en = db.Column(db.String(100))
    name_ar = db.Column(db.String(100))
    
    direction = db.Column(db.String(4), nullable=False, default='rtl')
    
    date_format = db.Column(db.String(50), default='YYYY/MM/DD')
    time_format = db.Column(db.String(50), default='HH:mm')
    calendar_type = db.Column(db.String(50), default='gregorian')
    
    is_active = db.Column(db.Boolean, default=True)
    is_default = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Language {self.code}>'


class TranslationKey(db.Model):
    """کلیدهای ترجمه برای تمام متون پلتفرم"""
    __tablename__ = 'translation_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(200), nullable=False, unique=True, index=True)
    category = db.Column(db.String(100), index=True)
    
    description = db.Column(db.Text)
    content_type = db.Column(db.String(50), default='text')
    
    is_active = db.Column(db.Boolean, default=True)
    requires_review = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    translations = db.relationship('Translation', backref='translation_key', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<TranslationKey {self.key}>'


class Translation(db.Model):
    """مقادیر ترجمه‌شده"""
    __tablename__ = 'translations'
    
    id = db.Column(db.Integer, primary_key=True)
    key_id = db.Column(db.Integer, db.ForeignKey('translation_keys.id'), nullable=False, index=True)
    language_code = db.Column(db.String(10), nullable=False)
    
    value = db.Column(db.Text, nullable=False)
    is_auto_translated = db.Column(db.Boolean, default=False)
    quality_score = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('key_id', 'language_code', name='unique_key_language'),
    )
    
    def __repr__(self):
        return f'<Translation {self.key_id} - {self.language_code}>'


class LocalizationSettings(db.Model):
    """تنظیمات بومی‌سازی برای هر کاربر"""
    __tablename__ = 'localization_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True, index=True)
    
    preferred_language = db.Column(db.String(10), default='fa')
    preferred_calendar = db.Column(db.String(50), default='jalali')
    preferred_currency = db.Column(db.String(10), default='IRR')
    
    measurement_system = db.Column(db.String(20), default='metric')
    timezone = db.Column(db.String(50), default='Asia/Tehran')
    use_persian_digits = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='localization_settings')
    
    def __repr__(self):
        return f'<LocalizationSettings User {self.user_id}>'
