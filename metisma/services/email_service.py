# services/email_service.py
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask import current_app, render_template, url_for
from flask_mail import Message
from extensions import mail
from models import User

def generate_verification_token(user):
    """توکن امن بر اساس ایمیل کاربر تولید می‌کند"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    # ✅ اصلاح حیاتی: فقط رشته ایمیل سریالایز می‌شود، نه کل آبجکت User
    return serializer.dumps(user.email, salt='email-verify-salt')

def verify_email_token(token_string):
    """توکن را بررسی کرده و کاربر مربوطه را برمی‌گرداند"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        # بازیابی ایمیل از توکن
        email = serializer.loads(token_string, salt='email-verify-salt', max_age=86400) # اعتبار ۲۴ ساعت
        user = User.query.filter_by(email=email).first()

        if not user:
            return None, "User not found."
        return user, None

    except SignatureExpired:
        return None, "Token expired. Please use the resend link."
    except BadSignature:
        return None, "Token is invalid or tampered with."
    except Exception as e:
        current_app.logger.error(f"Token verification error: {e}")
        return None, "Token verification error."
def send_verification_email(user, token_string):
    """قالب ایمیل را رندر و ارسال می‌کند"""
    verify_url = url_for('users.verify_email_route', token=token_string, _external=True)
    
    html_body = render_template(
        'email/verify_email.html',
        username=user.username,
        verify_url=verify_url,
        app_name='Metisma'
    )
    
    msg = Message(
        subject='✅ Activate Your Metisma Account',
        recipients=[user.email],
        html=html_body,
        body=f'Welcome {user.username}! Please verify your email: {verify_url}',
        sender=current_app.config.get('MAIL_DEFAULT_SENDER')
    )
    
    try:
        mail.send(msg)
        current_app.logger.info(f'Verification email sent to {user.email}')
        return True, None
    except Exception as e:
        current_app.logger.error(f'Email send failed: {e}')
        return False, str(e)