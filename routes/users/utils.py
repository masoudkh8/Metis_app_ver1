# routes/users/utils.py
from flask import url_for
from flask_mail import Message
from app import mail, get_serializer

def send_email_verification(user):
    s = get_serializer()
    token = s.dumps(user.email, salt='email-verify')

    verify_url = url_for('users.confirm_email', token=token, _external=True)

    html_body = f"""
    <h2>Congratulations! Request to upgrade to special user</h2>
    <p>To verify your email address, click the link below:</p>
    <p><a href="{verify_url}" style="color: #007BFF;">Email verification</a></p>
    <p>This link will expire after 1 hour.</p>
    <p>If you did not make this request, please ignore this email.</p>
    """

    msg = Message(
        subject="Email confirmation for upgrade to special user",
        recipients=[user.email],
        html=html_body
    )
    mail.send(msg)