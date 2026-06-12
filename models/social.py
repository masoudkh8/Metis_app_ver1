# models/social.py
"""
ماژول شبکه اجتماعی متیسما
شامل: پست‌ها، فالو/کانکشن، لایک، کامنت
"""
from . import db
from datetime import datetime
from sqlalchemy import text


class Follow(db.Model):
    """
    سیستم دنبال کردن کاربران (Graph/Connections)
    کاربر A کاربر B را دنبال می‌کند
    """
    __tablename__ = 'follow'
    
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    following_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # سطح دسترسی: public فقط پست‌های عمومی، connection دسترسی کامل‌تر
    connection_type = db.Column(db.String(20), default='public')  # public, connection, premium
    
    # جلوگیری از فالو تکراری
    __table_args__ = (
        db.UniqueConstraint('follower_id', 'following_id', name='uq_follow_user_pair'),
    )
    
    # Relationships
    follower = db.relationship('User', foreign_keys=[follower_id], back_populates='followed')
    following = db.relationship('User', foreign_keys=[following_id], back_populates='followers')
    
    def __repr__(self):
        return f"<Follow {self.follower_id} -> {self.following_id}>"
    
    @classmethod
    def is_following(cls, follower_id, following_id):
        """بررسی اینکه آیا کاربر A کاربر B را دنبال می‌کند"""
        return cls.query.filter_by(
            follower_id=follower_id,
            following_id=following_id
        ).first() is not None
    
    @classmethod
    def get_followers_count(cls, user_id):
        """تعداد دنبال‌کنندگان یک کاربر"""
        return cls.query.filter_by(following_id=user_id).count()
    
    @classmethod
    def get_following_count(cls, user_id):
        """تعداد افرادی که کاربر دنبال می‌کند"""
        return cls.query.filter_by(follower_id=user_id).count()


class Post(db.Model):
    """
    پست‌های فید اخبار (The Feed)
    قلب تپنده شبکه اجتماعی
    """
    __tablename__ = 'post'
    
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    # محتوا
    content = db.Column(db.Text, nullable=False)  # متن پست
    visibility = db.Column(db.String(20), default='public')  # public, followers_only, private
    
    # رسانه‌ها (JSON برای ذخیره لیست فایل‌ها)
    # مثال: {"images": ["url1", "url2"], "files": ["file1.pdf"]}
    media = db.Column(db.JSON, default=dict)
    
    # تگ‌کردن محصولات یا شرکت‌ها
    tagged_products = db.Column(db.JSON, default=list)  # لیست product_ids
    tagged_companies = db.Column(db.JSON, default=list)  # لیست company_ids
    
    # آمار تعاملات (برای بهینه‌سازی، از Redis هم می‌توان استفاده کرد)
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    shares_count = db.Column(db.Integer, default=0)
    views_count = db.Column(db.Integer, default=0)
    
    # وضعیت
    is_pinned = db.Column(db.Boolean, default=False)  # سنجاق شده توسط ادمین
    is_featured = db.Column(db.Boolean, default=False)  # پست برگزیده پلتفرم
    is_edited = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author = db.relationship('User', back_populates='posts')
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan', lazy='dynamic')
    # likes relationship حذف شد چون در مدل Like با primaryjoin سفارشی تعریف شده است
    
    def __repr__(self):
        return f"<Post {self.id} by {self.author_id}>"
    
    def to_dict(self, include_author=True):
        """تبدیل پست به دیکشنری برای API"""
        data = {
            'id': self.id,
            'content': self.content,
            'visibility': self.visibility,
            'media': self.media or {},
            'tagged_products': self.tagged_products or [],
            'tagged_companies': self.tagged_companies or [],
            'likes_count': self.likes_count,
            'comments_count': self.comments_count,
            'shares_count': self.shares_count,
            'views_count': self.views_count,
            'is_pinned': self.is_pinned,
            'is_featured': self.is_featured,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_author and self.author:
            data['author'] = {
                'id': self.author.id,
                'username': self.author.username,
                'company_name': self.author.company_name,
                'role': self.author.role.value if self.author.role else None,
                'role_display': self.author.role_display_name,
            }
            
            # اضافه کردن اطلاعات پروفایل اگر موجود باشد
            if hasattr(self.author, 'profile') and self.author.profile:
                profile = self.author.profile
                data['author']['bio'] = profile.bio
                data['author']['website'] = profile.website
        
        return data
    
    @classmethod
    def get_feed_for_user(cls, user_id, limit=50, include_featured=True):
        """
        دریافت فید اخبار برای یک کاربر
        الگوریتم ساده: پست‌های کسانی که فالو کرده + پست‌های برگزیده
        """
        # کوئری برای پیدا کردن کاربرانی که این کاربر دنبال می‌کند
        following_subquery = db.session.query(Follow.following_id).filter_by(
            follower_id=user_id
        ).subquery()
        
        # پست‌های کاربران فالو شده
        followed_posts = cls.query.filter(
            cls.author_id.in_(following_subquery),
            cls.visibility.in_(['public', 'followers_only'])
        )
        
        # پست‌های برگزیده پلتفرم
        if include_featured:
            featured_posts = cls.query.filter_by(is_featured=True, visibility='public')
            # ترکیب دو کوئری (با حذف تکراری‌ها)
            all_posts = followed_posts.union(featured_posts)
        else:
            all_posts = followed_posts
        
        # مرتب‌سازی بر اساس زمان (جدیدترین اول)
        return all_posts.order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_public_posts(cls, limit=50):
        """دریافت پست‌های عمومی برای نمایش در پروفایل عمومی"""
        return cls.query.filter_by(visibility='public').order_by(
            cls.created_at.desc()
        ).limit(limit).all()


class Comment(db.Model):
    """
    کامنت‌های پست‌ها (Engagement)
    """
    __tablename__ = 'comment'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)  # برای پاسخ به کامنت‌ها
    
    content = db.Column(db.Text, nullable=False)
    
    # آمار
    likes_count = db.Column(db.Integer, default=0)
    
    # وضعیت
    is_edited = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)  # نرم‌دیلیت برای حفظ زنجیره مکالمه
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    post = db.relationship('Post', back_populates='comments')
    author = db.relationship('User', backref='comments')
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Comment {self.id} on Post {self.post_id}>"
    
    def to_dict(self, include_author=True):
        """تبدیل کامنت به دیکشنری"""
        data = {
            'id': self.id,
            'post_id': self.post_id,
            'parent_id': self.parent_id,
            'content': self.content,
            'likes_count': self.likes_count,
            'is_edited': self.is_edited,
            'is_deleted': self.is_deleted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'replies_count': len(self.replies) if self.replies else 0,
        }
        
        if include_author and self.author:
            data['author'] = {
                'id': self.author.id,
                'username': self.author.username,
                'company_name': self.author.company_name,
                'role': self.author.role.value if self.author.role else None,
            }
        
        return data


