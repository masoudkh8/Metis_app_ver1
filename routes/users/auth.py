import random
import logging
import json
import pyotp
import pytz
import secrets
import hashlib
from datetime import datetime, timedelta
from flask import render_template, flash, redirect, url_for, request, current_app, session
from flask_login import login_required, current_user, login_user, logout_user
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask_mail import Message
from models import db, User, PasswordResetToken, EmailVerificationToken, LoginSession, ActivityLog
from models.premium_request import PremiumRequest
from . import users_bp
from extensions import mail
from kavenegar import KavenegarAPI

tehran_tz = pytz.timezone('Asia/Tehran')
logger = logging.getLogger(__name__)


def get_serializer():
    """Create a URL-safe timed serializer for email tokens."""
    return URLSafeTimedSerializer(current_app.secret_key)


def send_sms(phone, message):
    """Send SMS via Kavenegar API with proper error handling and logging."""
    if not phone:
        logger.error("The mobile number is empty.")
        return False

    # Clean phone number (remove leading zero)
    cleaned_phone = phone
    if cleaned_phone.startswith("0"):
        cleaned_phone = cleaned_phone[1:]
    
    if not cleaned_phone.isdigit() or len(cleaned_phone) != 10:
        logger.error(f"Invalid number format: {phone}")
        return False

    # Debug mode: just log without sending
    if current_app.config.get('D_STATE'):
        logger.info(f"[TEST] SMS to {phone}: {message}")
        return True

    # Production mode: send actual SMS
    try:
        api_key = current_app.config.get('KAVENEGAR_API_KEY')

        if not api_key:
            logger.error("Kavenegar API key not configured")
            return False
            
        api = KavenegarAPI(api_key)
        params = {'sender': '2000660110', 'receptor': phone, 'message': message}
        response = api.sms_send(params)

        if response.status_code == 200:
            json_resp = response.json()
            if json_resp["return"]["status"] == 200:
                logger.info(f"SMS to {phone} sent successfully.")
                return True
            else:
                logger.error(f"Kavenegar error: {json_resp['return']['message']}")
                return False
        else:
            logger.error(f"HTTP error: {response.status_code}, response: {response.text}")
            return False

    except Exception as e:
        logger.error(f"Error sending SMS: {e}")
        return False



@users_bp.route('/verify_phone', methods=['GET', 'POST'])
@login_required
def verify_phone():
    if not current_user.phone or not current_user.phone.strip():
        flash("❌ Please enter your mobile number in your profile first.")
        return redirect(url_for('users.profile'))

    req = PremiumRequest.query.filter_by(user_id=current_user.id).order_by(PremiumRequest.submitted_at.desc()).first()

    # اگر درخواستی وجود ندارد، یک درخواست جدید با وضعیت draft ایجاد کن
    if not req:
        req = PremiumRequest(
            user_id=current_user.id,
            requested_phone=current_user.phone,
            status='draft',  # ✅ تغییر از 'pending' به 'draft'
        )
        db.session.add(req)
        db.session.commit()

    # اگر شماره قبلاً تأیید شده، به مرحله بعد برو
    if req.phone_verified:
        flash("✅ Your mobile number has already been verified.")
        return redirect(url_for('users.show_verify_email_page'))  # ✅ به ایمیل برو، نه payment_confirmation

    if request.method == 'POST':
        if 'resend' in request.form:
            code = str(random.randint(100000, 999999))
            req.phone_verification_code = code
            db.session.commit()
            try:
                send_sms(current_user.phone, f"Verification code: {code}")
                flash("New code sent.")
            except Exception as e:
                current_app.logger.error(f"SMS failed: {e}")
                flash("❌ There was a problem sending the code.")
            return redirect(url_for('users.verify_phone'))

        code = request.form.get('code', '').strip()
        if not code:
            flash("Please enter the code.")
        elif code == req.phone_verification_code:
            req.phone_verified = True
            req.phone_verification_code = None
            db.session.commit()
            flash("✅ Mobile number successfully verified.")
            return redirect(url_for('users.show_verify_email_page'))  # ✅ بعد از تأیید شماره، به ایمیل برو
        else:
            flash("❌ The code is invalid.")

    # ارسال اولیه کد
    if not req.phone_verification_code:
        code = str(random.randint(100000, 999999))
        req.phone_verification_code = code
        db.session.commit()
        try:
            send_sms(current_user.phone, f"Verification code: {code}")
            flash("A verification code has been sent to your number.")
        except Exception as e:
            current_app.logger.error(f"SMS failed: {e}")
            flash("❌ There was a problem sending the code.")

    return render_template('users/verify_phone.html', req=req)







