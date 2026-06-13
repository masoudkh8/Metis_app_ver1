# routes/users/routes.py
import hashlib
from extensions import cache
from flask_wtf.csrf import generate_csrf
from datetime import datetime
import pytz
tehran_tz = pytz.timezone('Asia/Tehran')
import os
import json
import secrets
from werkzeug.utils import secure_filename
from metisma.services.email_service import generate_verification_token, send_verification_email ,verify_email_token
from services.access_control import has_permission, permission_required
from services.permissions import Permission
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from functools import wraps
from extensions import limiter
from models import Message, Notification, db, user
from models.user import User, Role
from models.auth import PasswordResetToken, LoginSession, ActivityLog, EmailVerificationToken, TwoFactorBackupCode
from models.port import Port
from flask_babel import gettext as _
from . import users_bp,root_bp
from .auth import verify_phone, verify_2fa_login, show_verify_email_page
# Import permissions routes to register them under users_bp
from . import permissions_routes

from config import Config
from PIL import Image
import requests

# reCAPTCHA validation helper
def verify_recaptcha(response_token):
    """Verify reCAPTCHA token with Google"""
    if not Config.RECAPTCHA_ENABLED or not response_token:
        return True  # Skip if disabled
    
    secret_key = Config.RECAPTCHA_SECRET_KEY
    verify_url = "https://www.google.com/recaptcha/api/siteverify"
    
    try:
        payload = {
            'secret': secret_key,
            'response': response_token
        }
        response = requests.post(verify_url, data=payload, timeout=5)
        result = response.json()
        return result.get('success', False) and result.get('score', 0) >= 0.5
    except Exception as e:
        current_app.logger.error(f"reCAPTCHA verification failed: {e}")
        return False


# ==============================
# دکوریتورهای دسترسی مبتنی بر نقش
# ==============================
def role_required(*roles):
    """دکوریتور برای محدود کردن دسترسی بر اساس نقش کاربر"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash(_("Please log in first."), "error")
                return redirect(url_for('users.login'))
            
            if current_user.role.value not in roles:
                flash(_("Unauthorized access. This section is for specific roles."), "error")
                return redirect(url_for('users.profile'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ==============================
# توابع کمکی برای آپلود امن فایل
# ==============================
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    """بررسی پسوند فایل مجاز"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file(file, image_only=False):
    """اعتبارسنجی کامل فایل آپلود شده"""
    if not file or file.filename == '':
        return False, "No file selected."
    
    # Determine allowed extensions based on type
    if image_only:
        allowed_exts = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
        max_size = current_app.config.get('MAX_IMAGE_SIZE', 5 * 1024 * 1024)
        error_msg = "File type not allowed (JPG, PNG, GIF, WEBP only)"
    else:
        allowed_exts = ALLOWED_EXTENSIONS
        max_size = MAX_FILE_SIZE
        error_msg = "File type not allowed (PDF, PNG, JPG only)"
    
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_exts:
        return False, error_msg
    
    # بررسی اندازه فایل
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > max_size:
        size_mb = max_size / (1024 * 1024)
        return False, f"File size must not exceed {size_mb:.0f}MB"
    
    return True, ""


# routes/users/routes.py یا app.py
@root_bp.route('/')
@cache.cached(timeout=300, query_string=True)  # کش به مدت 5 دقیقه
def main_page():
    return render_template('landing.html')


@users_bp.before_request
def make_session_permanent():
    """Make sessions permanent so they expire after PERMANENT_SESSION_LIFETIME"""
    session.permanent = True


