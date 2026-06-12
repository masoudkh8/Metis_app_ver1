# routes/social/routes.py
"""
Metisma Social Network Routes Module
Includes: Public Profile, News Feed, Follow/Unfollow, Like, Comment, Share
"""
from flask_babel import gettext as _
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from models import db
from models.user import User, UserProfile
from models.social import Post, Comment, Like, Follow
from models.notification import Notification
from datetime import datetime
import pytz
from celery_app import celery, send_notification_task
tehran_tz = pytz.timezone('Asia/Tehran')

social_bp = Blueprint('social', __name__, url_prefix='/social')


def send_notification_async(user_id, notification_data):
    """
    Send notification via Celery task for real-time delivery.
    Falls back to synchronous if Celery is not available.
    """
    try:
        task = send_notification_task.delay(user_id, notification_data)
        return task
    except Exception:
        # Fallback: create notification synchronously
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
        return None


# ============================================
# 1. Public Profile
# ============================================

@social_bp.route('/profile/<username>')
def public_profile(username):
    """
    Display user's public profile
    This page is viewable by everyone (even without login) - SEO Friendly
    """
    # Get user from database
    profile_user = User.query.filter_by(username=username, is_active=True).first_or_404()
    
    # Get user's public posts
    profile_posts = Post.query.filter_by(
        author_id=profile_user.id,
        visibility='public'
    ).order_by(Post.created_at.desc()).limit(20).all()
    
    return render_template('users/public_profile.html', 
                         profile_user=profile_user, 
                         profile_posts=profile_posts)


# ============================================
# 2. Follow/Connection System (Graph/Connections)
# ============================================

@social_bp.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow_user(user_id):
    """
    Follow a user
    """
    if current_user.id == user_id:
        return jsonify({'error': _('social.cannot_follow_self')}), 400
    
    user_to_follow = User.query.get_or_404(user_id)
    
    # Check if already following
    existing_follow = Follow.is_following(current_user.id, user_id)
    
    if not existing_follow:
        follow = Follow(
            follower_id=current_user.id,
            following_id=user_id,
            connection_type='public'
        )
        db.session.add(follow)
        
        # Create notification data
        notification_data = {
            'title': _('social.new_follower_notification'),
            'message': f'{current_user.username} {_("social.followed_you")}',
            'type': 'follow',
            'actor_id': current_user.id
        }
        
        # Send notification asynchronously
        send_notification_async(user_id, notification_data)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': _('social.now_following').format(username=user_to_follow.username),
            'followers_count': Follow.get_followers_count(user_id)
        })
    else:
        return jsonify({'error': _('social.already_following')}), 400


@social_bp.route('/unfollow/<int:user_id>', methods=['POST'])
@login_required
def unfollow_user(user_id):
    """
    Unfollow a user
    """
    if current_user.id == user_id:
        return jsonify({'error': _('social.cannot_follow_self')}), 400
    
    # Find follow record
    follow = Follow.query.filter_by(
        follower_id=current_user.id,
        following_id=user_id
    ).first()
    
    if follow:
        db.session.delete(follow)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': _('social.unfollowed'),
            'followers_count': Follow.get_followers_count(user_id)
        })
    else:
        return jsonify({'error': _('social.not_following')}), 400


@social_bp.route('/followers/<int:user_id>')
def user_followers(user_id):
    """
    Display list of user's followers
    """
    user = User.query.get_or_404(user_id)
    followers = Follow.query.filter_by(following_id=user_id).all()
    
    return render_template('users/followers_list.html', 
                         user=user, 
                         followers=followers)


@social_bp.route('/following/<int:user_id>')
def user_following(user_id):
    """
    Display list of users that this user is following
    """
    user = User.query.get_or_404(user_id)
    following = Follow.query.filter_by(follower_id=user_id).all()
    
    return render_template('users/following_list.html', 
                         user=user, 
                         following=following)


# ============================================
# 3. News Feed (The Feed)
# ============================================

@social_bp.route('/feed')
@login_required
def news_feed():
    """
    Personalized news feed for user
    Display posts from followed users + featured posts
    Enhanced algorithm using TrustScore
    """
    # Get feed with TrustScore-enhanced algorithm
    feed_posts = Post.get_feed_with_trust_score(current_user.id, limit=50, include_featured=True)
    
    return render_template('users/feed.html', feed_posts=feed_posts)


