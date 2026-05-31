# tasks/social_notifications.py
"""
Celery Tasks for Social Network Notifications
These tasks handle asynchronous notification delivery and real-time updates.
"""

from celery_app import celery
from models import db
from models.notification import Notification
from datetime import datetime
import pytz

tehran_tz = pytz.timezone('Asia/Tehran')


@celery.task(bind=True, max_retries=3)
def send_notification_task(self, user_id, notification_data):
    """
    Create and send notification asynchronously.
    
    Args:
        user_id: ID of the user to notify
        notification_data: Dictionary containing:
            - title: Notification title
            - message: Notification message
            - type: Notification type (follow, like, comment, etc.)
            - actor_id: ID of the user who triggered the notification
            - related_id: ID of the related object (post, comment, etc.)
            - related_type: Type of the related object
    """
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
        
        # Try to send real-time notification via SocketIO
        try:
            from socketio_app import send_realtime_notification
            send_realtime_notification(user_id, {
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'type': notification.notification_type,
                'actor_id': notification.actor_id,
                'created_at': notification.created_at.isoformat() if notification.created_at else None
            })
        except Exception as e:
            # SocketIO not available, notification is already saved in DB
            print(f"Real-time notification failed: {e}")
        
        return {
            'status': 'success',
            'notification_id': notification.id,
            'user_id': user_id
        }
        
    except Exception as exc:
        # Retry on failure
        raise self.retry(exc=exc, countdown=60)


@celery.task
def cleanup_old_notifications(days_old=30):
    """
    Clean up old notifications periodically.
    Delete notifications older than specified days.
    """
    from datetime import timedelta
    
    cutoff_date = datetime.now(tehran_tz) - timedelta(days=days_old)
    
    deleted_count = Notification.query.filter(
        Notification.created_at < cutoff_date
    ).delete()
    
    db.session.commit()
    
    return {
        'status': 'success',
        'deleted_count': deleted_count,
        'cutoff_date': cutoff_date.isoformat()
    }


@celery.task
def calculate_feed_score_for_user(user_id):
    """
    Calculate personalized feed score for a user based on TrustScore.
    This task can be run periodically to pre-compute feed rankings.
    """
    from models.social import Post
    from models.user import User
    
    # Get posts from followed users
    from models.social import Follow
    
    followed_users = Follow.query.filter_by(follower_id=user_id).all()
    followed_user_ids = [f.following_id for f in followed_users]
    
    # Get posts and calculate scores
    posts = Post.query.filter(
        Post.author_id.in_(followed_user_ids),
        Post.visibility == 'public'
    ).limit(100).all()
    
    scored_posts = []
    for post in posts:
        # Calculate score based on TrustScore and engagement
        author = db.session.get(User, post.author_id)
        trust_score = author.trust_score if hasattr(author, 'trust_score') else 50
        
        # Score formula: TrustScore + engagement bonuses
        score = trust_score + (post.likes_count * 2) + (post.comments_count * 3)
        
        scored_posts.append({
            'post_id': post.id,
            'score': score,
            'author_trust_score': trust_score
        })
    
    # Sort by score
    scored_posts.sort(key=lambda x: x['score'], reverse=True)
    
    return {
        'status': 'success',
        'user_id': user_id,
        'posts_scored': len(scored_posts),
        'top_post_scores': scored_posts[:10]
    }