@users_bp.route('/create_first_admin', methods=['GET', 'POST'])
def create_first_admin():
    # فقط در محیط توسعه یا وقتی هیچ ادمینی وجود ندارد قابل دسترسی است
    if User.query.filter_by(role=Role.ADMIN, is_active=True).first():
        flash(_("There is already an admin."))
        return redirect(url_for('users.login'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not username or not email or not password:
            flash(_("❌ Please fill in all fields."))
            return redirect(url_for('users.create_first_admin'))

        if len(username) < 3:
            flash(_("❌ Username must be at least 3 characters long."))
            return redirect(url_for('users.create_first_admin'))

        if '@' not in email:
            flash(_("❌ The email address is invalid."))
            return redirect(url_for('users.create_first_admin'))

        if len(password) < 8:
            flash(_("❌ The password must be at least 8 characters long."))
            return redirect(url_for('users.create_first_admin'))

        if User.query.filter_by(username=username, is_active=True).first():
            flash(_("❌ Username already taken."))
            return redirect(url_for('users.create_first_admin'))

        if User.query.filter_by(email=email, is_active=True).first():
            flash(_("❌ Email already used."))
            return redirect(url_for('users.create_first_admin'))

        try:
            hashed = generate_password_hash(password)
            user = User(
                username=username,
                email=email,
                password_hash=hashed,
                role=Role.ADMIN,
                is_premium=True,
                is_active=True
            )

            db.session.add(user)
            db.session.commit()
            flash(_("✅ The first admin was created successfully. Please log in."))
            return redirect(url_for('admin.login'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating admin: {e}")
            flash(_("❌ An error occurred while creating the admin."))
            return redirect(url_for('users.create_first_admin'))

    return render_template('admin/create_first_admin.html')


##############
# در routes/users/routes.py یا root_bp
@users_bp.route('/set-language')
def set_language():
    """Set user language preference"""
    lang = request.args.get('lang', 'fa')
    if lang in ['fa', 'en']:
        session['lang'] = lang
        # ریدایرکت به صفحه قبلی یا خانه
        next_page = request.args.get('next') or request.referrer or url_for('root.index')
        return redirect(next_page)
    return redirect(url_for('root.index'))





# -------------------------------
# ثبت نام
# -------------------------------
# Register (Request 2: Smart Multi-step Registration)
# ثبت‌نام پیشرفته با CAPTCHA و تأیید ایمیل
# -------------------------------
@users_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")  # Rate limiting for registration
def register():
    if current_user.is_authenticated:
        flash(_("You already have an account. Please log out first to register a new account."))
        return redirect(url_for('users.profile'))
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role')
        company = request.form.get('company', '').strip()
        country = request.form.get('country', '').strip()
        phone = request.form.get('phone', '').strip()
        
        # New specialized fields
        expertise_area = request.form.get('expertise_area', '').strip()
        job_title = request.form.get('job_title', '').strip()
        bio = request.form.get('bio', '').strip()
        website = request.form.get('website', '').strip()
        
        # reCAPTCHA verification
        recaptcha_response = request.form.get('g-recaptcha-response')
        if not verify_recaptcha(recaptcha_response):
            flash(_("reCAPTCHA verification failed. Please try again."), "error")
            return redirect(url_for('users.register'))
        
        # Precise input validation (Request 2)
        errors = []
        
        # Username check
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters long.")
        if User.query.filter_by(username=username, is_active=True).first():
            errors.append("Username already taken.")
        
        # Email check
        if not email or '@' not in email:
            errors.append("Invalid email address.")
        if User.query.filter_by(email=email, is_active=True).first():
            errors.append("Email already used.")
        
        # Strong password check (Request 2)
        if not password or len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        elif password != confirm_password:
            errors.append("Passwords do not match.")
        else:
            # Password strength check
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_digit = any(c.isdigit() for c in password)
            
            if not (has_upper and has_lower and has_digit):
                errors.append("Password should contain uppercase, lowercase, and numbers for better security.")
        
        # Role check
        if not role or not Role.has_value(role):
            errors.append("Invalid role selected.")
        
        # Phone check
        if phone and (not phone.isdigit() or len(phone.replace('+', '').replace('-', '')) < 10):
            errors.append("Invalid phone number.")
        
        # If there are errors, return to form
        if errors:
            for error in errors:
                flash(error)
            return redirect(url_for('users.register'))
        # Create new user - DEBUG VERSION
        try:
            hashed = generate_password_hash(password)
            new_user = User(
                username=username, email=email, password_hash=hashed,
                role=Role(role), company_name=company, country=country, phone=phone,
                expertise_area=expertise_area, job_title=job_title, bio=bio, website=website,
                trust_score_value=0,  # شروع با امتیاز صفر برای سخت‌گیری Trust Score
                is_email_verified=False,
                registered_at=datetime.now(tehran_tz)
            )

            db.session.add(new_user)
            db.session.commit()
            print(f"✅ User {new_user.username} created in DB")

            # Create user profile
            from models.user import UserProfile
            if not new_user.profile:
                profile = UserProfile(user=new_user)
                db.session.add(profile)
                db.session.commit()
                print(f"✅ Profile created for {new_user.username}")

            # ==========================================
            # ✅ بخش ایمیل - با دیباگ دقیق
            # ==========================================
            print("📧 Starting email verification process...")

            try:
                # 1. تولید توکن
                print("  → Generating token...")
                from metisma.services.email_service import generate_verification_token
                raw_token = generate_verification_token(new_user)
                print(f"  → Token generated: {raw_token[:10]}...")

                # 2. ارسال ایمیل
                print("  → Sending email...")
                from metisma.services.email_service import send_verification_email
                email_sent, error_msg = send_verification_email(new_user, raw_token)

                if email_sent:
                    print(f"  → ✅ Email sent to {new_user.email}")
                    flash(_("✅ Registration successful! Verification email sent."), "success")
                else:
                    print(f"  → ❌ Email failed: {error_msg}")

                    flash(
                        _("Account created but email failed: %(error_msg)s") % {"error_msg": error_msg},
                        "warning"
                    )

            except Exception as email_error:
                # خطای اختصاصی بخش ایمیل
                print(f"  → 💥 Email subsystem error: {email_error}")
                import traceback
                traceback.print_exc()

                flash(
                    _("Account created but email system error: %(error)s") % {"error": str(email_error)},
                    "warning"
                )
            return redirect(url_for('users.login'))

        except Exception as e:
            # خطای اصلی و نهایی
            db.session.rollback()
            print(f"💥 CRITICAL ERROR in register: {e}")
            import traceback
            traceback.print_exc()  # چاپ کامل خطا در کنسول
            flash(_("Registration error: %(error)s") % {"error": str(e)}, "error")
            return redirect(url_for('users.register'))

    return render_template('users/register.html', roles=Role)




# -------------------------------
# ورود
# -------------------------------
@users_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")  # Rate limiting برای جلوگیری از brute force
def login():

    # اگر کاربر قبلاً لاگین کرده و 2FA فعال نیست، مستقیم به پروفایل برود
    if current_user.is_authenticated and not current_user.two_factor_enabled:
        return redirect(url_for('users.profile'))
    
    # اگر کاربر در حال گذر از مرحله 2FA است، اجازه نده دوباره لاگین کند
    if session.get('2fa_pending_user_id'):
        return redirect(url_for('users.verify_2fa_login'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        raw_remember_me = request.form.get('remember', False)
        remember_me = True if raw_remember_me == 'on' or raw_remember_me is True else False

        user = User.query.filter_by(email=email, is_active=True).first()

        # بررسی قفل بودن حساب
        if user and user.locked_until:
            if datetime.utcnow() < user.locked_until:
                lock_time = user.locked_until.strftime('%Y-%m-%d %H:%M')

                flash(
                    _("[LOCKED] Your account is locked until %(lock_time)s due to failed attempts.") % {
                        "lock_time": lock_time},
                    "error"
                )
                ActivityLog.log_activity(
                    user_id=user.id,
                    activity_type='login_blocked',
                    description='Account locked due to failed attempts',
                    request=request,
                    success=False,
                    failure_reason='account_locked'
                )
                return render_template('users/login.html')
            else:
                # رفع قفل خودکار
                user.locked_until = None
                user.failed_login_attempts = 0
                db.session.commit()

        if user and check_password_hash(user.password_hash, password):

            # ✅ بررسی تأیید ایمیل قبل از ورود
            if not user.is_email_verified:
                flash(_("❌ Please verify your email before logging in. Check your inbox for the verification link."),
                      "warning")
                ActivityLog.log_activity(
                    user_id=user.id,
                    activity_type='login_blocked',
                    description='Login blocked - Email not verified',
                    request=request,
                    success=False,
                    failure_reason='email_not_verified'
                )
                return render_template('users/login.html')


            # ورود موفق - ریست کردن تلاش‌های ناموفق
            if user.failed_login_attempts > 0:
                user.failed_login_attempts = 0
                user.locked_until = None
                db.session.commit()
            
            # لاگ فعالیت ورود موفق
            ActivityLog.log_activity(
                user_id=user.id,
                activity_type='login',
                description='Successful password authentication',
                request=request,
                success=True
            )
            
            # اگر 2FA فعال است، به صفحه تأیید کد برو
            if user.two_factor_enabled:
                # ذخیره اطلاعات موقت در session برای مرحله بعد
                session['2fa_pending_user_id'] = user.id
                session['2fa_remember_me'] = remember_me
                flash(_("✅ Password verified. Please enter your 2FA code."), "info")
                return redirect(url_for('users.verify_2fa_login'))
            
            # اگر 2FA فعال نیست، ادامه فرآیند ورود عادی
            # ایجاد جلسه جدید
            login_session = LoginSession.create_session(
                user=user,
                request=request,
                remember_me=remember_me
            )
            session_token = login_session.session_token
            
            login_user(user, remember=remember_me)
            
            # ذخیره توکن جلسه در cookie
            response = redirect(url_for('users.profile'))
            response.set_cookie('session_token', session_token, httponly=True, secure=True, samesite='Lax')
            
            flash(_("✅ Welcome!"))
            return response
        else:
            # ورود ناموفق
            if user:
                user.failed_login_attempts += 1
                
                # قفل حساب پس از 5 تلاش ناموفق
                if user.failed_login_attempts >= 5:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=15)  # 15 دقیقه قفل
                    db.session.commit()
                    
                    ActivityLog.log_activity(
                        user_id=user.id,
                        activity_type='account_locked',
                        description='Account locked due to 5 failed attempts',
                        request=request,
                        success=False,
                        failure_reason='too_many_failed_attempts'
                    )
                    
                    flash(_("❌ Your account has been locked for 15 minutes due to too many failed attempts."))
                else:
                    db.session.commit()
                    
                    ActivityLog.log_activity(
                        user_id=user.id,
                        activity_type='login_failed',
                        description=f'Failed login attempt ({user.failed_login_attempts}/5)',
                        request=request,
                        success=False,
                        failure_reason='invalid_password'
                    )
                    
                    remaining_attempts = 5 - user.failed_login_attempts
                    flash(
                        _("Incorrect email or password. %(attempts)s more attempts before account is locked.") % {
                            "attempts": remaining_attempts
                        },
                        "error"
                    )
            else:
                # کاربر وجود ندارد - برای امنیت پیام کلی نمایش می‌دهیم
                flash(_("❌ Incorrect email or password."))
    
    support_user = User.query.filter_by(role=Role.ADMIN, is_active=True).first()
    return render_template('users/login.html', support_user=support_user)



# -------------------------------
# ویرایش پروفایل پیشرفته
# -------------------------------
@users_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        # اطلاعات پایه
        current_user.company_name = request.form.get('company', '').strip()
        current_user.country = request.form.get('country', '').strip()
        current_user.phone = request.form.get('phone', '').strip()
        
        # فیلدهای تخصصی جدید (درخواست ۴)
        current_user.expertise_area = request.form.get('expertise_area', '').strip()
        current_user.job_title = request.form.get('job_title', '').strip()
        current_user.bio = request.form.get('bio', '').strip()
        current_user.website = request.form.get('website', '').strip()
        
        # پردازش شبکه‌های اجتماعی (JSON format)
        social_links = {
            'linkedin': request.form.get('linkedin', '').strip(),
            'telegram': request.form.get('telegram', '').strip(),
            'whatsapp': request.form.get('whatsapp', '').strip()
        }
        # حذف مقادیر خالی
        social_links = {k: v for k, v in social_links.items() if v}
        current_user.social_links = json.dumps(social_links) if social_links else None
        
        # ✅ آپلود عکس پروفایل
        profile_file = request.files.get('profile_image')
        if profile_file and profile_file.filename != '':
            is_valid, error_msg = validate_file(profile_file, image_only=True)
            if not is_valid:

                flash(
                    _("Error: %(error)s") % {"error": error_msg},
                    "error"
                )
            else:
                upload_folder = current_app.config.get('PROFILE_UPLOAD_FOLDER', 'static/uploads/profiles')
                os.makedirs(upload_folder, exist_ok=True)
                filename = secure_filename(profile_file.filename)
                unique_filename = f"{current_user.id}_{secrets.token_hex(8)}_{filename}"
                filepath = os.path.join(upload_folder, unique_filename)
                img = Image.open(profile_file)
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                img.thumbnail((400, 400), Image.Resampling.LANCZOS)
                img.save(filepath, quality=85, optimize=True)
                if current_user.profile_image:
                    old_path = os.path.join(current_app.root_path, current_user.profile_image.lstrip('/'))
                    if os.path.exists(old_path):
                        try:
                            os.remove(old_path)
                        except Exception as e:
                            current_app.logger.error(f"Error deleting old profile image: {e}")

                current_user.profile_image = url_for('static', filename=f'uploads/profiles/{unique_filename}')
                flash(_("✅ Profile picture updated successfully."), "success")

        db.session.commit()
        flash(_("✅ Profile updated successfully."), "success")
        return redirect(url_for('users.profile'))
    
    # GET: نمایش فرم ویرایش پروفایل
    return render_template('users/profile_edit.html', user=current_user)







# -------------------------------
# تنظیمات حساب کاربری
# -------------------------------
@users_bp.route('/account-settings')
@login_required
def account_settings():
    """نمایش صفحه تنظیمات حساب کاربری"""
    return render_template('users/account_settings.html', user=current_user)


# -------------------------------
# تغییر رمز عبور
# -------------------------------
@users_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """تغییر رمز عبور کاربر با اعتبارسنجی کامل"""
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    # بررسی رمز عبور فعلی
    if not check_password_hash(current_user.password_hash, current_password):
        flash(_("❌ The current password is incorrect."), "error")
        return redirect(url_for('users.account_settings'))
    
    # اعتبارسنجی رمز عبور جدید
    if len(new_password) < 8:
        flash(_("❌ New password must be at least 8 characters long."), "error")
        return redirect(url_for('users.account_settings'))
    
    # بررسی تطابق رمز جدید و تکرار آن
    if new_password != confirm_password:
        flash(_("❌ New password and repeat password do not match."), "error")
        return redirect(url_for('users.account_settings'))
    
    # بررسی تکراری نبودن رمز عبور جدید با رمز قبلی
    if check_password_hash(current_user.password_hash, new_password):
        flash(_("⚠️ New password must not be the same as previous password."), "warning")
        return redirect(url_for('users.account_settings'))
    
    try:
        # به‌روزرسانی رمز عبور با هش کردن
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        # لاگ عملیات برای امنیت
        current_app.logger.info(f"Password changed for user {current_user.id} ({current_user.email})")

        flash(_("✅ Your password has been changed successfully."), "success")
        return redirect(url_for('users.account_settings'))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error changing password for user {current_user.id}: {e}")
        flash(_("❌ An error occurred while changing the password. Please try again."), "error")
        return redirect(url_for('users.account_settings'))


# -------------------------------
# حذف حساب کاربری
# -------------------------------
@users_bp.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    """حذف نرم حساب کاربری با تأیید دو مرحله‌ای"""
    
    # بررسی وجود چک‌باکس تأیید
    confirmation = request.form.get('confirmation_checkbox')
    if not confirmation:
        flash(_("⚠️ Please check the confirmation checkbox to delete the account."), "warning")
        return redirect(url_for('users.account_settings'))
    
    user_id = current_user.id
    user_email = current_user.email
    username = current_user.username
    
    try:
        # غیرفعال‌سازی حساب کاربری (soft delete)
        current_user.is_active = False
        
        # حذف توکن‌های فعال کاربر (در صورت وجود مدل Session/Token)
        # این بخش بستگی به پیاده‌سازی session management دارد
        # فعلاً logout انجام می‌دهیم
        logout_user()
        
        # لاگ عملیات برای امنیت
        current_app.logger.warning(
            f"Account deleted: User ID={user_id}, Email={user_email}, Username={username}"
        )
        
        # ارسال نوتیفیکیشن به ادمین (اختیاری)
        try:
            from models.notification import Notification
            admin_notification = Notification(
                user_id=None,  # نوتیفیکیشن سیستمی
                title = "Delete Account",
                message = f"The account {username} ({user_email}) has been deleted.",
                category = "admin_alert",
                is_read = False
            )
            db.session.add(admin_notification)
            db.session.commit()
        except Exception as notif_error:
            db.session.rollback()
            current_app.logger.error(f"Error creating admin notification: {notif_error}")
        
        flash(_("🗑️ Your account has been successfully deleted. Thank you for your cooperation."), "success")
        return redirect(url_for('users.register'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting account for user {user_id}: {e}")
        flash(_("❌ An error occurred while deleting the account. Please contact support."), "error")
        return redirect(url_for('users.account_settings'))


# -------------------------------
# خروج
# -------------------------------
@users_bp.route('/logout')
@login_required
def logout():
    # لاگ فعالیت خروج
    ActivityLog.log_activity(
        user_id=current_user.id,
        activity_type='logout',
        description='Logout',
        request=request,
        success=True
    )
    
    # باطل کردن جلسه فعلی
    session_token = request.cookies.get('session_token')
    if session_token:
        from hashlib import sha256
        hashed_token = sha256(session_token.encode()).hexdigest()
        login_session = LoginSession.query.filter_by(session_token=hashed_token).first()
        if login_session:
            login_session.revoke()
    
    logout_user()
    flash(_("👋 You have successfully logged out."))
    return redirect(url_for('users.login'))


@users_bp.route('/profile')
@login_required
def profile():
    """نمایش پروفایل کاربر با اطلاعات کامل و وضعیت مدارک"""

    if not current_user.is_active:
        logout_user()
        flash(_("❌ This account is inactive."))
        return redirect(url_for('users.login'))

    # محاسبه تعداد اعلان‌های خوانده‌نشده
    from models.notification import Notification
    unread_notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    # محاسبه تعداد سفارش‌های در انتظار (فقط برای PRODUCER)
    pending_orders = 0
    if current_user.role == Role.PRODUCER:
        from models.order import OrderStatus,Order
        pending_orders = Order.query.filter_by(seller_id=current_user.id, status=OrderStatus.PENDING).count()

    # دریافت مدارک آپلود شده برای بررسی وضعیت تأیید
    verification_docs = json.loads(current_user.verification_documents) if current_user.verification_documents else []
    
    # تعیین وضعیت تأیید مدارک
    document_status = 'not_uploaded'  # not_uploaded, pending, approved, rejected
    if verification_docs:
        # اگر مدارک آپلود شده باشند، فرض می‌کنیم در حال بررسی هستند
        # در آینده می‌توان فیلد جداگانه برای وضعیت هر مدرک اضافه کرد
        document_status = 'pending'
        if current_user.is_verified:
            document_status = 'approved'
    
    # محاسبه وضعیت pending tasks
    pending_tasks = []
    if not current_user.is_verified and verification_docs:
        pending_tasks.append({
            'title': 'Checking Identity Verification Documents',
            'description': 'Your documents are being reviewed by the admin',
            'status': 'pending',
            'icon': 'document'
        })
    elif not current_user.is_verified and not verification_docs:
        pending_tasks.append({
            'title': 'Upload Identity Verification Documents',
            'description': 'Upload your documents to increase your trust score',
            'status': 'action_required',
            'action_url': url_for('users.upload_documents'),
            'icon': 'upload'
        })
    
    # پروفایل کامل برای داشبورد هوشمند
    support_user = User.query.filter_by(username='support', is_active=True).first()

    if not support_user:
        support_user = User.query.filter_by(role=Role.PRODUCER, is_active=True).first()

    seller = User.query.filter_by(role=Role.PRODUCER, is_active=True).first()
    buyer = User.query.filter_by(role=Role.BUYER, is_active=True).first()
    broker = User.query.filter_by(role=Role.BROKER, is_premium=True, is_active=True).first()

    # 🔥 اضافه شده: دریافت ۳ پست اخیر کاربر جاری
    from models.social import Post
    my_recent_posts = Post.query.filter_by(
        author_id=current_user.id
    ).order_by(Post.created_at.desc()).limit(3).all()

    return render_template('users/profile.html', 
                          user=current_user,
                          support_user=support_user,
                          pending_orders=pending_orders,
                          unread_notifications=unread_notifications,
                          seller=seller,
                          buyer=buyer,
                          broker=broker,
                          pending_tasks=pending_tasks,
                          verification_docs=verification_docs,
                          my_recent_posts=my_recent_posts,  # 🔥 ارسال به تمپلیت
                          document_status=document_status)



from models.order import Order, OrderStatus


# routes/users/order_routes.py
from flask import flash, redirect, url_for, request, render_template
from flask_login import login_required, current_user
from models import db
from models.user import User, Role
from models.order import Order, OrderStatus
from . import users_bp
import requests

# Import fallback utility
from utils.fallback import get_data_with_fallback


@users_bp.route('/place_order', methods=['GET', 'POST'])
@login_required
def place_order():
    """
    ثبت سفارش با اعتبارسنجی کامل و امن
    """
    if request.method == 'POST':
        try:
            # دریافت و اعتبارسنجی ورودی
            product = request.form.get('product', '').strip()
            quantity_str = request.form.get('quantity', '').strip()
            price_str = request.form.get('price', '').strip()
            origin_port = request.form.get('origin_port', '').strip()
            destination_port = request.form.get('destination_port', '').strip()
            seller_id_str = request.form.get('seller_id', '').strip()
            notes = request.form.get('notes', '').strip()

            # ✅ اعتبارسنجی فیلدها
            if not product:
                flash(_("❌ Please enter the product name."))
                return redirect(url_for('users.place_order'))

            if not origin_port or not destination_port:
                flash(_("❌ Please select origin and destination."))
                return redirect(url_for('users.place_order'))

            # ✅ اعتبارسنجی کمیت و قیمت
            try:
                quantity = float(quantity_str)
                price = float(price_str)
                if quantity <= 0 or price <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                flash(_("❌ Invalid quantity or price."))
                return redirect(url_for('users.place_order'))

            # ✅ اعتبارسنجی فروشنده
            if not seller_id_str.isdigit():
                flash(_("❌ The seller is invalid."))
                return redirect(url_for('users.place_order'))

            seller_id = int(seller_id_str)
            seller = db.session.get(User, seller_id)
            if not seller or seller.role != Role.PRODUCER:  # ✅ باید اینطور اصلاح شود
                flash(_("❌ The desired seller was not found or is not a producer."))
                return redirect(url_for('users.place_order'))

            if not seller:
                flash(_("❌ The desired seller was not found."))
                return redirect(url_for('users.place_order'))

            if seller.role != Role.PRODUCER:
                flash(_("❌ The selected user is not a producer."))
                return redirect(url_for('users.place_order'))

            # ✅ تعیین بروکر (فقط اگر کاربر ویژه باشد)
            broker_id = current_user.id if current_user.is_premium else None

            # ✅ ایجاد سفارش
            order = Order(
                product=product,
                quantity_tons=quantity,
                price_per_ton=price,
                origin_port=origin_port,
                destination_port=destination_port,
                notes=notes,
                buyer_id=current_user.id,
                seller_id=seller.id,
                broker_id=broker_id,
                status=OrderStatus.PENDING
            )
            order.calculate_total()

            # ✅ ارسال اعلان به فروشنده
            from models.notification import Notification
            notification = Notification(
                user_id=seller.id,
                # message=f" You received a new order from {current_user.username} . (#{order.id})"

                title='New Order Received',
                message=f"You received a new order from {current_user.username} for {quantity} tons of {product.title()}. (#{order.id})",
                notification_type='new_order',
                actor_id=current_user.id,
                related_id=order.id,
                related_type='order'
            )

            # ✅ افزودن و ذخیره در یک تراکنش واحد
            db.session.add(order)
            db.session.add(notification)
            db.session.commit()


            # Send real-time notification via Celery
            try:
                from tasks.social_notifications import send_notification_task
                send_notification_task.delay(seller.id, {
                    'title': 'New Order Received',
                    'message': f"You received a new order from {current_user.username}!",
                    'type': 'new_order',
                    'actor_id': current_user.id,
                    'related_id': order.id,
                    'related_type': 'order'
                })
            except Exception as e:
                print(f"Celery not available: {e}")



            flash(_("✅ Order successfully placed."))
            return redirect(url_for('users.my_orders'))

        except Exception as e:
            db.session.rollback()  # ⚠️ بازگردانی تراکنش در صورت خطا
            print(f"❌ Error creating order: {e}")
            flash(_("❌ An error occurred while placing your order. Please try again."))
            return redirect(url_for('users.place_order'))

    # GET: نمایش فرم — فقط PRODUCERها
    sellers = User.query.filter_by(role=Role.PRODUCER, is_active=True).all()
    return render_template('users/place_order.html', sellers=sellers)


# -------------------------------
# نمایش سفارش‌های کاربر
# -------------------------------
@users_bp.route('/orders')
@login_required
def my_orders():
    orders = Order.query.filter(
        (Order.buyer_id == current_user.id) |
        (Order.seller_id == current_user.id) |
        (Order.broker_id == current_user.id)
    ).order_by(Order.created_at.desc()).all()
    return render_template('users/orders.html', orders=orders)


# -------------------------------
# نمایش سفارش‌های PRODUCER
# -------------------------------
@users_bp.route('/seller/orders')
@login_required
def seller_orders():
    # Check if user has permission to manage orders instead of just checking role
    if not has_permission(current_user, Permission.ORDER_EDIT):
        flash(_("❌ You do not have permission to manage orders."))
        return redirect(url_for('users.profile'))

    orders = Order.query.filter_by(seller_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('users/producer_orders.html', orders=orders)


@users_bp.route('/order/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    """Cancel a pending order (buyer only)"""
    order = Order.query.get_or_404(order_id)

    # Only buyer or admin can cancel
    if order.buyer_id != current_user.id and current_user.role != Role.ADMIN:
        flash(_("❌ You can only cancel your own orders."))
        return redirect(url_for('users.my_orders'))

    if order.status == OrderStatus.PENDING:
        order.status = OrderStatus.CANCELLED

        # Notify seller
        from models.notification import Notification
        notification = Notification(
            user_id=order.seller_id,
            title='Order Cancelled',
            message=f"Order (#{order.id}) for {order.quantity_tons} tons of {order.product.title()} was cancelled by the buyer.",
            notification_type='order_cancelled_by_buyer',
            actor_id=current_user.id,
            related_id=order.id,
            related_type='order'
        )
        db.session.add(notification)

        try:
            from tasks.social_notifications import send_notification_task
            send_notification_task.delay(order.seller_id, {
                'title': 'Order Cancelled',
                'message': f"Order (#{order.id}) was cancelled by the buyer.",
                'type': 'order_cancelled_by_buyer',
                'actor_id': current_user.id,
                'related_id': order.id,
                'related_type': 'order'
            })
        except Exception as e:
            print(f"Celery not available: {e}")

        db.session.commit()
        flash(_("🗑️ Order #{order_id} has been cancelled."))
    else:
        flash(_("⚠️ This order cannot be cancelled as it has already been processed."))

    return redirect(url_for('users.my_orders'))


# -------------------------------
# تأیید سفارش توسط فروشنده
# -------------------------------
@users_bp.route('/order/<int:order_id>/confirm', methods=['POST'])
@login_required
def confirm_order(order_id):
    order = Order.query.get_or_404(order_id)

    if current_user.role != Role.PRODUCER or order.seller_id != current_user.id:
        flash(_("❌ Unauthorized access."))
        return redirect(url_for('users.seller_orders'))

    if order.status == OrderStatus.PENDING:
        order.status = OrderStatus.CONFIRMED
        # confirmed_at will be set automatically by the model's default

        # ارسال اعلان به خریدار
        from models.notification import Notification
        notification = Notification(
            user_id=order.buyer_id,
            # message=f"Your order (#{order.id}) was confirmed by {current_user.username} ."
            title='Order Confirmed',
            message=f"Your order (#{order.id}) for {order.quantity_tons} tons of {order.product.title()} was confirmed by {current_user.username}.",
            notification_type='order_confirmed',
            actor_id=current_user.id,
            related_id=order.id,
            related_type='order'
        )
        db.session.add(notification)

        # Send real-time notification
        try:
            from tasks.social_notifications import send_notification_task
            send_notification_task.delay(order.buyer_id, {
                'title': 'Order Confirmed',
                'message': f"Your order (#{order.id}) was confirmed!",
                'type': 'order_confirmed',
                'actor_id': current_user.id,
                'related_id': order.id,
                'related_type': 'order'
            })
        except Exception as e:
            print(f"Celery not available: {e}")

        db.session.commit()

        flash(_("✅ The order was confirmed and the notification was sent"))
    else:
        flash(_("⚠️This order has already been approved or rejected."))

    return redirect(url_for('users.seller_orders'))


# -------------------------------
# رد سفارش توسط فروشنده
# -------------------------------
@users_bp.route('/order/<int:order_id>/reject', methods=['POST'])
@login_required
def reject_order(order_id):
    order = Order.query.get_or_404(order_id)

    if current_user.role != Role.PRODUCER or order.seller_id != current_user.id:
        flash(_("❌ Unauthorized access."))
        return redirect(url_for('users.seller_orders'))

    if order.status == OrderStatus.PENDING:
        order.status = OrderStatus.CANCELLED



        # ارسال اعلان به خریدار
        from models.notification import Notification
        notification = Notification(
            user_id=order.buyer_id,
            title='Order Rejected',
            message=f"Your order (#{order.id}) for {order.quantity_tons} tons of {order.product.title()} was rejected by {current_user.username}.",
            notification_type='order_cancelled',
            actor_id=current_user.id,
            related_id=order.id,
            related_type='order'
        )
        db.session.add(notification)

        # Send real-time notification
        try:
            from tasks.social_notifications import send_notification_task
            send_notification_task.delay(order.buyer_id, {
                'title': 'Order Rejected',
                'message': f"Your order (#{order.id}) was rejected.",
                'type': 'order_cancelled',
                'actor_id': current_user.id,
                'related_id': order.id,
                'related_type': 'order'
            })
        except Exception as e:
            print(f"Celery not available: {e}")



        db.session.commit()
        flash(_("🗑️ Order #{order_id} rejected."))
    else:
        flash(_("⚠️ This order has already changed status."))

    return redirect(url_for('users.seller_orders'))


# -------------------------------
# Update Order Status (In Transit / Delivered)
# -------------------------------
@users_bp.route('/order/<int:order_id>/update-status', methods=['POST'])
@login_required
def update_order_status(order_id):
    """Update order status to in_transit or delivered"""
    order = Order.query.get_or_404(order_id)

    # Only seller can update to in_transit, only admin or seller can mark as delivered
    if current_user.role not in [Role.PRODUCER, Role.ADMIN]:
        flash(_("❌ Unauthorized access."))
        return redirect(url_for('users.my_orders'))

    if order.seller_id != current_user.id and current_user.role != Role.ADMIN:
        flash(_("❌ You can only update your own orders."))
        return redirect(url_for('users.seller_orders'))

    new_status = request.form.get('status')

    if new_status == 'in_transit' and order.status == OrderStatus.CONFIRMED:
        order.status = OrderStatus.IN_TRANSIT
        order.shipped_at = datetime.now(tehran_tz)

        # Notify buyer
        from models.notification import Notification
        notification = Notification(
            user_id=order.buyer_id,
            title='Order Shipped',
            message=f"Your order (#{order.id}) has been shipped and is in transit.",
            notification_type='order_shipped',
            actor_id=current_user.id,
            related_id=order.id,
            related_type='order'
        )
        db.session.add(notification)

        try:
            from tasks.social_notifications import send_notification_task
            send_notification_task.delay(order.buyer_id, {
                'title': 'Order Shipped',
                'message': f"Your order (#{order.id}) is on its way!",
                'type': 'order_shipped',
                'actor_id': current_user.id,
                'related_id': order.id,
                'related_type': 'order'
            })
        except Exception as e:
            print(f"Celery not available: {e}")

        flash(_("✅ Order status updated to In Transit"))

    elif new_status == 'delivered' and order.status == OrderStatus.IN_TRANSIT:
        order.status = OrderStatus.DELIVERED
        order.delivered_at = datetime.now(tehran_tz)

        # Notify buyer
        from models.notification import Notification
        notification = Notification(
            user_id=order.buyer_id,
            title='Order Delivered',
            message=f"Your order (#{order.id}) has been delivered successfully.",
            notification_type='order_delivered',
            actor_id=current_user.id,
            related_id=order.id,
            related_type='order'
        )
        db.session.add(notification)

        try:
            from tasks.social_notifications import send_notification_task
            send_notification_task.delay(order.buyer_id, {
                'title': 'Order Delivered',
                'message': f"Your order (#{order.id}) has been delivered!",
                'type': 'order_delivered',
                'actor_id': current_user.id,
                'related_id': order.id,
                'related_type': 'order'
            })
        except Exception as e:
            print(f"Celery not available: {e}")

        flash(_("✅ Order marked as Delivered"))
    else:
        flash(_("⚠️ Cannot update order status at this stage."))

    db.session.commit()
    return redirect(url_for('users.seller_orders') if current_user.role == Role.PRODUCER else url_for('users.my_orders'))



@users_bp.route('/notifications')
@login_required
def notifications():
    # خواندن همه اعلان‌ها
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()

    # علامت‌گذاری به عنوان خوانده شده
    for n in notifs:
        if not n.is_read:
            n.is_read = True
    db.session.commit()

    return render_template('users/notifications.html', notifications=notifs, unread_count=0)


@users_bp.route('/api/unread-notifications')
# @limiter.exempt  # ✅ این مسیر دیگر هرگز محدودیت زمانی نخواهد داشت
@limiter.limit("1000 per minute")
@login_required
def get_unread_notifications():
    """API endpoint to get unread notification count"""
    from models.notification import Notification
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return {'unread_count': unread_count}


@users_bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    """Mark all notifications as read"""
    from models.notification import Notification
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    flash("✅ All notifications marked as read")
    return redirect(url_for('users.notifications'))


@users_bp.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    # ✅ فقط کاربران ویژه می‌تونن به لیست چت دسترسی داشته باشن و با کاربران دیگر چت کنن
    # اما کاربران غیر ویژه می‌تونن پیام‌های ادمین رو ببینن
    receiver_id = request.args.get('receiver_id', type=int)
    receiver = db.session.get(User, receiver_id) if receiver_id else None
    
    # بررسی اینکه آیا کاربر جاری غیر ویژه است و سعی دارد به چت دسترسی پیدا کند
    if not current_user.is_premium:
        # اگر کاربر غیر ویژه است، فقط می‌تواند پیام‌های ادمین را ببیند
        # نمی‌تواند به صورت فعال چت جدیدی شروع کند
        if request.method == 'POST':
            flash(_("❌ Limited access: Only special users can send messages."), "error")
            return redirect(url_for('users.profile'))
        
        # برای کاربران غیر ویژه، فقط نمایش پیام‌های ادمین مجاز است
        # لیست کاربران را خالی نگه می‌داریم
        users = []
        
        # اگر receiver مشخص شده، باید ادمین باشد
        if receiver and receiver.role != Role.ADMIN:
            flash(_("❌ Access denied: Non-special users can only view messages from admin."), "error")
            return redirect(url_for('users.profile'))
            
    else:
        # کاربران ویژه می‌تونن با همه کاربران ویژه چت کنن
        users = User.query.filter(
            User.id != current_user.id,
            User.is_premium == True
        ).all()

        # ✅ اگر گیرنده وجود نداشته باشه یا ویژه نباشه (برای کاربران عادی)
        if receiver and not receiver.is_premium:
            flash(_("❌ This user is not special and you cannot chat with him/her."), "error")
            receiver = None

    # ارسال پیام (فقط برای کاربران ویژه)
    if request.method == 'POST' and receiver and current_user.is_premium:
        content = request.form['content'].strip()
        if content:
            # ایجاد پیام
            msg = Message(
                sender_id=current_user.id,
                receiver_id=receiver.id,
                content=content
            )
            db.session.add(msg)
            db.session.commit()

            # ✅ ارسال اعلان به گیرنده
            notification = Notification(
                user_id=receiver.id,
                message=f"📩 You received a new message from {current_user.username} ."
            )
            db.session.add(notification)
            db.session.commit()

            flash(_("✉️ Message sent."))
        return redirect(url_for('users.chat', receiver_id=receiver.id))

    # دریافت پیام‌ها
    messages = []
    if receiver:
        messages = Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.receiver_id == receiver.id)) |
            ((Message.sender_id == receiver.id) & (Message.receiver_id == current_user.id))
        ).order_by(Message.created_at.asc()).all()

        # علامت‌گذاری پیام‌های دریافتی به عنوان خوانده شده
        for m in messages:
            if m.receiver_id == current_user.id and not m.is_read:
                m.is_read = True
        db.session.commit()

    return render_template('users/chat.html', users=users, receiver=receiver, messages=messages)


# ✅ مسیر جدید برای پشتیبانی - کاربران غیر ویژه می‌تونن پیام‌های ادمین رو اینجا ببینن و ارسال کنن
@users_bp.route('/support', methods=['GET', 'POST'])
@login_required
def support():
    """بخش پشتیبانی برای کاربران - مشاهده و ارسال پیام به ادمین"""
    # پیدا کردن کاربر ادمین
    admin_user = User.query.filter_by(role=Role.ADMIN, is_active=True).first()
    
    if not admin_user:
        flash(_("⚠️ No admin found to contact."), "warning")
        return redirect(url_for('users.profile'))
    
    # اگر درخواست POST است، کاربر می‌خواهد پیام ارسال کند
    if request.method == 'POST':
        content = request.form.get('message', '').strip()
        
        if not content:
            flash(_("❌ Please enter a message."), "error")
            return redirect(url_for('users.support'))
        
        # ایجاد پیام جدید از کاربر به ادمین
        message = Message(
            sender_id=current_user.id,
            receiver_id=admin_user.id,
            content=content
        )
        db.session.add(message)
        
        # ایجاد اعلان برای ادمین
        from models.notification import Notification
        notification = Notification(
            user_id=admin_user.id,
            message=f"📩 New support message from {current_user.username}"
        )
        db.session.add(notification)
        db.session.commit()
        
        flash(_("✅ Your message was sent to support."), "success")
        return redirect(url_for('users.support'))
    
    # دریافت پیام‌های بین کاربر جاری و ادمین
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == admin_user.id)) |
        ((Message.sender_id == admin_user.id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at.asc()).all()

    # علامت‌گذاری پیام‌های دریافتی به عنوان خوانده شده
    for m in messages:
        if m.receiver_id == current_user.id and not m.is_read:
            m.is_read = True
    db.session.commit()
    
    return render_template('users/support.html', admin_user=admin_user, messages=messages)







from flask import g

@users_bp.app_context_processor
def inject_support_user():
    if current_user.is_authenticated:
        # مثلاً PRODUCER اول یا کاربر با username='support'
        support_user = User.query.filter_by(username='support', is_active=True).first()
        if not support_user:
            support_user = User.query.filter_by(role=Role.PRODUCER, is_active=True).first()
        return {'support_user': support_user}
    return {'support_user': None}


####################################
import requests
from flask import request
import json
from models import DataProvider
from functools import wraps

provider = DataProvider()
country_codes = provider.COUNTRY_CODES



@users_bp.route('/vessel_finder', methods=['GET', 'POST'])
@login_required
def vessel_finder():
    if not current_user.is_premium:
        flash(_("❌ Access is only allowed for special users."), "error")
        return redirect(url_for('users.profile'))

    # فقط در صورت POST و دریافت IMO
    if request.method == 'POST':
        imo = request.form.get('imo', '').strip()

        # اعتبارسنجی
        if not imo or not imo.isdigit() or len(imo) != 7:
            flash(_("❌ Please enter a valid 7-digit ID (IMO)."), "error")
            return render_template('users/vessel_finder.html')

        url = f"https://api.searoutes.com/vessel/v2/{imo}/position"
        headers = {
            "X-API-Key": "zXlhor8hMV9fXyeZ3nero4aPpYAw39eU37KYP9ne",
            "Content-Type": "application/json"
        }

        def fetch_vessel_data():
            """Helper function to fetch data from API"""
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()

        # Use fallback mechanism
        data = get_data_with_fallback(url=url, fallback_query_func=None, timeout=10, headers=headers)

        # If network failed and no fallback data returned, show error
        if not data:
            flash(_("⚠️ Network unavailable. Showing demo data."), "warning")
            # Return demo/static data when offline
            return render_template(
                'users/vessel_finder.html',
                latitude=35.6892,  # Example: Tehran
                longitude=51.3890,
                imo=imo,
                mmsi="000000000",
                name="Demo Vessel (Offline Mode)",
                destination="Unknown",
                speed="0.0",
                date_arrival="N/A"
            )

        try:
            if not data:
                flash(_("❌ No data found for this ship."), "error")
                return render_template('users/vessel_finder.html')

            pos = data[0]['position']
            info = data[0]['info']

            return render_template(
                'users/vessel_finder.html',
                latitude=pos['geometry']['coordinates'][1],
                longitude=pos['geometry']['coordinates'][0],
                imo=info['imo'],
                mmsi=info['mmsi'],
                name=info['name'],
                destination=pos['properties'].get('destination', 'Uncertain'),
                speed=pos['properties'].get('speed', 'Uncertain'),
                date_arrival=pos['properties'].get('eta', 'Uncertain')
            )

        except requests.exceptions.Timeout:
            flash(_("❌ The request to the server was scheduled. Please try again."), "error")
        except requests.exceptions.RequestException as e:
            flash(_("❌ An error occurred with the ship tracking service."), "error")
        except (KeyError, IndexError) as e:
            flash(_("❌ The received data is invalid."), "error")

    # GET یا خطا: نمایش فرم
    return render_template('users/vessel_finder.html')
######################################TEST

# نمایش نقشه
@users_bp.route('/map')
@login_required
def show_map():
    if not current_user.is_premium:
        flash(_("❌ Only special users can access the map."))
        return redirect(url_for('users.profile'))
    
    # Fetch ports with fallback to local DB
    def get_local_ports():
        ports = Port.query.all()  # Limit for performance
        return [port.to_dict() for port in ports]
    
    # Try to fetch from external source (if you have one), otherwise use local DB
    # For now, we directly use local DB as primary source since ports are static
    ports_data = get_local_ports()
    
    # Ensure data structure is consistent
    if not ports_data:
        flash(_("⚠️ No port data available."), "warning")
        ports_data = []
    
    return render_template('users/map.html', ports=ports_data)


##############################################################test2

# routes/users/routes.py
from flask import jsonify


@users_bp.route('/api/ports', methods=['GET'])
@login_required
def get_ports():
    # فقط کاربران ویژه می‌تونن ببینن
    if not current_user.is_premium:
        return jsonify({'error': 'Restricted access: Special users only'}), 403

    # Fetch ports from local DB (always available, no external dependency)
    try:
        ports = Port.query.all()  # Limit for API performance
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'country': p.country,
            'location': [p.latitude, p.longitude]
        } for p in ports])
    except Exception as e:
        # Fallback to empty list if DB error
        return jsonify([]), 200


@users_bp.route('/add_port', methods=['POST'])
@login_required
def add_port():
    if current_user.role != Role.PRODUCER:
        return jsonify({'error': 'Access denied'}), 403

    data = request.get_json()
    port = Port(
        name=data['name'],
        country=data['country'],
        latitude=data['latitude'],
        longitude=data['longitude']
    )
    db.session.add(port)
    db.session.commit()
    return jsonify({'message': 'Port added.', 'port': port.to_dict()})


@users_bp.route('/update_port/<port_id>', methods=['PUT'])
@login_required
def update_port(port_id):
    if current_user.role != Role.PRODUCER:
        return jsonify({'error': 'Access denied'}), 403

    # ✅ چک کردن اینکه port_id عددی باشه
    if not port_id.isdigit():
        return jsonify({'error': 'The port ID must be a positive number.'}), 400

    port_id = int(port_id)

    port = Port.query.get_or_404(port_id)
    data = request.get_json()

    port.name = data['name']
    port.country = data['country']
    port.latitude = data['latitude']
    port.longitude = data['longitude']

    db.session.commit()
    return jsonify({'message': 'Port successfully updated.'})


@users_bp.route('/delete_port/<port_id>', methods=['DELETE'])
@login_required
def delete_port(port_id):
    if current_user.role != Role.PRODUCER:
        return jsonify({'error': 'Access denied'}), 403
    if not port_id.isdigit():
        return jsonify({'error': 'The port ID must be a positive number.'}), 400

    port_id = int(port_id)
    port = Port.query.get_or_404(port_id)
    db.session.delete(port)
    db.session.commit()
    return jsonify({'message': 'The port was removed.'})

# @users_bp.route('/test')
# def test():
#     return "✅ مسیر /users/test کار می‌کنه!"

####################################################################

import os
from flask import request, flash, redirect, url_for, render_template
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db
from models.premium_request import PremiumRequest

# مسیر اصلی ارتقاء
@users_bp.route('/upgrade_to_premium')
@login_required
def upgrade_to_premium():
    # آخرین درخواست کاربر
    req = PremiumRequest.query.filter_by(user_id=current_user.id).order_by(PremiumRequest.submitted_at.desc()).first()
    # دریافت تمام درخواست‌ها برای نمایش تاریخچه
    requests = PremiumRequest.query.filter_by(user_id=current_user.id).order_by(
        PremiumRequest.submitted_at.desc()).all()

    if req:
        if req.status == 'approved':
            flash(_("✅ You have already become a special user."))
            return redirect(url_for('users.profile'))
        elif req.status == 'pending':
            # فقط اگر مدارک آپلود شده باشند، کاربر در حال بررسی است
            if req.passport_file and req.license_file and req.payment_receipt:
                flash(_("⚠️ Your request is under review by admin."))
                return redirect(url_for('users.view_my_documents'))
            # اگر مدارک آپلود نشده، اجازه ادامه فرآیند را بده

    # ارسال `req` به تمپلیت
    return render_template('users/upgrade_premium.html', req=req, requests=requests )

# شروع فرآیند (ایجاد درخواست جدید)
@users_bp.route('/start_upgrade', methods=['POST'])
@login_required
def start_upgrade():
    # حذف احراز موبایل - مستقیماً به آپلود مدارک می‌رویم
    
    # بررسی اینکه آیا کاربر قبلاً درخواست تأیید شده دارد
    existing_approved = PremiumRequest.query.filter_by(
        user_id=current_user.id, 
        status='approved'
    ).first()
    
    if existing_approved:
        flash(_("You are already a Premium member. Your documents have been verified."), "info")
        return redirect(url_for('users.view_my_documents'))
    
    # بررسی درخواست در حال انتظار
    existing_pending = PremiumRequest.query.filter_by(
        user_id=current_user.id, 
        status='pending'
    ).first()
    
    if existing_pending:
        # اگر مدارک آپلود شده باشند، کاربر در حال بررسی است
        if existing_pending.passport_file and existing_pending.license_file and existing_pending.payment_receipt:
            flash(_("You already have a pending verification request."), "info")
            return redirect(url_for('users.upgrade_to_premium'))
        # اگر مدارک آپلود نشده، اجازه ادامه فرآیند را بده
    
    # ایجاد درخواست جدید فقط اگر هیچ درخواست فعالی وجود ندارد
    req = PremiumRequest(user_id=current_user.id, requested_phone=current_user.phone or '')
    db.session.add(req)
    db.session.commit()

    flash(_("The upgrade process has started. Please upload your documents."))
    return redirect(url_for('users.upload_documents'))

# آپلود مدارک برای Premium
@users_bp.route('/upload_documents', methods=['GET', 'POST'])
@login_required
def upload_documents():
    req = PremiumRequest.query.filter_by(user_id=current_user.id).order_by(PremiumRequest.submitted_at.desc()).first()

    # اگر درخواستی وجود ندارد، کاربر باید ابتدا فرآیند را شروع کند
    if not req:
        flash(_("Please start the premium verification process first."), "error")
        return redirect(url_for('users.upgrade_to_premium'))

    # اگر کاربر قبلاً پریمیوم شده (تأیید نهایی)، نمی‌تواند مدارک را تغییر دهد
    if req.status == 'approved':
        flash(_("Your documents have been verified. You cannot modify them."), "info")
        return redirect(url_for('users.view_my_documents'))

    # اگر مدارک قبلاً آپلود شده و در حال بررسی است
    if req.passport_file and req.license_file:
        if req.status == 'pending':
            flash(_("Your documents are under review by admin."), "info")
            return redirect(url_for('users.view_my_documents'))
        else:
            # هنوز تأیید نشده، اجازه آپلود مجدد
            pass

    unique_f = f"{current_user.id}_{current_user.username}"
    # upload_folder = f'static/uploads/documents/user_{unique_f}/'
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'documents', f'user_{unique_f}')

    os.makedirs(upload_folder, exist_ok=True)

    if request.method == 'POST':
        files_uploaded = False

        # پردازش پاسپورت
        passport_file = request.files.get('passport_file')


        if passport_file and passport_file.filename != '':
            is_valid, error_msg = validate_file(passport_file)
            if not is_valid:
                flash(
                    _("Error: %(error)s") % {"error": error_msg},
                    "error"
                )
                return redirect(url_for('users.upload_documents'))

            filename = secure_filename(f"passport.+{passport_file.filename.rsplit('.', 1)[1].lower()}")
            # filename = secure_filename(f"passport_{current_user.id}_{current_user.username}+")
            passport_file.save(os.path.join(upload_folder, filename))
            req.passport_file = filename
            files_uploaded = True

        # پردازش لایسنس
        license_file = request.files.get('license_file')
        if license_file and license_file.filename != '':
            is_valid, error_msg = validate_file(license_file)
            if not is_valid:
                flash(
                    _("Error: %(error)s") % {"error": error_msg},
                    "error"
                )
                return redirect(url_for('users.upload_documents'))

            filename = secure_filename(f"license.+{license_file.filename.rsplit('.', 1)[1].lower()}")
            # filename = secure_filename(f"license_{req.user.id}_{req.user.username}")
            license_file.save(os.path.join(upload_folder, filename))
            req.license_file = filename
            files_uploaded = True

        if files_uploaded:
            req.docs_verified = True
            db.session.commit()

            flash(_("✅ Documents uploaded successfully."), "success")
            return redirect(url_for('users.make_payment'))
        else:
            flash(_("❌ No files were found to upload. Please select files and try again."), "error")

    return render_template('users/upload_documents.html', req=req)


# مشاهده مدارک توسط کاربر (فقط خواندنی بعد از تأیید)
@users_bp.route('/my_documents')
@login_required
def view_my_documents():
    req = PremiumRequest.query.filter_by(user_id=current_user.id).order_by(PremiumRequest.submitted_at.desc()).first()
    
    if not req:
        flash(_("No verification request found."), "error")
        return redirect(url_for('users.upgrade_to_premium'))
    
    return render_template('users/my_documents.html', req=req)

# پرداخت و آپلود رسید
@users_bp.route('/make_payment', methods=['GET', 'POST'])
@login_required
def make_payment():
    req = PremiumRequest.query.filter_by(user_id=current_user.id).order_by(PremiumRequest.submitted_at.desc()).first()

    # اگر درخواستی وجود ندارد یا مدارک آپلود نشده، کاربر باید ابتدا مدارک را آپلود کند
    if not req or not (req.passport_file and req.license_file):
        flash(_("Please upload your documents first."), "error")
        return redirect(url_for('users.upload_documents'))

    # اگر رسید پرداخت قبلاً آپلود شده و تأیید شده، کاربر نباید بتواند دوباره آپلود کند
    if req.payment_verified and req.payment_receipt:
        return redirect(url_for('users.payment_confirmation',now=datetime.now()))


    if request.method == 'POST':
        if 'receipt' in request.files:
            file = request.files['receipt']
            if file.filename != '':
                unique_f = f"{current_user.id}_{current_user.username}"
                # upload_folder = f'static/uploads/documents/user_{unique_f}/'
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'documents',
                                             f'user_{unique_f}')

                filename = secure_filename(f"receipt.+{file.filename.rsplit('.', 1)[1].lower()}")
                # filename = secure_filename(f"receipt_{current_user.id}_{current_user.username}")
                file.save(os.path.join(upload_folder, filename))
                req.payment_receipt = filename

                req.status = 'pending'
                req.payment_verified = True
                db.session.commit()
                flash(_("Payment receipt received. Reviewing..."))
                # ارسال اعلان به ادمین
                notify_admin_of_new_request(req)
                return redirect(url_for('users.payment_confirmation',now=datetime.now()))

    return render_template('users/make_payment.html', req=req)