# -------------------------------
# تأیید ایمیل (صفحه نمایش)
# -------------------------------
# -------------------------------
# تأیید ایمیل (صفحه نمایش - برای کاربرانی که ثبت‌نام کرده‌اند)
# -------------------------------
@users_bp.route('/verify_email', endpoint='show_verify_email_page')  # ← تغییر: اضافه کردن endpoint منحصر به فرد
@login_required
def show_verify_email_page():  # ← تغییر: نام تابع جدید
    print('start email process')
    req = PremiumRequest.query.filter_by(user_id=current_user.id).order_by(PremiumRequest.submitted_at.desc()).first()

    # اگر درخواستی وجود ندارد، کاربر باید ابتدا فرآیند را شروع کند
    if not req:
        flash("Please start the premium verification process first.", "error")
        return redirect(url_for('users.upgrade_to_premium'))

    # حذف شرط phone_verified - مستقیماً به تأیید ایمیل می‌رویم
    # if not req or not req.phone_verified:
    #     return redirect(url_for('users.verify_phone'))

    if req.email_verified:
        print('req.email_verified')
        return redirect(url_for('users.upload_documents'))

    if not req.email_verification_token:
        if send_email_verification(current_user):
            flash("Confirmation email sent.")
        else:
            print('....... ❌❌')
            flash("❌ There was an error sending the email.")
            return render_template('users/verify_email.html', req=req)

    return render_template('users/verify_email.html', req=req)

# ارسال ایمیل تأیید
def send_email_verification(user):

    print('send email func')
    serializer = get_serializer()
    token = serializer.dumps(user.email, salt='email-verify-salt')

    req = PremiumRequest.query.filter_by(user_id=user.id).order_by(PremiumRequest.submitted_at.desc()).first()
    print(req)
    if req:
        req.email_verification_token = token
        db.session.commit()

    confirm_url = url_for('users.confirm_email', token=token, _external=True)

    html_body = f"""
    <h2>Hello {user.username}!</h2>
    <p>Verify your email to complete the upgrade process to a premium user:</p>
    <p><a href="{confirm_url}">✅ Email verification</a></p>
    <p>This link will expire after 24 hours.</p>
    """

    msg = Message(
        subject="✅ Email Verification - Upgrade Process",
        recipients=[user.email],
        html=html_body,
        sender=current_app.config.get('MAIL_DEFAULT_SENDER')
    )
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False


# -------------------------------
# تأیید توکن ایمیل
# -------------------------------
@users_bp.route('/confirm_email/<token>')
@login_required
def confirm_email(token):
    print('start confirm_email func')
    s = get_serializer()
    try:
        email = s.loads(token, salt='email-verify-salt', max_age=86400)
    except SignatureExpired:
        flash("❌ The link has expired.")

    #     return redirect(url_for('users.verify_email'))
    # except BadSignature:
    #     flash("❌ The link is invalid.")
    #     return redirect(url_for('users.upgrade_to_premium'))
        return redirect(url_for('users.show_verify_email_page'))
    except BadSignature:
        flash("❌ The link is invalid.")
        return redirect(url_for('users.show_verify_email_page'))

    if email != current_user.email:
        flash("❌ This link is not for you.")
        return redirect(url_for('users.login'))

    req = PremiumRequest.query.filter_by(user_id=current_user.id).order_by(PremiumRequest.submitted_at.desc()).first()
    if not req:
        flash("❌ No request found.")
        return redirect(url_for('users.upgrade_to_premium'))

    if not req.email_verified:
        req.email_verified = True
        req.email_verification_token = None
        # ✅ همچنین is_email_verified را در جدول User نیز true کن
        current_user.is_email_verified = True

        db.session.commit()
        flash("✅ Email has been verified.")

    return redirect(url_for('users.upload_documents'))


