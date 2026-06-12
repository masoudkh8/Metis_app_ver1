# routes/social/routes.py
"""
Metisma Social Network Routes Module
Includes: Public Profile, News Feed, Follow/Unfollow, Like, Comment, Share
"""
from flask_babel import gettext as _
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from models.user import Role
from extensions import limiter  # ✅ ایمپورت نمونه سراسری limiter
from flask_limiter.util import get_remote_address
from models import db
from models.user import User, UserProfile
from models.social import Post, Comment, Like, Follow
from models.notification import Notification
from datetime import datetime
import pytz

from utils.file_upload import upload_social_media # ایمپورت تابع جدید
tehran_tz = pytz.timezone('Asia/Tehran')
from utils.social_cache import increment_post_views_async, get_post_views

from . import social_bp


def send_notification_async(user_id, notification_data):
    """
    Send notification via Celery task for real-time delivery.
    Falls back to synchronous if Celery is not available.
    """
    from celery_app import celery, send_notification_task
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

    # 🔥 اصلاح حیاتی: بررسی فالو به صورت بهینه (بدون لود کردن کل لیست)
    is_following = False
    if current_user.is_authenticated:
        # روش ۱: اگر متد is_following در مدل User شما تعریف شده باشد (طبق فایل راهنما)
        is_following = current_user.is_following(profile_user.id)

        # روش ۲ (جایگزین): اگر متد بالا کار نکرد، از این کوئری مستقیم و سبک استفاده کنید:
        # is_following = Follow.query.filter_by(follower_id=current_user.id, following_id=profile_user.id).first() is not None

    return render_template('users/public_profile.html',
                           profile_user=profile_user,
                           profile_posts=profile_posts,
                           is_following=is_following)  # 🔥 ارسال متغیر به قالب


# ============================================
# 2. Follow/Connection System (Graph/Connections)
# ============================================

@social_bp.route('/follow/<int:user_id>', methods=['POST'])
@login_required
@limiter.limit("10/minute")
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
    # 🔥 اضافه شده: استخراج IDهای فالوینگ‌های کاربر فعلی
    following_ids = set()
    if current_user.is_authenticated:
        following_ids = set(
            f.following_id for f in Follow.query.filter_by(follower_id=current_user.id).all()
        )

    return render_template('users/followers_list.html',
                             user=user,
                             followers=followers,
                             following_ids=following_ids) # پاس دادن به تمپلیت


@social_bp.route('/following/<int:user_id>')
def user_following(user_id):
    """
    Display list of users that this user is following
    """
    user = User.query.get_or_404(user_id)
    following = Follow.query.filter_by(follower_id=user_id).all()


    following_ids = set()
    if current_user.is_authenticated:
        following_ids = set(f.following_id for f in Follow.query.filter_by(follower_id=current_user.id).all())

    return render_template('users/following_list.html',
                           user=user,
                           following=following,
                           following_ids=following_ids)


# ============================================
# 3. News Feed (The Feed)
# ============================================


