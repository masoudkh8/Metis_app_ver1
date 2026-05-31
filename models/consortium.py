# models/consortium.py
"""
بخش ۵: ماژول کنسرسیوم‌سازی هوشمند (Consortium Engine)
- موتور کشف فرصت‌های کنسرسیومی
- سیستم پیشنهاد شریک هوشمند
- پنل مدیریت کنسرسیوم
- قرارداد هوشمند
"""
from . import db
from datetime import datetime
import pytz

tehran_tz = pytz.timezone('Asia/Tehran')


class ConsortiumProject(db.Model):
    """پروژه‌های بزرگ نیازمند مشارکت چند شرکت"""
    __tablename__ = 'consortium_projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # اطلاعات پروژه
    industry = db.Column(db.String(100))  # صنعت مرتبط
    target_country = db.Column(db.String(100))  # کشور هدف
    required_capacity = db.Column(db.String(200))  # ظرفیت مورد نیاز
    estimated_value = db.Column(db.String(100))  # ارزش تقریبی
    
    # وضعیت
    status = db.Column(db.String(20), default='open')  # open, forming, active, completed, cancelled
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(tehran_tz))
    
    # اعضا
    members = db.relationship('ConsortiumMember', back_populates='project', cascade='all, delete-orphan')
    
    # قرارداد
    contract = db.relationship('ConsortiumContract', back_populates='project', uselist=False, cascade='all, delete-orphan')


class ConsortiumMember(db.Model):
    """اعضای هر کنسرسیوم"""
    __tablename__ = 'consortium_members'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('consortium_projects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # نقش در کنسرسیوم
    role = db.Column(db.String(50), nullable=False)  # e.g., 'leader', 'supplier', 'logistics_partner'
    
    # سهم سرمایه (درصد)
    capital_share = db.Column(db.Integer, default=0)  # 0-100
    
    # سهم سود (درصد)
    profit_share = db.Column(db.Integer, default=0)  # 0-100
    
    # وضعیت
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(tehran_tz))
    status = db.Column(db.String(20), default='active')  # active, left, removed
    
    # روابط
    project = db.relationship('ConsortiumProject', back_populates='members')
    user = db.relationship('User', backref='consortium_memberships')


class ConsortiumContract(db.Model):
    """قرارداد هوشمند کنسرسیوم"""
    __tablename__ = 'consortium_contracts'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('consortium_projects.id'), unique=True, nullable=False)
    
    # مفاد قرارداد
    terms = db.Column(db.Text)  # شرایط و ضوابط
    responsibilities = db.Column(db.Text)  # مسئولیت‌های هر عضو
    
    # توزیع سود
    profit_distribution_method = db.Column(db.String(100))  # e.g., 'proportional_to_capital'
    
    # شرایط خروج
    exit_conditions = db.Column(db.Text)
    
    # امضاها
    signed_by = db.Column(db.Text)  # لیست کاربرانی که امضا کرده‌اند (JSON)
    fully_signed = db.Column(db.Boolean, default=False)
    
    # زمان
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(tehran_tz))
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(tehran_tz))
    
    # رابطه
    project = db.relationship('ConsortiumProject', back_populates='contract')


class PartnerMatch(db.Model):
    """پیشنهادات شریک هوشمند"""
    __tablename__ = 'partner_matches'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # کاربران برای تطبیق
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # امتیاز تطابق (۰-۱۰۰)
    match_score = db.Column(db.Integer, default=0)
    
    # دلیل تطابق
    match_reasons = db.Column(db.Text)  # e.g., 'مکمل در صنعت X', 'تجربه در کشور Y'
    
    # وضعیت
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(tehran_tz))
    
    # روابط
    user1 = db.relationship('User', foreign_keys=[user1_id], backref='partner_matches_as_user1')
    user2 = db.relationship('User', foreign_keys=[user2_id], backref='partner_matches_as_user2')