class Like(db.Model):
    """
    لایک پست‌ها و کامنت‌ها (Engagement)
    استفاده از JSON برای پشتیبانی از لایک هم پست و هم کامنت
    """
    __tablename__ = 'like'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    # نوع آیتم مورد لایک: 'post' یا 'comment'
    target_type = db.Column(db.String(20), nullable=False)  # 'post' یا 'comment'
    target_id = db.Column(db.Integer, nullable=False, index=True)  # post_id یا comment_id
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # جلوگیری از لایک تکراری
    __table_args__ = (
        db.UniqueConstraint('user_id', 'target_type', 'target_id', name='uq_like_user_target'),
    )
    
    # Relationships
    user = db.relationship('User', backref='likes')
    # post relationship با primaryjoin سفارشی برای پلی‌مورفیک
    post = db.relationship('Post', 
                          primaryjoin="and_(Like.target_type=='post', Like.target_id==Post.id)",
                          foreign_keys=[target_id],
                          viewonly=True)
    
    def __repr__(self):
        return f"<Like {self.user_id} on {self.target_type}:{self.target_id}>"
    
    @classmethod
    def is_liked(cls, user_id, target_type, target_id):
        """بررسی اینکه آیا کاربر آیتم را لایک کرده است"""
        return cls.query.filter_by(
            user_id=user_id,
            target_type=target_type,
            target_id=target_id
        ).first() is not None
    
    @classmethod
    def get_likes_count(cls, target_type, target_id):
        """تعداد لایک‌های یک آیتم"""
        return cls.query.filter_by(
            target_type=target_type,
            target_id=target_id
        ).count()


# Helper functions
def create_sample_posts(admin_user, sample_data):
    """
    ایجاد پست‌های نمونه برای پر کردن اولیه پلتفرم
    استراتژی محتوای اولیه از CONTEXT_MASTER_BRIEF
    """
    posts = []
    for data in sample_data:
        post = Post(
            author_id=admin_user.id,
            content=data['content'],
            visibility='public',
            is_featured=data.get('is_featured', False),
            media=data.get('media', {}),
            tagged_companies=data.get('tagged_companies', [])
        )
        db.session.add(post)
        posts.append(post)
    
    db.session.commit()
    return posts