@social_bp.route('/feed')
@login_required
def news_feed():
    # ۱. دریافت شماره صفحه از URL (پیش‌فرض صفحه ۱)
    page = request.args.get('page', 1, type=int)
    per_page = 15

    # ۲. دریافت پست‌های صفحه جاری (Paginate)
    feed_posts = Post.query.filter(
        Post.visibility.in_(['public', 'followers_only'])
    ).order_by(Post.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    # ۳. بهینه‌سازی کوئری لایک‌ها: فقط برای پست‌های "همین صفحه" کوئری می‌زنیم
    liked_post_ids = set()
    liked_comment_ids = set()

    # نکته: @login_required تضمین می‌کند که current_user همیشه احراز هویت شده است.
    # پس نیازی به if current_user.is_authenticated نیست.
    if feed_posts.items:  # اگر پستی در این صفحه وجود دارد

        # الف) استخراج ID پست‌های موجود در همین صفحه
        post_ids_on_page = [post.id for post in feed_posts.items]

        # ب) کوئری بهینه: فقط لایک‌های کاربر جاری را برای همین پست‌های خاص بررسی می‌کنیم
        # استفاده از .in_() باعث می‌شود دیتابیس فقط چند رکورد (مثلاً حداکثر ۱۵ تا) را برگرداند
        liked_posts_query = Like.query.filter(
            Like.user_id == current_user.id,
            Like.target_type == 'post',
            Like.target_id.in_(post_ids_on_page)
        ).with_entities(Like.target_id).all()

        liked_post_ids = {lp[0] for lp in liked_posts_query}

        # ج) (اختیاری) اگر در تمپلیت feed.html کامنت‌ها هم رندر می‌شوند، برای کامنت‌ها هم همین کار را می‌کنیم
        # اگر کامنت‌ها در فید اصلی نمایش داده نمی‌شوند، می‌توانید این بخش را حذف کنید تا سرعت بیشتر شود.
        # (فرض بر این است که ID کامنت‌های این پست‌ها را دارید، در غیر این صورت فقط liked_post_ids کافی است)
        # comment_ids_on_page = [comment.id for post in feed_posts.items for comment in post.comments]
        # liked_comments_query = Like.query.filter(
        #     Like.user_id == current_user.id,
        #     Like.target_type == 'comment',
        #     Like.target_id.in_(comment_ids_on_page)
        # ).with_entities(Like.target_id).all()
        # liked_comment_ids = {lc[0] for lc in liked_comments_query}

    # ۴. ارسال به تمپلیت
    return render_template(
        'users/feed.html',
        feed_posts=feed_posts,
        liked_post_ids=liked_post_ids,
        liked_comment_ids=liked_comment_ids
    )

@social_bp.route('/post/create', methods=['GET', 'POST'])
@login_required
@limiter.limit("5 per hour")
def create_post():
    """
    Create new post with media and tags support
    """
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        visibility = request.form.get('visibility', 'public')

        # دریافت فایل‌ها (نام فیلد در HTML باید name="media" باشد)
        media_files = request.files.getlist('media')

        # اصلاح: اگر هم متن خالی بود و هم فایلی آپلود نشده بود، خطا بده
        if not content and not (media_files and any(file.filename for file in media_files)):
            flash(_('social.post_content_empty'), 'error')
            return redirect(url_for('social.news_feed'))

        # پردازش فایل‌های آپلودی
        media = {'images': [], 'files': []}
        if media_files and any(file.filename for file in media_files):
            # فراخوانی تابع آپلود (مطمئن شوید این تابع همان نسخه امنیتی با UUID است که قبلاً فرستادم)
            media_urls = upload_social_media(media_files)

            # دسته‌بندی هوشمند بر اساس پسوند
            media = {
                'images': [url for url in media_urls if
                           url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))],
                'files': [url for url in media_urls if
                          not url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
            }

        # پردازش تگ محصولات و شرکت‌ها (دریافت به صورت لیست)
        tagged_products = request.form.getlist('tagged_products', type=int)
        tagged_companies = request.form.getlist('tagged_companies', type=int)

        # ساخت شیء پست
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


    # 🔥 این بخش برای حالت GET اضافه شد:
    from models import Product
    products = Product.query.all()  # لیست تمام محصولات
    # companies = Company.query.all()  # لیست تمام شرکت‌ها
    companies = []

    return render_template('users/create_post.html',  products=products,
        companies=companies)


@social_bp.route('/post/<int:post_id>')
def view_post(post_id):
    post = Post.query.get_or_404(post_id)

    # افزایش بازدید (آسنکرون)
    increment_post_views_async(post_id)

    comments = Comment.query.filter_by(
        post_id=post_id,
        is_deleted=False
    ).order_by(Comment.created_at.asc()).all()

    total_views = get_post_views(post_id)

    # ✅ منطق جدید برای ارسال وضعیت لایک‌ها به تمپلیت
    liked_post_ids = set()
    liked_comment_ids = set()

    if current_user.is_authenticated:
        from models.social import Like

        # ۱. بررسی لایک پست جاری
        liked_post = Like.query.filter_by(
            user_id=current_user.id,
            target_type='post',
            target_id=post_id
        ).first()
        if liked_post:
            liked_post_ids.add(post_id)

        # ۲. بررسی لایک کامنت‌های همین پست (بهینه‌شده با .in_)
        comment_ids = [c.id for c in comments]
        if comment_ids:
            liked_comments = Like.query.filter(
                Like.user_id == current_user.id,
                Like.target_type == 'comment',
                Like.target_id.in_(comment_ids)
            ).with_entities(Like.target_id).all()
            liked_comment_ids = {lc[0] for lc in liked_comments}

    return render_template('users/post_detail.html',
                           post=post,
                           comments=comments,
                           total_views=total_views,
                           liked_post_ids=liked_post_ids,  # ✅ ضروری برای _post_card.html
                           liked_comment_ids=liked_comment_ids)  # ✅ ضروری برای _comment_item.html

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
@limiter.limit("10/minute")
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
        User.role.in_(Role.get_core_roles())  # ✅ استفاده از تمام ۸ نقش اصلی به صورت پویا
    ).order_by(db.desc(User.trust_score_value)).limit(10).all() if hasattr(User, 'trust_score_value') else []

    following_ids = set()
    if current_user.is_authenticated:
        following_ids = set(f.following_id for f in Follow.query.filter_by(follower_id=current_user.id).all())

    return render_template('users/explore.html',
                           featured_posts=featured_posts,
                           suggested_users=suggested_users,
                           following_ids=following_ids)  # ارسال به قالب
# Share System Routes Added
