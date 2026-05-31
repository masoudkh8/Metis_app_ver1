# models/auth.py
# مدل‌های امنیتی و احراز هویت پیشرفته

from . import db
from datetime import datetime, timedelta, timezone

import secrets
import base64
import hashlib
import time


def utc_now():
    """برگرداندن زمان فعلی به UTC بدون timezone info برای سازگاری با دیتابیس"""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class PasswordResetToken(db.Model):
    """توکن بازیابی رمز عبور با انقضا"""
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    used_at = db.Column(db.DateTime, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)  # IP درخواست‌دهنده
    
    # Relationship
    user = db.relationship('User', backref=db.backref('reset_tokens', lazy='dynamic', cascade='all, delete-orphan'))
    
    def __init__(self, user_id, expiry_hours=24, ip_address=None):
        self.user_id = user_id
        self.token = secrets.token_urlsafe(32)
        self.created_at = utc_now()
        self.expires_at = self.created_at + timedelta(hours=expiry_hours)
        self.ip_address = ip_address
    
    @staticmethod
    def create_for_user(user, expiry_hours=1, ip_address=None):
        """ایجاد توکن بازیابی برای کاربر و ذخیره در دیتابیس"""
        import hashlib
        
        # باطل کردن توکن‌های قبلی استفاده نشده
        PasswordResetToken.query.filter_by(
            user_id=user.id, 
            used=False
        ).update({'used': True}, synchronize_session=False)

        # ایجاد توکن جدید - ذخیره توکن اصلی قبل از هش کردن
        reset_token = PasswordResetToken(
            user_id=user.id,
            expiry_hours=expiry_hours,
            ip_address=ip_address
        )
        
        # ذخیره توکن اصلی برای بازگرداندن
        original_token = reset_token.token
        
        # هش کردن توکن برای ذخیره امن در دیتابیس
        reset_token.token = hashlib.sha256(reset_token.token.encode()).hexdigest()
        
        db.session.add(reset_token)
        db.session.commit()
        
        return original_token  # بازگرداندن توکن اصلی (نه هش شده)
    
    def is_valid(self):
        """بررسی اعتبار توکن"""
        return not self.used and utc_now() < self.expires_at


    def mark_as_used(self):
        """علامت‌گذاری توکن به عنوان استفاده شده"""
        self.used = True
        self.used_at = utc_now()
        db.session.commit()
    
    def __repr__(self):
        return f"<PasswordResetToken for User {self.user_id}>"


