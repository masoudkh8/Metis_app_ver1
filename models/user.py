# models/user.py
# from flask_sqlalchemy import SQLAlchemy
from . import db
from flask_login import UserMixin
from enum import Enum
from datetime import datetime
import pytz
import json

tehran_tz = pytz.timezone('Asia/Tehran')


class Role(str,Enum):
    """8 Specialized User Roles Based on CONTEXT_MASTER_BRIEF"""
    PRODUCER = 'producer'              # Producer/Exporter
    BUYER = 'buyer'                    # Importer/Buyer
    BROKER = 'broker'                  # Commercial Broker
    CORPORATE_AGENT = 'corporate_agent' # Corporate Agent
    LOGISTICS = 'logistics'            # Logistics and Insurance Services
    LEGAL = 'legal'                    # Legal and Compliance Services
    TECH_PARTNER = 'tech_partner'      # Technology Partner
    INVESTOR = 'investor'              # Financial Investor
    ADMIN = 'admin'                    # System Management
    MODERATOR = 'moderator'            # Content Moderator
    
    @staticmethod
    def has_value(value):
        return value in [role.value for role in Role]
    
    @staticmethod
    def get_display_name(role_value):
        """Get Persian Display Name of Role"""
        display_names = {
            'producer': 'Producer/Exporter',
            'buyer': 'Importer/Buyer',
            'broker': 'Commercial Broker',
            'corporate_agent': 'Corporate Agent',
            'logistics': 'Logistics and Insurance Services',
            'legal': 'Legal and Compliance Services',
            'tech_partner': 'Technology Partner',
            'investor': 'Financial Investor',
            'admin': 'System Manager',
            'moderator': 'Content Moderator'
        }
        return display_names.get(role_value, role_value)
    
    @staticmethod
    def get_core_roles():
        """Get Core Business Roles (Without Admin and Moderator)"""
        return [role.value for role in Role if role.value not in ['admin', 'moderator']]