# ==================== Password Recovery ====================

@users_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """Password recovery request"""
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash("❌ Please enter your email.", "error")
            return redirect(url_for('users.forgot_password'))
        
        user = User.query.filter_by(email=email).first()
        
        # Even if user doesn't exist, show same message for security
        if user:
            # Create recovery token
            token = PasswordResetToken.create_for_user(
                user=user,
                ip_address=request.remote_addr,
                expiry_hours=1
            )
            
            # Send email
            reset_url = url_for('users.reset_password', token=token, _external=True)
            
            msg = Message(
                subject='Metisma Password Recovery',
                recipients=[user.email],
                html=render_template('email/password_reset.html',
                                   user=user, 
                                   reset_url=reset_url)
            )
            
            try:
                mail.send(msg)
                ActivityLog.log_activity(
                    user_id=user.id,
                    activity_type='password_reset_requested',
                    description='Request Password Recovery',
                    request=request,
                    status='success'
                )
            except Exception as e:
                logger.error(f"Error sending password reset email: {e}")
                ActivityLog.log_activity(
                    user_id=user.id,
                    activity_type='password_reset_requested',
                    description='of Error sending email: {str(e)}',
                    request=request,
                    status='failed'
                )
        
        flash("✅ If your email is registered in the system, a recovery link will be sent to you.", "info")
        return redirect(url_for('users.login'))
    
    return render_template('users/forgot_password.html')