class LoginSession(db.Model):
    """مدیریت جلسات ورود کاربران"""
    __tablename__ = 'login_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    session_token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    
    # اطلاعات دستگاه و موقعیت
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 support
    user_agent = db.Column(db.Text, nullable=True)
    device_type = db.Column(db.String(50), nullable=True)  # mobile, desktop, tablet
    browser = db.Column(db.String(50), nullable=True)
    os = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(50), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    
    # وضعیت جلسه
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_current = db.Column(db.Boolean, default=False)  # آیا این جلسه فعلی است؟
    created_at = db.Column(db.DateTime, default=utc_now, index=True)
    last_activity = db.Column(db.DateTime, default=utc_now)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    # Remember Me
    remember_me = db.Column(db.Boolean, default=False)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('sessions', lazy='dynamic', cascade='all, delete-orphan'))
    
    def __init__(self, user_id, request=None, remember_me=False, session_duration_days=30):
        self.user_id = user_id
        self.session_token = secrets.token_urlsafe(32)
        self.remember_me = remember_me
        
        if request:
            self.ip_address = request.remote_addr
            self.user_agent = request.headers.get('User-Agent', '')[:500]
            self._parse_user_agent()
        
        self.created_at = utc_now()
        self.last_activity = utc_now()
        
        # تنظیم زمان انقضا بر اساس Remember Me
        if remember_me:
            self.expires_at = self.created_at + timedelta(days=session_duration_days)
        else:
            # جلسه معمولی: 24 ساعت بدون فعالیت منقضی می‌شود
            self.expires_at = self.created_at + timedelta(hours=24)
    
    @staticmethod
    def create_session(user, request=None, remember_me=False):
        """ایجاد جلسه ورود جدید برای کاربر"""
        # غیرفعال کردن جلسات قدیمی منقضی شده
        LoginSession.query.filter_by(
            user_id=user.id,
            is_active=True
        ).filter(
            LoginSession.expires_at < utc_now()
        ).update({'is_active': False})
        
        # ایجاد جلسه جدید
        new_session = LoginSession(
            user_id=user.id,
            request=request,
            remember_me=remember_me
        )
        
        db.session.add(new_session)
        db.session.commit()
        
        return new_session
    
    @staticmethod
    def logout_all_sessions(user_id):
        """خروج از تمام جلسات کاربر به جز جلسه فعلی"""
        LoginSession.query.filter_by(
            user_id=user_id,
            is_active=True
        ).update({'is_active': False})
        db.session.commit()
    
    def _parse_user_agent(self):
        """تجزیه User Agent برای تشخیص دستگاه و مرورگر"""
        ua = self.user_agent or ''
        
        # تشخیص نوع دستگاه
        if 'Mobile' in ua or 'Android' in ua or 'iPhone' in ua:
            self.device_type = 'mobile'
        elif 'Tablet' in ua or 'iPad' in ua:
            self.device_type = 'tablet'
        else:
            self.device_type = 'desktop'
        
        # تشخیص مرورگر
        if 'Chrome' in ua and 'Edg' not in ua:
            self.browser = 'Chrome'
        elif 'Firefox' in ua:
            self.browser = 'Firefox'
        elif 'Safari' in ua and 'Chrome' not in ua:
            self.browser = 'Safari'
        elif 'Edg' in ua:
            self.browser = 'Edge'
        elif 'MSIE' in ua or 'Trident' in ua:
            self.browser = 'Internet Explorer'
        else:
            self.browser = 'Other'
        
        # تشخیص سیستم عامل
        if 'Windows' in ua:
            self.os = 'Windows'
        elif 'Mac OS' in ua or 'MacOS' in ua:
            self.os = 'macOS'
        elif 'Linux' in ua:
            self.os = 'Linux'
        elif 'Android' in ua:
            self.os = 'Android'
        elif 'iPhone' in ua or 'iPad' in ua:
            self.os = 'iOS'
        else:
            self.os = 'Other'
    
    def update_activity(self):
        """به‌روزرسانی زمان آخرین فعالیت"""
        self.last_activity = utc_now()
        if self.remember_me and self.expires_at:
            # تمدید انقضا برای Remember Me
            self.expires_at = utc_now() + timedelta(days=30)
        else:
            # تمدید انقضا برای جلسه معمولی
            self.expires_at = utc_now() + timedelta(hours=24)
        db.session.commit()
    
    def is_expired(self):
        """بررسی انقضای جلسه"""
        return utc_now() > self.expires_at if self.expires_at else False
    
    def revoke(self):
        """ابطال جلسه"""
        self.is_active = False
        db.session.commit()
    
    def logout(self):
        """خروج از جلسه"""
        self.revoke()
        db.session.commit()
    
    def to_dict(self):
        """تبدیل به دیکشنری برای نمایش"""
        return {
            'id': self.id,
            'session_token': self.session_token[:8] + '...',  # نمایش بخشی از توکن
            'ip_address': self.ip_address,
            'device_type': self.device_type,
            'browser': self.browser,
            'os': self.os,
            'country': self.country,
            'city': self.city,
            'is_active': self.is_active,
            'is_current': self.is_current,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'last_activity': self.last_activity.strftime('%Y-%m-%d %H:%M:%S') if self.last_activity else None,
            'expires_at': self.expires_at.strftime('%Y-%m-%d %H:%M:%S') if self.expires_at else None,
            'remember_me': self.remember_me
        }
    
    def __repr__(self):
        return f"<LoginSession for User {self.user_id} - {self.device_type}>"