class UserProfile(db.Model):
    """Specialized User Profile with Fields Specific to Each Role"""
    __tablename__ = 'user_profile'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    
    # General Profile Information
    bio = db.Column(db.Text)  # Professional Biography
    website = db.Column(db.String(200))
    linkedin = db.Column(db.String(200))
    telegram = db.Column(db.String(100))
    whatsapp = db.Column(db.String(50))
    
    # Specialized Fields by Role
    # For Producer/Exporter
    production_capacity = db.Column(db.String(100))  # Production Capacity
    export_experience_years = db.Column(db.Integer)  # Years of Export Experience
    main_products = db.Column(db.Text)  # Main Products
    certifications = db.Column(db.Text)  # Certifications (ISO, HACCP, etc.)
    target_markets = db.Column(db.Text)  # Target Markets
    
    # For Buyer/Importer
    annual_import_volume = db.Column(db.String(100))  # Annual Import Volume
    main_categories = db.Column(db.Text)  # Main Required Categories
    preferred_payment_terms = db.Column(db.String(200))  # Preferred Payment Terms
    
    # For Broker
    specialization_sectors = db.Column(db.Text)  # Specialization Sectors
    broker_license_number = db.Column(db.String(50))  # Broker License Number
    commission_rate = db.Column(db.String(20))  # Commission Rate
    
    # For Corporate Agent
    company_position = db.Column(db.String(100))  # Position in Company
    authorization_level = db.Column(db.String(100))  # Authorization Level
    # parent_company_id commented out until Company model is created
    # parent_company_id = db.Column(db.Integer, db.ForeignKey('company.id'))  # Parent Company
    
    # For Logistics & Insurance
    service_types = db.Column(db.Text)  # Service Types (Sea, Air, Land Transport, Insurance)
    coverage_regions = db.Column(db.Text)  # Coverage Regions
    insurance_license = db.Column(db.String(50))  # Insurance License
    fleet_size = db.Column(db.String(50))  # Fleet Size
    
    # For Legal & Compliance
    practice_areas = db.Column(db.Text)  # Practice Areas (Customs, Contracts, Arbitration)
    bar_association_number = db.Column(db.String(50))  # Bar Association Number
    years_of_practice = db.Column(db.Integer)  # Years of Practice
    
    # For Tech Partner
    tech_specialties = db.Column(db.Text)  # Technical Specialties (ERP, CRM, AI, Blockchain)
    portfolio_url = db.Column(db.String(200))  # Portfolio URL
    service_packages = db.Column(db.Text)  # Service Packages
    
    # For Investor
    investment_capacity = db.Column(db.String(100))  # Investment Capacity
    preferred_sectors = db.Column(db.Text)  # Preferred Sectors for Investment
    investment_type = db.Column(db.String(100))  # Investment Type (VC, Angel, Project-based)
    risk_tolerance = db.Column(db.String(50))  # Risk Tolerance Level
    
    # Statuses
    is_verified = db.Column(db.Boolean, default=False)  # Identity Verification Completed
    verification_date = db.Column(db.DateTime)
    is_premium = db.Column(db.Boolean, default=False)
    premium_since = db.Column(db.DateTime)
    trust_score_override = db.Column(db.Integer)  # Manual Trust Score (For Admin)
    
    # === Custom Permissions System ===
    # This field allows you to set user permissions in a granular way
    # If NULL or empty, default role permissions will be used
    # Format: JSON Array of Permission strings (e.g., ["order.view", "logistics.update_status"])
    custom_permissions = db.Column(db.Text, nullable=True)  # JSON format
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='profile')

    # # رابطه با مدل Follow (برای دسترسی به لیست فالوورها و فالوینگ‌ها)
    # following_relations = db.relationship('Follow', foreign_keys='Follow.follower_id', back_populates='follower', cascade='all, delete-orphan')
    # followers_relations = db.relationship('Follow', foreign_keys='Follow.following_id', back_populates='following', cascade='all, delete-orphan')
    # company relationship will be established when Company model is created
    # documents and endorsements can be added as separate models if needed
    
    def get_custom_permissions(self):
        """
        Get List of Custom Permissions as List of Strings
        If profile doesn't exist or custom_permissions is empty, returns empty list
        """
        if not self.custom_permissions:
            return []
        try:
            if isinstance(self.custom_permissions, str):
                perms = json.loads(self.custom_permissions)
                return perms if isinstance(perms, list) else []
            elif isinstance(self.custom_permissions, list):
                return self.custom_permissions
            else:
                return []
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_custom_permissions(self, permissions_list):
        """
        Set Custom Permissions as List of Permission Value Strings
        Args:
            permissions_list: List of strings like ['order.view', 'logistics.update_status']
        """
        if not permissions_list or len(permissions_list) == 0:
            self.custom_permissions = None
        else:
            # Ensure only valid strings are stored
            valid_perms = [str(p) for p in permissions_list if p]
            self.custom_permissions = json.dumps(valid_perms, ensure_ascii=False)
    
    def add_permission(self, permission_value):
        """
        Add a Permission to Custom Permissions
        Args:
            permission_value: Permission string like 'order.view'
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            current_perms = self.get_custom_permissions()
            if permission_value not in current_perms:
                current_perms.append(permission_value)
                self.set_custom_permissions(current_perms)
                return True
            return False
        except Exception:
            return False
    
    def remove_permission(self, permission_value):
        """
        Remove a Permission from Custom Permissions
        Args:
            permission_value: Permission string like 'order.view'
        Returns:
            bool: True if permission was removed, False if it didn't exist
        """
        try:
            current_perms = self.get_custom_permissions()
            if permission_value in current_perms:
                current_perms.remove(permission_value)
                self.set_custom_permissions(current_perms)
                return True
            return False
        except Exception:
            return False
    
    def has_permission(self, permission_value):
        """
        Check Existence of a Permission in Custom Permissions
        Args:
            permission_value: Permission string like 'order.view'
        Returns:
            bool: True if permission exists
        """
        return permission_value in self.get_custom_permissions()


# Intermediate Table for Connections (Follow System) - Must be defined before User class
connections = db.Table('connections',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=db.func.now()),
    db.Column('connection_type', db.String(20), default='follow') # follow, connect, partner
)


class MembershipTier(str,Enum):
    """Elite Club Access Layers (Concentric Circles Model)"""
    OBSERVER = 'observer'          # Layer 1: Visitor (Newcomer, Unverified)
    VERIFIED = 'verified'          # Layer 2: Verified Member (KYC Completed, Basic Membership)
    PARTNER = 'partner'            # Layer 3: Strategic Partner (TrustScore > 70, Invitation or High Performance)
    ELITE = 'elite'                # Layer 4: Elite (Exclusive Invitation, TrustScore > 90, Board Approval)
    
    @staticmethod
    def get_display_name(tier_value):
        """Get Persian Display Name of Layer"""
        display_names = {
            'observer': 'Visitor',
            'verified': 'Verified Member',
            'partner': 'Strategic Partner',
            'elite': 'Elite'
        }
        return display_names.get(tier_value, tier_value)
    
    @staticmethod
    def get_hierarchy_level(tier_value):
        """Get Hierarchical Level for Comparison"""
        hierarchy = {
            'observer': 0,
            'verified': 1,
            'partner': 2,
            'elite': 3
        }
        return hierarchy.get(tier_value, 0)


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    # ✅ حالت جدید (استفاده از String):
    role = db.Column(db.String(50), nullable=False)
    membership_tier = db.Column(db.String(50), default='observer', nullable=False, index=True)


    # Invitation System (Exclusive Entry)
    invite_code = db.Column(db.String(32), unique=True, index=True, nullable=True)  # User's own invite code
    invited_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Who invited?
    invited_by = db.relationship('User', remote_side=[id], backref='invitees', foreign_keys=[invited_by_id])
    
    # Trust Score (Key to Layer Upgrade)
    trust_score_value = db.Column(db.Integer, default=50, nullable=False, index=True)  # ✅ Initial Score 50
    
    # Authentication Status (Condition for Entry to Layer 2)
    is_kyc_verified = db.Column(db.Boolean, default=False, nullable=False)
    kyc_documents_url = db.Column(db.String(255), nullable=True)
    
    # === Specialized Profile Fields (Request 1) ===
    expertise_area = db.Column(db.String(200))  # Area of Expertise for Professionals
    job_title = db.Column(db.String(100))  # Job Title
    bio = db.Column(db.Text)  # About Me / Professional Biography
    website = db.Column(db.String(200))  # Personal/Company Website
    social_links = db.Column(db.Text)  # Social Links (JSON format)
    
    # Identity Verification Status (Request 1)
    is_verified = db.Column(db.Boolean, default=False)  # ✅ Identity Verification Completed
    verification_documents = db.Column(db.Text)  # Identity Verification Documents (JSON format)
    
    # === Security and Authentication Fields ===
    # Avatar/Profile Picture
    avatar_filename = db.Column(db.String(255), nullable=True)  # Profile Picture Filename
    
    # Two-Factor Authentication (2FA)
    two_factor_enabled = db.Column(db.Boolean, default=False, nullable=False)
    two_factor_secret = db.Column(db.String(32), nullable=True)  # رمز的秘密 برای TOTP
    backup_codes = db.Column(db.Text, nullable=True)  # کدهای پشتیبان (JSON format)
    
    # Account Lockout
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)  # زمان قفل بودن حساب
    
    # Password History (برای جلوگیری از استفاده مجدد)
    password_history = db.Column(db.Text, nullable=True)  # JSON array of previous password hashes
    
    # Email Verification
    is_email_verified = db.Column(db.Boolean, default=False, nullable=False)
    email_verification_token = db.Column(db.String(255), nullable=True)

    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    # ===================================




    # Dark Mode Preference (stored in backend)
    dark_mode_preference = db.Column(db.String(20), default='system', nullable=False)  # 'light', 'dark', 'system'
    
    # Notification Preferences (JSON)
    notification_preferences = db.Column(db.Text, nullable=True)  # JSON settings for notifications
    
    # Privacy Settings (JSON)
    privacy_settings = db.Column(db.Text, nullable=True)  # JSON settings for privacy
    
    # تاریخچه
    last_login = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    notifications = db.relationship('Notification', 
                                   foreign_keys='Notification.user_id',
                                   back_populates='user', 
                                   lazy='dynamic',
                                   cascade='all, delete-orphan')

    company_name = db.Column(db.String(100))
    country = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)  # ✅ فعال/غیرفعال
    is_premium = db.Column(db.Boolean, default=False)
    premium_since = db.Column(db.DateTime, default=None)
    premium_requests = db.relationship('PremiumRequest', back_populates='user', cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    # New relationships for 16-section platform
    profile = db.relationship('UserProfile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    trust_score = db.relationship('TrustScore', back_populates='user', uselist=False, cascade='all, delete-orphan')
    badges = db.relationship('UserBadge', back_populates='user', cascade='all, delete-orphan')
    progress = db.relationship('UserProgress', back_populates='user', uselist=False, cascade='all, delete-orphan')
    credit_account = db.relationship('TradeCreditAccount', back_populates='user', uselist=False, cascade='all, delete-orphan')

    # ✅ روابط اجتماعی (Follow System) - باید دقیقاً داخل کلاس User باشند
    followed = db.relationship('Follow', foreign_keys='Follow.follower_id', back_populates='follower',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys='Follow.following_id', back_populates='following',
                                cascade='all, delete-orphan')
    # رابطه پست‌ها (چون در social.py به آن اشاره شده است)
    posts = db.relationship('Post', back_populates='author', cascade='all, delete-orphan', lazy='dynamic')

    # روابط اجتماعی (Follow System) - استفاده از مدل Follow از social.py
    # relationshipهای follow/followers در models/social.py به User اضافه می‌شوند
    # اینجا فقط برای سازگاری با کدهای قدیمی تعریف شده
    
    # پست‌ها - relationship در models/social.py تعریف شده است
    # برای جلوگیری از تداخل، اینجا تعریف نمی‌کنیم

  
    @property
    def unread_notifications_count(self):
        return self.notifications.filter_by(user_id=self.id, is_read=False).count()
    
    @property
    def role_display_name(self):
        """Get Persian display name of user role"""
        return Role.get_display_name(self.role.value) if self.role else None
    
    @property
    def tier_display_name(self):
        """Get Persian display name of membership tier"""
        return MembershipTier.get_display_name(self.membership_tier.value) if self.membership_tier else 'Visitor'
    
    @property
    def is_core_member(self):
        """Is the user among the core members of the elite club?"""
        return self.role.value in Role.get_core_roles() if self.role else False
    
    @property
    def is_admin_or_moderator(self):
        """Does the user have administrative access?"""
        return self.role.value in ['admin', 'moderator'] if self.role else False
    
    def can_access_tier(self, required_tier: MembershipTier) -> bool:
        """Smart access check based on club tier"""
        if not self.membership_tier or not required_tier:
            return False
        return MembershipTier.get_hierarchy_level(self.membership_tier.value) >= MembershipTier.get_hierarchy_level(required_tier.value)
    
    def generate_invite_code(self):
        """Generate unique invite code"""
        import secrets
        if not self.invite_code:
            self.invite_code = f"{self.username.upper()[:4]}-{secrets.token_hex(4)}"
        return self.invite_code

    # در فایل models/user.py، داخل کلاس User، این سه متد را جایگزین متدهای قدیمی کنید:

    def follow(self, user):
        """دنبال کردن یک کاربر"""
        from .social import Follow
        target_id = user.id if hasattr(user, 'id') else user

        if self.id != target_id and not Follow.is_following(self.id, target_id):
            new_follow = Follow(follower_id=self.id, following_id=target_id)
            db.session.add(new_follow)
            db.session.commit()

    def unfollow(self, user):
        """لغو دنبال کردن یک کاربر"""
        from .social import Follow
        target_id = user.id if hasattr(user, 'id') else user

        follow_record = Follow.query.filter_by(
            follower_id=self.id,
            following_id=target_id
        ).first()

        if follow_record:
            db.session.delete(follow_record)
            db.session.commit()

    def is_following(self, user):
        """بررسی اینکه آیا این کاربر، کاربر دیگر را دنبال می‌کند یا خیر"""
        from .social import Follow
        target_id = user.id if hasattr(user, 'id') else user

        if target_id == self.id:
            return False

        # استفاده از متد کلاس Follow که از تداخل جلوگیری می‌کند
        return Follow.is_following(self.id, target_id)
    def get_public_profile_url(self):
        """Get Public Profile URL"""
        return f"/user/{self.username}"
    
    def to_dict(self):
        """Convert to Dictionary for API"""
        import json
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.value,
            'role_display': self.role_display_name,
            'tier': self.membership_tier.value if self.membership_tier else 'observer',
            'tier_display': self.tier_display_name,
            'trust_score': self.trust_score_value,
            'is_verified': self.is_verified or self.is_kyc_verified,
            'company_name': self.company_name,
            'country': self.country,
            'invite_code': self.invite_code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            # New specialized fields
            'expertise_area': self.expertise_area,
            'job_title': self.job_title,
            'bio': self.bio,
            'website': self.website,
            'social_links': json.loads(self.social_links) if self.social_links else {},
            'verification_documents': json.loads(self.verification_documents) if self.verification_documents else []
        }
    
    def set_password(self, password):
        """Set Password with Hashing"""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check Password"""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User {self.username} ({self.role.value}) [{self.membership_tier.value}]>"
