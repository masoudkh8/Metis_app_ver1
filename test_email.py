# test_email.py
from app import create_app
from extensions import mail
from flask_mail import Message

app = create_app()

with app.app_context():
    try:
        msg = Message(
            subject='🧪 Test Email from Metisma',
            recipients=['msdkhlj110@gmail.com'],  # ایمیل خودتان برای تست
            body='If you receive this, your email configuration is working! ✅',
            sender=app.config.get('MAIL_DEFAULT_SENDER')
        )
        mail.send(msg)
        print('✅ Email sent successfully!')
    except Exception as e:
        print(f'❌ Error: {e}')