@users_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Password recovery with token"""
    # Hash token for comparison
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    reset_token = PasswordResetToken.query.filter_by(
        token=token_hash,
        used=False
    ).first()
    
    if not reset_token or not reset_token.is_valid():
        flash("❌ The recovery link is invalid or expired.", "error")
        return redirect(url_for('users.forgot_password'))
    
    user = db.session.get(User, reset_token.user_id)
    if not user:
        flash("❌ User not found.", "error")
        return redirect(url_for('users.login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or len(password) < 8:
            flash("❌ Password must be at least 8 characters long.", "error")
            return redirect(url_for('users.reset_password', token=token))
        
        if password != confirm_password:
            flash("❌ Password and repeat do not match.", "error")
            return redirect(url_for('users.reset_password', token=token))
        
        # Check password history
        import json
        if user.password_history:
            try:
                history = json.loads(user.password_history)
                # Don't check if current password is in history (optional)
            except:
                pass
        
        # Set new password
        user.set_password(password)
        
        # Save previous password to history
        if user.password_history:
            try:
                history = json.loads(user.password_history)
            except:
                history = []
        else:
            history = []
        
        history.append(user.password_hash)
        # Keep only last 5 passwords
        user.password_history = json.dumps(history[-5:])
        
        # Reset failed attempts
        user.failed_login_attempts = 0
        user.locked_until = None
        
        # Use token
        reset_token.mark_as_used()
        
        # Log activity
        ActivityLog.log_activity(
            user_id=user.id,
            activity_type='password_reset_completed',
            description='Successful password recovery',
            request=request,
            status='success'
        )
        
        # Logout all sessions except current
        LoginSession.logout_all_sessions(user.id)
        
        flash("✅ Your password has been changed successfully. Please log in.", "success")
        return redirect(url_for('users.login'))
    
    return render_template('users/reset_password.html', token=token, user=user)


# ==================== Two-Factor Authentication (2FA) ====================

import pyotp

@users_bp.route('/enable_2fa', methods=['GET', 'POST'])
@login_required
def enable_2fa():
    """Enable two-factor authentication"""
    if current_user.two_factor_enabled:
        flash("⚠️ Two-factor authentication is already enabled.", "warning")
        return redirect(url_for('users.profile'))
    
    if request.method == 'POST':
        code = request.form.get('code')
        secret = session.get('2fa_secret')
        
        if not secret or not code:
            flash("❌ The information is incomplete.", "error")
            return redirect(url_for('users.enable_2fa'))
        
        totp = pyotp.TOTP(secret)
        
        if totp.verify(code):
            # Save secret and enable
            current_user.two_factor_secret = secret
            current_user.two_factor_enabled = True
            
            # Generate backup codes
            backup_codes = [str(random.randint(100000, 999999)) for _ in range(10)]
            current_user.backup_codes = json.dumps(backup_codes)
            
            db.session.commit()
            
            # Clear session
            session.pop('2fa_secret', None)
            session['backup_codes'] = backup_codes
            
            ActivityLog.log_activity(
                user_id=current_user.id,
                activity_type='2fa_enabled',
                description='Enable two-factor authentication',
                request=request,
                status='success'
            )

            flash("✅ Two-factor authentication enabled. Save backup codes!", "success")
            return redirect(url_for('users.show_backup_codes'))
        else:
            flash("❌ The code entered is not valid.", "error")
    
    # Generate new secret
    secret = pyotp.random_base32()
    session['2fa_secret'] = secret
    
    # Generate URI for QR Code
    uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=current_user.email,
        issuer_name="Metisma"
    )
    
    return render_template('users/enable_2fa.html', uri=uri, secret=secret)


@users_bp.route('/show_backup_codes')
@login_required
def show_backup_codes():
    """Display backup codes"""
    backup_codes = session.get('backup_codes')
    if not backup_codes:
        flash("⚠️ No backup codes found.", "warning")
        return redirect(url_for('users.profile'))
    
    return render_template('users/show_backup_codes.html', codes=backup_codes)


@users_bp.route('/disable_2fa', methods=['POST'])
@login_required
def disable_2fa():
    """Disable two-factor authentication"""
    if not current_user.two_factor_enabled:
        flash("⚠️ Two-factor authentication is not enabled.", "warning")
        return redirect(url_for('users.profile'))
    
    code = request.form.get('code')
    backup_code = request.form.get('backup_code')
    
    verified = False
    
    if code:
        totp = pyotp.TOTP(current_user.two_factor_secret)
        verified = totp.verify(code)
    elif backup_code:
        import json
        if current_user.backup_codes:
            try:
                codes = json.loads(current_user.backup_codes)
                if backup_code in codes:
                    codes.remove(backup_code)
                    current_user.backup_codes = json.dumps(codes)
                    verified = True
            except:
                pass
    
    if verified:
        current_user.two_factor_enabled = False
        current_user.two_factor_secret = None
        db.session.commit()
        
        ActivityLog.log_activity(
            user_id=current_user.id,
            activity_type='2fa_disabled',
            description='Disable two-factor authentication',
            request=request,
            status='success'
        )

        flash("✅ Two-factor authentication disabled.", "success")
    else:
        flash("❌ The code entered is not valid.", "error")
    
    return redirect(url_for('users.profile'))


# ==================== 2FA Verification During Login ====================

@users_bp.route('/verify_2fa_login', methods=['GET', 'POST'])
def verify_2fa_login():
    """2FA code verification page during login"""
    # Check for user in session
    user_id = session.get('2fa_pending_user_id')
    if not user_id:
        flash("❌ No pending login found. Please log in first.", "warning")
        return redirect(url_for('users.login'))
    
    user = db.session.get(User, user_id)
    if not user or not user.two_factor_enabled:
        # If 2FA was disabled, return to login
        session.pop('2fa_pending_user_id', None)
        session.pop('2fa_remember_me', None)
        return redirect(url_for('users.login'))
    
    if request.method == 'POST':
        code = request.form.get('code')
        backup_code = request.form.get('backup_code')
        
        verified = False
        
        # بررسی کد TOTP
        if code:
            totp = pyotp.TOTP(user.two_factor_secret)
            # پنجره زمانی برای اختلاف ساعت (valid for 30 seconds before/after)
            verified = totp.verify(code, valid_window=1)
        
        # بررسی کد پشتیبان
        if not verified and backup_code:
            import json
            if user.backup_codes:
                try:
                    codes = json.loads(user.backup_codes)
                    if backup_code in codes:
                        codes.remove(backup_code)
                        user.backup_codes = json.dumps(codes)
                        verified = True
                except:
                    pass
        
        if verified:
            remember_me = session.get('2fa_remember_me', False)
            
            # لاگ فعالیت ورود موفق
            ActivityLog.log_activity(
                user_id=user.id,
                activity_type='login_2fa_verified',
                description='Successful 2FA verification during login',
                request=request,
                success=True
            )
            
            # ایجاد جلسه جدید
            login_session = LoginSession.create_session(
                user=user,
                request=request,
                remember_me=remember_me
            )
            session_token = login_session.session_token
            
            login_user(user, remember=remember_me)
            
            # پاک کردن session موقت
            session.pop('2fa_pending_user_id', None)
            session.pop('2fa_remember_me', None)
            
            # ذخیره توکن جلسه در cookie
            response = redirect(url_for('users.profile'))
            response.set_cookie('session_token', session_token, httponly=True, secure=True, samesite='Lax')
            
            flash("✅ Welcome! Two-factor authentication successful.", "success")
            return response
        else:
            flash("❌ The code entered is not valid. Please try again.", "error")
            ActivityLog.log_activity(
                user_id=user.id,
                activity_type='login_2fa_failed',
                description='Failed 2FA verification during login',
                request=request,
                success=False,
                failure_reason='invalid_2fa_code'
            )
    
    return render_template('users/verify_2fa_login.html', user=user)


# ==================== Session Management ====================

@users_bp.route('/sessions')
@login_required
def manage_sessions():
    """Manage active sessions"""
    sessions = LoginSession.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).order_by(LoginSession.created_at.desc()).all()
    
    return render_template('users/sessions.html', sessions=sessions)


@users_bp.route('/sessions/<int:session_id>/revoke', methods=['POST'])
@login_required
def revoke_session(session_id):
    """Revoke a specific session"""
    login_session = LoginSession.query.filter_by(
        id=session_id,
        user_id=current_user.id
    ).first()
    
    if login_session:
        login_session.logout()
        ActivityLog.log_activity(
            user_id=current_user.id,
            activity_type='session_revoked',
            description=f'Revoke session {session_id}',
            request=request,
            status='success'
        )
        flash("✅ Session successfully canceled.", "success")
    else:
        flash("❌ Session not found.", "error")
    
    return redirect(url_for('users.manage_sessions'))


@users_bp.route('/sessions/revoke_all', methods=['POST'])
@login_required
def revoke_all_sessions():
    """Revoke all sessions"""
    LoginSession.logout_all_sessions(current_user.id)
    
    ActivityLog.log_activity(
        user_id=current_user.id,
        activity_type='all_sessions_revoked',
        description='Cancel all sessions',
        request=request,
        status='success'
    )

    flash("✅ All sessions have been canceled.", "success")
    return redirect(url_for('users.manage_sessions'))


# ==================== User Activities ====================

@users_bp.route('/activity_log')
@login_required
def activity_log():
    """Display user activity log"""
    page = request.args.get('page', 1, type=int)
    activities = ActivityLog.query.filter_by(
        user_id=current_user.id
    ).order_by(
        ActivityLog.created_at.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('users/activity_log.html', activities=activities)