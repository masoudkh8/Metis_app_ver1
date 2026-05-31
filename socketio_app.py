# socketio_app.py - Flask-SocketIO Configuration for Real-time Notifications
"""
Metisma Platform - Real-time WebSocket Support using Flask-SocketIO
Features:
- Real-time notifications (push notifications in-app)
- Live feed updates
- Chat support (future)
- Presence tracking (online/offline status)
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user
from models import db
from models.notification import Notification
from datetime import datetime
import pytz

tehran_tz = pytz.timezone('Asia/Tehran')

# Initialize SocketIO
socketio = SocketIO()

def init_socketio(app):
    """Initialize SocketIO with the Flask app."""
    socketio.init_app(
        app,
        cors_allowed_origins="*",  # Configure appropriately for production
        async_mode='eventlet',  # or 'gevent' for better performance
        message_queue=app.config.get('REDIS_URL', 'redis://localhost:6379/0'),
        ping_timeout=60,
        ping_interval=25
    )
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        if current_user.is_authenticated:
            # Join user's personal room for notifications
            join_room(f'user_{current_user.id}')
            print(f'User {current_user.id} connected via WebSocket')
            
            # Emit connection confirmation
            emit('connected', {
                'user_id': current_user.id,
                'message': 'Connected to real-time notifications'
            })
            
            # Send unread notification count
            unread_count = Notification.query.filter_by(
                user_id=current_user.id,
                is_read=False
            ).count()
            
            emit('unread_count', {'count': unread_count})
        
        return True
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        if current_user.is_authenticated:
            leave_room(f'user_{current_user.id}')
            print(f'User {current_user.id} disconnected from WebSocket')
        
        return True
    
    @socketio.on('join_room_event')
    def handle_join_room(data):
        """Join a specific room (e.g., for post comments, groups)."""
        if not current_user.is_authenticated:
            return
        
        room = data.get('room')
        if room:
            join_room(room)
            emit('joined_room', {'room': room})
    
    @socketio.on('leave_room_event')
    def handle_leave_room(data):
        """Leave a specific room."""
        if not current_user.is_authenticated:
            return
        
        room = data.get('room')
        if room:
            leave_room(room)
            emit('left_room', {'room': room})
    
    @socketio.on('mark_notification_read')
    def handle_mark_read(data):
        """Mark notification as read via WebSocket."""
        if not current_user.is_authenticated:
            return
        
        notification_id = data.get('notification_id')
        if notification_id:
            notification = db.session.get(Notification, notification_id)
            if notification and notification.user_id == current_user.id:
                notification.is_read = True
                db.session.commit()
                
                # Update unread count
                unread_count = Notification.query.filter_by(
                    user_id=current_user.id,
                    is_read=False
                ).count()
                
                emit('unread_count', {'count': unread_count})
                emit('notification_marked', {
                    'notification_id': notification_id,
                    'success': True
                })
    
    @socketio.on('mark_all_read')
    def handle_mark_all_read(data):
        """Mark all notifications as read."""
        if not current_user.is_authenticated:
            return
        
        Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).update({'is_read': True})
        db.session.commit()
        
        emit('unread_count', {'count': 0})
        emit('all_notifications_read', {'success': True})


def send_realtime_notification(user_id, notification_data):
    """
    Send real-time notification to a specific user.
    This function should be called after creating a notification in the database.
    
    Args:
        user_id: ID of the user to notify
        notification_data: Dictionary containing notification details
    """
    try:
        # Emit to user's personal room
        socketio.emit('new_notification', notification_data, room=f'user_{user_id}')
        
        # Also emit update to unread count
        unread_count = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()
        
        socketio.emit('unread_count', {'count': unread_count}, room=f'user_{user_id}')
        
        print(f'Real-time notification sent to user {user_id}')
    except Exception as e:
        print(f'Error sending real-time notification: {e}')


def notify_user_follow(follower_id, followed_user_id):
    """Send real-time notification when someone follows a user."""
    from flask import url_for
    
    notification_data = {
        'type': 'follow',
        'title': 'New Follower',
        'message': 'User followed you',
        'actor_id': follower_id,
        'url': url_for('social.public_profile', username='_username_', _external=True),
        'created_at': datetime.now(tehran_tz).isoformat()
    }
    
    send_realtime_notification(followed_user_id, notification_data)


def notify_post_like(liker_id, post_author_id, post_id):
    """Send real-time notification when someone likes a post."""
    from flask import url_for
    
    notification_data = {
        'type': 'like',
        'title': 'New Like',
        'message': 'User liked your post',
        'actor_id': liker_id,
        'related_id': post_id,
        'related_type': 'post',
        'url': url_for('social.view_post', post_id=post_id, _external=True),
        'created_at': datetime.now(tehran_tz).isoformat()
    }
    
    send_realtime_notification(post_author_id, notification_data)


def notify_comment(commenter_id, post_author_id, post_id, comment_content):
    """Send real-time notification when someone comments on a post."""
    from flask import url_for
    
    notification_data = {
        'type': 'comment',
        'title': 'New Comment',
        'message': 'User commented on your post',
        'actor_id': commenter_id,
        'related_id': post_id,
        'related_type': 'post',
        'comment_preview': comment_content[:100] if comment_content else '',
        'url': url_for('social.view_post', post_id=post_id, _external=True),
        'created_at': datetime.now(tehran_tz).isoformat()
    }
    
    send_realtime_notification(post_author_id, notification_data)


def notify_share(sharer_id, post_author_id, post_id):
    """Send real-time notification when someone shares a post."""
    from flask import url_for
    
    notification_data = {
        'type': 'share',
        'title': 'New Share',
        'message': 'User shared your post',
        'actor_id': sharer_id,
        'related_id': post_id,
        'related_type': 'post',
        'url': url_for('social.view_post', post_id=post_id, _external=True),
        'created_at': datetime.now(tehran_tz).isoformat()
    }
    
    send_realtime_notification(post_author_id, notification_data)
