# celery_app.py
from celery import Celery, Task

# ۱. ساخت یک نمونه خام از Celery (بدون نیاز به Flask app در لحظه ایمپورت)
celery = Celery(__name__)


# ۲. کلاس ContextTask برای اجرای تسک‌ها در فلسک Context
class ContextTask(Task):
    abstract = True

    def __call__(self, *args, **kwargs):
        # اپلیکیشن فلسک را از نمونه celery دریافت می‌کنیم
        app = getattr(celery, 'flask_app', None)
        if app:
            with app.app_context():
                return self.run(*args, **kwargs)
        return self.run(*args, **kwargs)


# اختصاص کلاس ContextTask به celery (قبل از تعریف تسک‌ها)
celery.Task = ContextTask


# ۳. تابع init_celery برای اتصال و کانفیگ سلری با Flask app
def init_celery(app):
    """Configure Celery with the Flask app."""
    # ذخیره اپلیکیشن در نمونه celery برای استفاده در ContextTask
    celery.flask_app = app

    celery.conf.update(
        broker=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        task_serializer=app.config.get('CELERY_TASK_SERIALIZER', 'json'),
        result_serializer=app.config.get('CELERY_RESULT_SERIALIZER', 'json'),
        timezone=app.config.get('CELERY_TIMEZONE', 'UTC'),
        accept_content=['json'],
        result_expires=3600,
        task_track_started=True,
        task_send_sent_event=True,
    )
    return celery


# ❌ تابع create_celery_app و خط اجرای آن در پایین فایل را کاملاً حذف کنید!
# این خط باعث Circular Import می‌شد.

# ۴. تعریف تسک‌های پس‌زمینه (Background Tasks)
@celery.task(bind=True, max_retries=3)
def send_email_task(self, recipient, subject, body):
    """Send email in background using Flask-Mail."""
    from flask_mail import Message
    from extensions import mail

    try:
        msg = Message(subject, recipients=[recipient], body=body)
        mail.send(msg)
        return {'status': 'success', 'message': f'Email sent to {recipient}'}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery.task(bind=True, max_retries=3)
def send_sms_task(self, phone_number, message):
    """Send SMS in background using Kavenegar or AmootSMS."""
    from config import Config
    import requests

    try:
        if Config.KAVENEGAR_API_KEY:
            url = f"https://api.kavenegar.com/v1/{Config.KAVENEGAR_API_KEY}/sms/send.json"
            params = {'receptor': phone_number, 'message': message}
            response = requests.post(url, data=params, timeout=10)
            response.raise_for_status()
            return {'status': 'success', 'message': f'SMS sent to {phone_number}'}

        elif Config.AMOOTSMS_TOKEN:
            url = "https://rest.amootsms.ir/api/send"
            headers = {'Authorization': f'Bearer {Config.AMOOTSMS_TOKEN}'}
            data = {'to': phone_number, 'text': message}
            response = requests.post(url, json=data, headers=headers, timeout=10)
            response.raise_for_status()
            return {'status': 'success', 'message': f'SMS sent to {phone_number}'}
        else:
            return {'status': 'error', 'message': 'No SMS provider configured'}

    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery.task(bind=True)
def process_heavy_data_task(self, data_id):
    """Process heavy database queries in background."""
    from models import db
    import time

    try:
        time.sleep(2)
        result = {
            'data_id': data_id,
            'processed_at': time.time(),
            'status': 'completed'
        }
        return result
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)


@celery.task
def cleanup_old_sessions():
    """Clean up old session data periodically."""
    from models import db
    from datetime import datetime, timedelta

    try:
        return {'status': 'success', 'message': 'Cleanup completed'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


@celery.task(bind=True, max_retries=3)
def send_notification_task(self, user_id, notification_data):
    """Send notification to user via database."""
    from models import db
    from models.notification import Notification

    try:
        notification = Notification(
            user_id=user_id,
            title=notification_data.get('title', ''),
            message=notification_data.get('message', ''),
            notification_type=notification_data.get('type', 'system'),
            actor_id=notification_data.get('actor_id'),
            related_id=notification_data.get('related_id'),
            related_type=notification_data.get('related_type')
        )

        db.session.add(notification)
        db.session.commit()

        return {
            'status': 'success',
            'notification_id': notification.id,
            'message': f'Notification sent to user {user_id}'
        }

    except Exception as exc:
        db.session.rollback()
        raise self.retry(exc=exc, countdown=60)


# ۵. مقداردهی اولیه خودکار برای Celery Worker
# وقتی سلری ورکر اجرا می‌شود، این فایل ایمپورت می‌شود اما create_app صدا زده نمی‌شود.
# این کد تضمین می‌کند که وقتی ورکر در حال اجراست، فلسک اپ هم ساخته شود تا تسک‌ها Context داشته باشند.
import sys

if 'worker' in sys.argv or 'beat' in sys.argv:
    from app import create_app

    flask_app = create_app()
    init_celery(flask_app)

if __name__ == '__main__':
    celery.start()