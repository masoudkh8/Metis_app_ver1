# models/notification.py
from . import db
from datetime import datetime
import pytz
tehran_tz = pytz.timezone('Asia/Tehran')

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)  # کسی که اعلان رو دریافت می‌کند
    
    # نوع اعلان: follow, like, comment, comment_reply, share, mention, system
    notification_type = db.Column(db.String(50), nullable=False, default='system')
    
    # کاربر انجام‌دهنده عمل (مثلاً کسی که لایک کرده)
    actor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # آیتم مرتبط (post_id, comment_id, etc.)
    related_id = db.Column(db.Integer, nullable=True)
    related_type = db.Column(db.String(50), nullable=True)  # 'post', 'comment', etc.
    
    message = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(200), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(tehran_tz), index=True)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], back_populates='notifications')
    actor = db.relationship('User', foreign_keys=[actor_id], backref='actor_notifications')
    
    def __repr__(self):
        return f"<Notification for {self.user.username}: {self.notification_type}>" if self.user else f"<Notification {self.id}>"
    
    def to_dict(self):
        """Convert notification to dictionary for API"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'notification_type': self.notification_type,
            'actor_id': self.actor_id,
            'related_id': self.related_id,
            'related_type': self.related_type,
            'message': self.message,
            'title': self.title,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'actor': {
                'id': self.actor.id if self.actor else None,
                'username': self.actor.username if self.actor else None,
            } if self.actor else None
        }