@social_bp.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """
    Create new post
    """
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        visibility = request.form.get('visibility', 'public')
        
        if not content:
            flash(_('social.post_content_empty'), 'error')
            return redirect(url_for('social.news_feed'))
        
        # Process uploaded files (if any)
        media = {'images': [], 'files': []}
        # TODO: Add file upload logic
        
        # Process product/company tags
        tagged_products = []
        tagged_companies = []
        # TODO: Add tagging logic
        
        post = Post(
            author_id=current_user.id,
            content=content,
            visibility=visibility,
            media=media,
            tagged_products=tagged_products,
            tagged_companies=tagged_companies
        )
        
        db.session.add(post)
        db.session.commit()
        
        flash(_('social.post_published'), 'success')
        return redirect(url_for('social.public_profile', username=current_user.username))
    
    return render_template('users/create_post.html')


@social_bp.route('/post/<int:post_id>')
def view_post(post_id):
    """
    Display a specific post
    """
    post = Post.query.get_or_404(post_id)
    
    # Increment view count
    post.views_count += 1
    db.session.commit()
    
    # Get comments
    comments = Comment.query.filter_by(
        post_id=post_id,
        is_deleted=False
    ).order_by(Comment.created_at.asc()).all()
    
    return render_template('users/post_detail.html', post=post, comments=comments)


@social_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """
    Delete post (only by author or admin)
    """
    post = Post.query.get_or_404(post_id)
    
    if post.author_id != current_user.id and not current_user.is_admin_or_moderator:
        flash(_('messages.access_denied'), 'error')
        return redirect(url_for('social.view_post', post_id=post_id))
    
    db.session.delete(post)
    db.session.commit()
    
    flash(_('social.post_deleted'), 'success')
    return redirect(url_for('social.public_profile', username=post.author.username))


# ============================================
# 4. Engagement - Like and Comment
# ============================================

@social_bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    """
    Like a post
    """
    post = Post.query.get_or_404(post_id)
    
    # Check if already liked
    existing_like = Like.is_liked(current_user.id, 'post', post_id)
    
    if not existing_like:
        like = Like(
            user_id=current_user.id,
            target_type='post',
            target_id=post_id
        )
        db.session.add(like)
        
        # Increment like counter
        post.likes_count += 1
        
        # Create notification for post author (if not liking own post)
        if post.author_id != current_user.id:
            notification_data = {
                'title': _('social.new_like_notification'),
                'message': f'{current_user.username} {_("social.liked_your_post")}',
                'type': 'like',
                'actor_id': current_user.id,
                'related_id': post_id,
                'related_type': 'post'
            }
            send_notification_async(post.author_id, notification_data)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'likes_count': post.likes_count,
            'is_liked': True
        })
    else:
        # Unlike
        like = Like.query.filter_by(
            user_id=current_user.id,
            target_type='post',
            target_id=post_id
        ).first()
        
        if like:
            db.session.delete(like)
            post.likes_count -= 1
            db.session.commit()
            
            return jsonify({
                'success': True,
                'likes_count': post.likes_count,
                'is_liked': False
            })
    
    return jsonify({'error': _('messages.error_occurred')}), 500


@social_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    """
    Add comment to a post
    """
    post = Post.query.get_or_404(post_id)
    
    content = request.form.get('content', '').strip()
    parent_id = request.form.get('parent_id', type=int)  # For reply to comment
    
    if not content:
        flash(_('social.comment_empty'), 'error')
        return redirect(url_for('social.view_post', post_id=post_id))
    
    comment = Comment(
        post_id=post_id,
        author_id=current_user.id,
        content=content,
        parent_id=parent_id
    )
    
    db.session.add(comment)
    
    # Increment comment counter
    post.comments_count += 1
    
    # Create notification for post author (if not commenting on own post)
    if post.author_id != current_user.id:
        notification_data = {
            'title': _('social.new_comment_notification'),
            'message': f'{current_user.username} {_("social.commented_on_your_post")}',
            'type': 'comment',
            'actor_id': current_user.id,
            'related_id': post_id,
            'related_type': 'post'
        }
        send_notification_async(post.author_id, notification_data)
    
    # If replying to another comment, notify the original comment author
    if parent_id:
        parent_comment = db.session.get(Comment, parent_id)
        if parent_comment and parent_comment.author_id != current_user.id:
            notification_data = {
                'title': _('social.new_reply_notification'),
                'message': f'{current_user.username} {_("social.replied_to_your_comment")}',
                'type': 'comment_reply',
                'actor_id': current_user.id,
                'related_id': post_id,
                'related_type': 'comment'
            }
            send_notification_async(parent_comment.author_id, notification_data)
    
    db.session.commit()
    
    flash(_('social.comment_posted'), 'success')
    return redirect(url_for('social.view_post', post_id=post_id))