# تأیید نهایی
@users_bp.route('/payment_confirmation')
@login_required
def payment_confirmation():
    return render_template('users/payment_confirmation.html',now=datetime.now())

# --- تابع کمکی: اعلان به ادمین ---
def notify_admin_of_new_request(req):
    """Send email notification to admins when a new premium request is submitted."""
    from flask_mail import Message
    from extensions import mail
    from flask import current_app
    
    try:
        admins = User.query.filter_by(role=Role.ADMIN, is_active=True).all()
        emails = [a.email for a in admins if a.email]

        if emails:
            msg = Message(
                subject="🔔 New request for promotion to special user",
                recipients=emails,
                body=f"User {req.user.username} has submitted a new request for premium access."
            )
            mail.send(msg)
            current_app.logger.info(f"Notification sent to {len(emails)} admin(s) for user {req.user.username}")
    except Exception as e:
        current_app.logger.error(f"Error sending admin notification: {e}")
        # Don't raise exception - this is a non-critical operation


# routes/api.py
from flask import Blueprint, request, jsonify, current_app
from models import User


api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/check-availability', methods=['GET'])
def check_availability():
    """Real-time availability check - ALWAYS returns JSON"""

    # دریافت پارامترها با دیباگ لاگ
    field = request.args.get('field')
    value = request.args.get('value', '').strip()

    current_app.logger.debug(f'Check availability: field={field}, value={value}')

    # اعتبارسنجی فیلد
    valid_fields = ['username', 'email', 'phone']
    if not field or field not in valid_fields:
        current_app.logger.warning(f'Invalid field parameter: {field}')
        return jsonify({
            'error': f'Invalid field. Must be one of: {valid_fields}',
            'available': True  # Fail-safe: اجازه ادامه می‌دهیم
        }), 400

    if not value or len(value) < 3:
        return jsonify({'available': True, 'message': 'Too short to check'}), 200

    try:
        # نرمال‌سازی مقدار
        if field == 'phone':
            value = ''.join(filter(str.isdigit, value)).lstrip('0')
            if not value:
                return jsonify({'available': True}), 200

        if field in ['email', 'username']:
            value = value.lower()

        # کوئری دیتابیس
        existing = User.query.filter(
            getattr(User, field) == value
        ).first()

        return jsonify({
            'available': existing is None,
            'message': 'Available' if existing is None else f'{field} already taken'
        }), 200

    except Exception as e:
        current_app.logger.error(f'Availability check error: {str(e)}', exc_info=True)
        # در صورت خطا، اجازه می‌دهیم فرم ارسال شود و سرور در submit نهایی چک کند
        return jsonify({
            'available': True,
            'warning': 'Could not verify, will check on submit'
        }), 200


