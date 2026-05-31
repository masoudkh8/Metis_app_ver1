# models/trust_score.py
"""
بخش ۷: لایه اعتماد چندبعدی (Trust Stack)
- امتیاز اعتبار پویا برای هر کاربر
- لایه‌های تأیید هویت، تخصص، اعتبار اجتماعی
"""
from . import db
from datetime import datetime
import pytz

tehran_tz = pytz.timezone('Asia/Tehran')


class TrustScore(db.Model):
    __tablename__ = 'trust_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    
    # لایه ۱: تأیید هویت پایه (۰-۲۵ امتیاز)
    identity_verified = db.Column(db.Boolean, default=False)  # مدارک ثبت شرکت
    identity_score = db.Column(db.Integer, default=0)  # 0-25
    
    # لایه ۲: تأیید تخصصی (۰-۲۵ امتیاز)
    expertise_verified = db.Column(db.Boolean, default=False)  # گواهی محصول، سابقه صادرات
    expertise_score = db.Column(db.Integer, default=0)  # 0-25
    
    # لایه ۳: اعتبار اجتماعی (۰-۲۵ امتیاز)
    social_score = db.Column(db.Integer, default=0)  # 0-25 (نظرات، معاملات موفق)
    
    # لایه ۴: اعتبار پویا (۰-۲۵ امتیاز)
    dynamic_score = db.Column(db.Integer, default=0)  # 0-25 (سرعت پاسخگویی، دقت تحویل)
    
    # امتیاز کل (۰-۱۰۰)
    total_score = db.Column(db.Integer, default=0)
    
    # تاریخچه تغییرات
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(tehran_tz), onupdate=lambda: datetime.now(tehran_tz))
    
    # رابطه
    user = db.relationship('User', back_populates='trust_score')
    
    def calculate_total(self):
        """محاسبه خودکار امتیاز کل"""
        self.total_score = self.identity_score + self.expertise_score + self.social_score + self.dynamic_score
        return self.total_score
    
    def get_badge(self):
        """دریافت نشان اعتبار بر اساس امتیاز"""
        score = self.total_score or 0
        if score >= 90:
            return "Platinum 🏆"
        elif score >= 75:
            return "Gold 🥇"
        elif score >= 50:
            return "Silver 🥈"
        elif score >= 25:
            return "Bronze 🥉"
        else:
            return "Newcomer 🆕"
