# tasks/__init__.py
"""
Celery Tasks Package
Import all tasks here to ensure they are registered with Celery.
"""

from .social_notifications import (
    send_notification_task,
    cleanup_old_notifications,
    calculate_feed_score_for_user
)

__all__ = [
    'send_notification_task',
    'cleanup_old_notifications',
    'calculate_feed_score_for_user'
]
