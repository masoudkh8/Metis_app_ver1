# models/ai_chat.py
# بخش ۱: هسته هوش مصنوعی و مشاوره هوشمند (AI Core)

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

class Conversation(db.Model):
    """
    مکالمات کاربر با ربات مشاور صادراتی
    """
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    # موضوع مکالمه
    topic = db.Column(db.String(200))
    category = db.Column(db.String(100))
    
    # زبان مکالمه
    language = db.Column(db.String(10), default='fa')
    
    # وضعیت
    status = db.Column(db.String(50), default='active')
    is_resolved = db.Column(db.Boolean, default=False)
    
    # امتیاز کاربر
    user_rating = db.Column(db.Integer)
    user_feedback = db.Column(db.Text)
    
    # زمان‌بندی
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    
    # روابط
    messages = db.relationship('ChatMessage', backref='conversation', lazy='dynamic', cascade='all, delete-orphan')
    user = db.relationship('User', backref='conversations')
    
    def __repr__(self):
        return f'<Conversation {self.id} - User {self.user_id}>'


class ChatMessage(db.Model):
    """
    پیام‌های مکالمه با ربات
    """
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False, index=True)
    
    role = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    content_fa = db.Column(db.Text)
    content_en = db.Column(db.Text)
    content_ar = db.Column(db.Text)
    
    message_type = db.Column(db.String(50), default='text')
    
    # داده‌های ساختاریافته
    msg_data = db.Column(JSONB, default=dict)
    sources = db.Column(db.JSON)
    
    tokens_used = db.Column(db.Integer, default=0)
    model_used = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ChatMessage {self.id} - {self.role}>'


class AIRecommendation(db.Model):
    """
    پیشنهادات هوشمند AI
    """
    __tablename__ = 'ai_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    recommendation_type = db.Column(db.String(100), nullable=False)
    
    title = db.Column(db.String(300), nullable=False)
    title_fa = db.Column(db.String(300))
    title_en = db.Column(db.String(300))
    title_ar = db.Column(db.String(300))
    
    description = db.Column(db.Text)
    description_fa = db.Column(db.Text)
    description_en = db.Column(db.Text)
    description_ar = db.Column(db.Text)
    
    data = db.Column(JSONB, default=dict)
    
    priority = db.Column(db.Integer, default=50)
    confidence_score = db.Column(db.Float)
    
    status = db.Column(db.String(50), default='pending')
    is_personalized = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    viewed_at = db.Column(db.DateTime)
    acted_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    
    user = db.relationship('User', backref='ai_recommendations')
    
    def __repr__(self):
        return f'<AIRecommendation {self.id} - {self.recommendation_type}>'


class CustomizationProfile(db.Model):
    """
    پروفایل شخصی‌سازی کاربر
    """
    __tablename__ = 'customization_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True, index=True)
    
    industry = db.Column(db.String(100))
    industry_fa = db.Column(db.String(100))
    industry_en = db.Column(db.String(100))
    industry_ar = db.Column(db.String(100))
    
    products = db.Column(db.JSON)
    target_countries = db.Column(db.JSON)
    
    dashboard_preferences = db.Column(JSONB, default=dict)
    notification_settings = db.Column(JSONB, default=dict)
    
    risk_tolerance = db.Column(db.String(20), default='medium')
    default_language = db.Column(db.String(10), default='fa')
    default_currency = db.Column(db.String(10), default='IRR')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='customization_profile')
    
    def __repr__(self):
        return f'<CustomizationProfile {self.id} - User {self.user_id}>'


class ContentGenerationRequest(db.Model):
    """
    درخواست تولید محتوا توسط AI
    """
    __tablename__ = 'content_generation_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    content_type = db.Column(db.String(100), nullable=False)
    input_data = db.Column(JSONB, nullable=False)
    parameters = db.Column(JSONB, default=dict)
    
    generated_content = db.Column(db.Text)
    generated_content_fa = db.Column(db.Text)
    generated_content_en = db.Column(db.Text)
    generated_content_ar = db.Column(db.Text)
    
    status = db.Column(db.String(50), default='pending')
    error_message = db.Column(db.Text)
    
    tokens_used = db.Column(db.Integer, default=0)
    model_used = db.Column(db.String(100))
    
    user_approved = db.Column(db.Boolean)
    user_edits = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    user = db.relationship('User', backref='content_generation_requests')
    
    def __repr__(self):
        return f'<ContentGenerationRequest {self.id} - {self.content_type}>'
