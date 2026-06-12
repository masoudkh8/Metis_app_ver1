# celery_app.py
from celery import Celery
from flask import Flask

def make_celery(app):
    """Create a Celery instance configured with the Flask app."""
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    
    # Configure Celery from Flask config
    celery.conf.update(
        task_serializer=app.config.get('CELERY_TASK_SERIALIZER', 'json'),
        result_serializer=app.config.get('CELERY_RESULT_SERIALIZER', 'json'),
        timezone=app.config.get('CELERY_TIMEZONE', 'UTC'),
        accept_content=['json'],
        result_expires=3600,
        task_track_started=True,
        task_send_sent_event=True,
    )
    
    class ContextTask(celery.Task):
        """Make Celery tasks run within Flask application context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery


def create_celery_app():
    """Create Flask app and initialize Celery."""
    from app import create_app
    from config import Config
    
    app = create_app()
    app.config.from_object(Config)
    
    celery = make_celery(app)
    return celery, app


# Create celery instance for direct imports
celery, flask_app = create_celery_app()


# Example background tasks
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
        # Retry on failure
        raise self.retry(exc=exc, countdown=60)


@celery.task(bind=True, max_retries=3)
def send_sms_task(self, phone_number, message):
    """Send SMS in background using Kavenegar or AmootSMS."""
    from config import Config
    import requests
    
    try:
        # Use Kavenegar API
        if Config.KAVENEGAR_API_KEY:
            url = f"https://api.kavenegar.com/v1/{Config.KAVENEGAR_API_KEY}/sms/send.json"
            params = {
                'receptor': phone_number,
                'message': message
            }
            response = requests.post(url, data=params, timeout=10)
            response.raise_for_status()
            return {'status': 'success', 'message': f'SMS sent to {phone_number}'}
        
        # Fallback to AmootSMS
        elif Config.AMOOTSMS_TOKEN:
            url = "https://rest.amootsms.ir/api/send"
            headers = {'Authorization': f'Bearer {Config.AMOOTSMS_TOKEN}'}
            data = {
                'to': phone_number,
                'text': message
            }
            response = requests.post(url, json=data, headers=headers, timeout=10)
            response.raise_for_status()
            return {'status': 'success', 'message': f'SMS sent to {phone_number}'}
        else:
            return {'status': 'error', 'message': 'No SMS provider configured'}
            
    except Exception as exc:
        # Retry on failure
        raise self.retry(exc=exc, countdown=60)


@celery.task(bind=True)
def process_heavy_data_task(self, data_id):
    """Process heavy database queries in background."""
    from models import db
    import time
    
    try:
        # Simulate heavy processing
        time.sleep(2)
        
        # Example: Process some data
        # You can replace this with actual data processing logic
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
        # Add your cleanup logic here
        # Example: Delete old records, clear cache, etc.
        return {'status': 'success', 'message': 'Cleanup completed'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


@celery.task(bind=True, max_retries=3)
def send_notification_task(self, user_id, notification_data):
    """
    Send notification to user via database and optionally via WebSocket.
    This task runs in background to avoid blocking the main request.
    """
    from models import db
    from models.notification import Notification

    try:
        # Create notification in database
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

        # Optional: Send via WebSocket for real-time delivery
        # You can implement this later if needed
        # from app import socketio
        # socketio.emit('notification', {
        #     'id': notification.id,
        #     'title': notification.title,
        #     'message': notification.message,
        #     'type': notification.notification_type
        # }, room=f'user_{user_id}')

        return {
            'status': 'success',
            'notification_id': notification.id,
            'message': f'Notification sent to user {user_id}'
        }

    except Exception as exc:
        # Retry on failure (max 3 times with 60 second delay)
        db.session.rollback()
        raise self.retry(exc=exc, countdown=60)


if __name__ == '__main__':
    celery.start()