@social_bp.route('/comment/<int:comment_id>/like', methods=['POST'])
@login_required
def like_comment(comment_id):
    """
    Like a comment
    """
    comment = Comment.query.get_or_404(comment_id)
    
    existing_like = Like.is_liked(current_user.id, 'comment', comment_id)
    
    if not existing_like:
        like = Like(
            user_id=current_user.id,
            target_type='comment',
            target_id=comment_id
        )
        db.session.add(like)
        comment.likes_count += 1
        
        # Notification for comment owner
        if comment.author_id != current_user.id:
            notification_data = {
                'title': _('social.new_like_notification'),
                'message': f'{current_user.username} {_("social.liked_your_comment")}',
                'type': 'like',
                'actor_id': current_user.id,
                'related_id': comment_id,
                'related_type': 'comment'
            }
            send_notification_async(comment.author_id, notification_data)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'likes_count': comment.likes_count,
            'is_liked': True
        })
    else:
        like = Like.query.filter_by(
            user_id=current_user.id,
            target_type='comment',
            target_id=comment_id
        ).first()
        
        if like:
            db.session.delete(like)
            comment.likes_count -= 1
            db.session.commit()
            
            return jsonify({
                'success': True,
                'likes_count': comment.likes_count,
                'is_liked': False
            })
    
    return jsonify({'error': _('messages.error_occurred')}), 500


@social_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """
    Delete comment (soft delete)
    """
    comment = Comment.query.get_or_404(comment_id)
    
    if comment.author_id != current_user.id and not current_user.is_admin_or_moderator:
        flash(_('messages.access_denied'), 'error')
        return redirect(url_for('social.view_post', post_id=comment.post_id))
    
    # Soft delete to preserve conversation thread
    comment.is_deleted = True
    comment.content = _('social.this_comment_deleted')
    db.session.commit()
    
    # Decrease post comment counter
    comment.post.comments_count -= 1
    db.session.commit()
    
    flash(_('social.comment_deleted'), 'success')
    return redirect(url_for('social.view_post', post_id=comment.post_id))


# ============================================
# 5. API endpoints for AJAX calls
# ============================================

@social_bp.route('/api/check-follow/<int:user_id>')
@login_required
def check_follow(user_id):
    """
    Check follow status (API)
    """
    is_following = Follow.is_following(current_user.id, user_id)
    return jsonify({
        'is_following': is_following,
        'followers_count': Follow.get_followers_count(user_id),
        'following_count': Follow.get_following_count(user_id)
    })


@social_bp.route('/api/post/<int:post_id>/stats')
def get_post_stats(post_id):
    """
    Get post statistics (API)
    """
    post = Post.query.get_or_404(post_id)
    is_liked = False
    
    if current_user.is_authenticated:
        is_liked = Like.is_liked(current_user.id, 'post', post_id)
    
    return jsonify({
        'likes_count': post.likes_count,
        'comments_count': post.comments_count,
        'shares_count': post.shares_count,
        'views_count': post.views_count,
        'is_liked': is_liked
    })


# ============================================
# 6. Helper Pages
# ============================================

@social_bp.route('/explore')
def explore():
    """
    Discover featured posts and suggested users
    """
    featured_posts = Post.query.filter_by(
        is_featured=True,
        visibility='public'
    ).order_by(Post.created_at.desc()).limit(20).all()
    
    # Suggested users (based on TrustScore)
    suggested_users = User.query.join(UserProfile).filter(
        User.is_active == True,
        User.role.value.in_(['producer', 'buyer', 'broker'])
    ).order_by(db.desc(User.trust_score)).limit(10).all() if hasattr(User, 'trust_score') else []
    
    return render_template('users/explore.html', 
                         featured_posts=featured_posts, 
                         suggested_users=suggested_users)
# Share System Routes Added