class ActivityLog(db.Model):
    """لاگ فعالیت‌های کاربران برای امنیت و ممیزی"""
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    
    # نوع فعالیت
    activity_type = db.Column(db.String(50), nullable=False, index=True)
    # login, logout, login_failed, password_change, email_change, profile_update, 
    # 2fa_enabled, 2fa_disabled, session_created, session_revoked, etc.
    
    # جزئیات فعالیت
    description = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    
    # وضعیت
    success = db.Column(db.Boolean, default=True, index=True)
    failure_reason = db.Column(db.String(255), nullable=True)
    
    # متادیتا اضافی (JSON) - renamed from metadata to extra_data to avoid SQLAlchemy reserved word
    extra_data = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=utc_now, index=True)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('activity_logs', lazy='dynamic', cascade='all, delete-orphan'))
    
    def __init__(self, user_id=None, activity_type='unknown', description=None, 
                 request=None, success=True, failure_reason=None, extra_data=None):
        self.user_id = user_id
        self.activity_type = activity_type
        self.description = description
        self.success = success
        self.failure_reason = failure_reason
        
        if request:
            self.ip_address = request.remote_addr
            self.user_agent = request.headers.get('User-Agent', '')[:500]
        
        if extra_data:
            import json
            self.extra_data = json.dumps(extra_data)
    
    @staticmethod
    def log_activity(user_id=None, activity_type='unknown', description=None,
                     request=None, success=True, failure_reason=None, status=None, extra_data=None):
        """ثبت فعالیت کاربر در لاگ"""
        # پشتیبانی از پارامتر status برای سازگاری با کدهای قدیمی
        if status is not None:
            success = (status == 'success')
        
        log = ActivityLog(
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            request=request,
            success=success,
            failure_reason=failure_reason,
            extra_data=extra_data
        )
        
        db.session.add(log)
        db.session.commit()
        
        return log
    
    def to_dict(self):
        """تبدیل به دیکشنری برای نمایش"""
        import json
        return {
            'id': self.id,
            'user_id': self.user_id,
            'activity_type': self.activity_type,
            'description': self.description,
            'ip_address': self.ip_address,
            'success': self.success,
            'failure_reason': self.failure_reason,
            'metadata': json.loads(self.extra_data) if self.extra_data else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
    
    def __repr__(self):
        return f"<ActivityLog {self.activity_type} - User {self.user_id}>"


class EmailVerificationToken(db.Model):
    """توکن تأیید ایمیل"""
    __tablename__ = 'email_verification_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    email = db.Column(db.String(120), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('email_tokens', lazy='dynamic', cascade='all, delete-orphan'))
    
    def __init__(self, user_id, email, expiration_hours=48):
        self.user_id = user_id
        self.email = email
        self.token = secrets.token_urlsafe(32)
        self.created_at = utc_now()
        self.expires_at = self.created_at + timedelta(hours=expiration_hours)
    
    def is_valid(self):
        """بررسی اعتبار توکن"""
        return not self.used and utc_now() < self.expires_at
    
    def mark_as_used(self):
        """علامت‌گذاری توکن به عنوان استفاده شده"""
        self.used = True
    
    def __repr__(self):
        return f"<EmailVerificationToken for {self.email}>"


class TwoFactorBackupCode(db.Model):
    """کدهای پشتیبان احراز هویت دو مرحله‌ای"""
    __tablename__ = 'two_factor_backup_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    code_hash = db.Column(db.String(255), nullable=False, index=True)
    used = db.Column(db.Boolean, default=False, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('two_factor_backup_codes_rel', lazy='dynamic', cascade='all, delete-orphan'))
    
    @staticmethod
    def generate_backup_codes(user_id, count=10):
        """تولید کدهای پشتیبان"""
        codes = []
        for _ in range(count):
            code = ''.join([str(secrets.randbelow(10)) for _ in range(8)])  # 8 رقمی
            codes.append(code)
            backup_code = TwoFactorBackupCode(
                user_id=user_id,
                code_hash=hashlib.sha256(code.encode()).hexdigest()
            )
            db.session.add(backup_code)
        
        db.session.commit()
        return codes
    
    @staticmethod
    def verify_backup_code(user_id, code):
        """بررسی کد پشتیبان"""
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        backup_code = TwoFactorBackupCode.query.filter_by(
            user_id=user_id, 
            code_hash=code_hash, 
            used=False
        ).first()
        
        if backup_code:
            backup_code.used = True
            backup_code.used_at = utc_now()
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def invalidate_all(user_id):
        """باطل کردن تمام کدهای پشتیبان"""
        TwoFactorBackupCode.query.filter_by(user_id=user_id, used=False).update({'used': True})
        db.session.commit()
    
    def __repr__(self):
        return f"<TwoFactorBackupCode user_id={self.user_id} used={self.used}>"