@users_bp.route('/verify-email/<token>', endpoint='verify_email_route')
def verify_email(token):
    """بررسی توکن و فعال‌سازی حساب کاربری"""
    # 1. اعتبارسنجی توکن (چک کردن هش و تاریخ انقضا)
    user, error_msg = verify_email_token(token)

    if not user:
        flash(
            _("Error: %(error)s") % {"error": error_msg},
            "error"
        )
        return redirect(url_for('users.resend_verification'))

    # 2. اگر قبلاً تایید شده
    if user.is_email_verified:
        flash(_("✅ Your email is already verified. You can login."), "success")
        return redirect(url_for('users.login'))

    # 3. تایید کاربر
    user.is_email_verified = True
    # 4. ذخیره تغییرات در دیتابیس
    db.session.commit()

    # 4. علامت‌گذاری توکن به عنوان استفاده شده
    import hashlib
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    token_record = EmailVerificationToken.query.filter_by(token=token_hash).first()
    if token_record:
        token_record.mark_as_used()
        db.session.commit()

    flash(_("🎉 Email verified successfully! Welcome to Metisma."), "success")
    return redirect(url_for('users.login'))


@users_bp.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    """ارسال مجدد ایمیل تایید"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()

        if not user:
            flash(_("No account found with this email."), "error")
            return redirect(url_for('users.resend_verification'))

        if user.is_email_verified:
            flash(_("✅ Your email is already verified."), "success")
            return redirect(url_for('users.login'))

        # تولید توکن جدید و ارسال
        raw_token = generate_verification_token(user)

        # ✅ ذخیره توکن در دیتابیس (EmailVerificationToken)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        existing_token = EmailVerificationToken.query.filter_by(token=token_hash).first()
        if not existing_token:
            new_token_record = EmailVerificationToken(
                user_id=user.id,
                email=user.email,
                expiration_hours=48
            )
            # هش کردن توکن قبل از ذخیره
            new_token_record.token = token_hash
            db.session.add(new_token_record)
            db.session.commit()


        success, error = send_verification_email(user, raw_token)

        if success:
            flash(_("📧 New verification email sent! Please check your inbox."), "success")
        else:
            flash(
                _("Error: ⚠️ Failed to send email: %(error)s") % {"error": error},
                "error"
            )

        return redirect(url_for('users.login'))

    return render_template('email/resend_form.html')  # یک تمپلیت ساده برای گرفتن ایمیل