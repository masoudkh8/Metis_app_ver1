"""
Metisma Exhibition Hall Models
=================================
Online Exhibition Data Models for Metisma

Includes:
- Exhibition management
- Virtual booths
- Visits and interactions
- Appointments

Version: 1.0.0
"""

from datetime import datetime
try:
    from sqlalchemy.dialects.postgresql import JSONB, UUID
    POSTGRES_AVAILABLE = True
except ImportError:
    from sqlalchemy import JSON as JSONB
    import uuid as uuid_module
    POSTGRES_AVAILABLE = False
import uuid

# Use the main db instance from models
from models import db

# Helper for UUID type compatibility
UUID_TYPE = UUID(as_uuid=True) if POSTGRES_AVAILABLE else db.String(36)
STRING_UUID_TYPE = db.String(36)  # For foreign keys to UUIDs when not using postgres


# =============================================================================
# ENUM Tables
# =============================================================================

class ExhibitionStatus(db.Model):
    """Exhibition status types"""
    __tablename__ = 'exhibition_status_enum'
    
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return f"<ExhibitionStatus {self.status}>"


class BoothType(db.Model):
    """Booth type categories"""
    __tablename__ = 'booth_type_enum'
    
    id = db.Column(db.Integer, primary_key=True)
    booth_type = db.Column(db.String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return f"<BoothType {self.booth_type}>"


# =============================================================================
# EXHIBITION MODELS
# =============================================================================

class Exhibition(db.Model):
    """
    Main exhibition entity
    Each exhibition can have multiple booths
    """
    __tablename__ = 'exhibitions'
    
    id = db.Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    title_fa = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200), nullable=False)
    description_fa = db.Column(db.Text)
    description_en = db.Column(db.Text)
    
    # Timing
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    timezone = db.Column(db.String(50), default='Asia/Tehran')
    
    # Status
    status_id = db.Column(db.Integer, db.ForeignKey('exhibition_status_enum.id'), 
                         default=1)
    status = db.relationship('ExhibitionStatus', backref='exhibitions')
    
    # Display settings
    banner_url = db.Column(db.String(500))
    thumbnail_url = db.Column(db.String(500))
    theme_color = db.Column(db.String(7), default='#1a56db')
    
    # Features
    has_virtual_tour = db.Column(db.Boolean, default=False)
    has_3d_booths = db.Column(db.Boolean, default=False)
    has_live_chat = db.Column(db.Boolean, default=True)
    has_video_conference = db.Column(db.Boolean, default=False)
    
    # Statistics
    total_booths = db.Column(db.Integer, default=0)
    total_visitors = db.Column(db.Integer, default=0)
    total_interactions = db.Column(db.Integer, default=0)
    
    # Metadata
    settings = db.Column(db.JSON, default={})
    seo_metadata = db.Column(db.JSON, default={})
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    booths = db.relationship('Booth', backref='exhibition', lazy='dynamic', cascade='all, delete-orphan')
    visits = db.relationship('ExhibitionVisit', backref='exhibition', lazy='dynamic')
    
    __table_args__ = (
        db.Index('idx_exhibitions_status', 'status_id'),
        db.Index('idx_exhibitions_dates', 'start_date', 'end_date'),
    )
    
    def __repr__(self):
        return f"<Exhibition {self.title_fa}>"


class Booth(db.Model):
    """
    Exhibition booth entity
    Can be standard, premium, or 3D booth
    """
    __tablename__ = 'booths'
    
    id = db.Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    exhibition_id = db.Column(UUID_TYPE, db.ForeignKey('exhibitions.id'), nullable=False)
    
    # Owner information (Polymorphic)
    owner_type = db.Column(db.String(50), nullable=False)  # company, user, brand
    owner_id = db.Column(STRING_UUID_TYPE, nullable=False)
    
    # Booth details
    booth_number = db.Column(db.String(20), nullable=False)
    title_fa = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200), nullable=False)
    description_fa = db.Column(db.Text)
    description_en = db.Column(db.Text)
    
    # Type and location
    type_id = db.Column(db.Integer, db.ForeignKey('booth_type_enum.id'), default=1)
    booth_type = db.relationship('BoothType', backref='booths')
    
    location_x = db.Column(db.Integer, default=0)
    location_y = db.Column(db.Integer, default=0)
    floor_plan = db.Column(db.String(50))
    
    # Multimedia content
    gallery_images = db.Column(db.JSON, default=[])
    video_urls = db.Column(db.JSON, default=[])
    brochure_url = db.Column(db.String(500))
    
    # 3D model
    model_3d_url = db.Column(db.String(500))
    model_3d_config = db.Column(db.JSON, default={})
    
    # Products/Services
    featured_products = db.Column(db.JSON, default=[])
    services_offered = db.Column(db.JSON, default=[])
    
    # Interactions
    contact_info = db.Column(db.JSON, default={})
    chat_enabled = db.Column(db.Boolean, default=True)
    appointment_enabled = db.Column(db.Boolean, default=True)
    
    # Statistics
    view_count = db.Column(db.Integer, default=0)
    interaction_count = db.Column(db.Integer, default=0)
    lead_count = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    approval_status = db.Column(db.String(50), default='pending')
    
    # SEO
    slug = db.Column(db.String(200), unique=True, nullable=False)
    seo_metadata = db.Column(db.JSON, default={})
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    visits = db.relationship('BoothVisit', backref='booth', lazy='dynamic')
    interactions = db.relationship('BoothInteraction', backref='booth', lazy='dynamic')
    appointments = db.relationship('BoothAppointment', backref='booth', lazy='dynamic')
    
    __table_args__ = (
        db.Index('idx_booths_exhibition', 'exhibition_id'),
        db.Index('idx_booths_owner', 'owner_type', 'owner_id'),
        db.Index('idx_booths_location', 'location_x', 'location_y'),
        db.Index('idx_booths_slug', 'slug', unique=True),
    )
    
    def __repr__(self):
        return f"<Booth {self.booth_number} - {self.title_fa}>"


class BoothVisit(db.Model):
    """Booth visit registration"""
    __tablename__ = 'booth_visits'
    
    id = db.Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    booth_id = db.Column(UUID_TYPE, db.ForeignKey('booths.id'), nullable=False)
    
    visitor_type = db.Column(db.String(50), nullable=False)
    visitor_id = db.Column(UUID_TYPE)
    
    session_id = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    
    duration_seconds = db.Column(db.Integer, default=0)
    pages_viewed = db.Column(db.Integer, default=1)
    
    entry_point = db.Column(db.String(100))
    referrer_url = db.Column(db.String(500))
    
    visited_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    interaction_data = db.Column(db.JSON, default={})
    
    __table_args__ = (
        db.Index('idx_booth_visits_booth', 'booth_id'),
        db.Index('idx_booth_visits_visitor', 'visitor_type', 'visitor_id'),
        db.Index('idx_booth_visits_time', 'visited_at'),
    )
    
    def __repr__(self):
        return f"<BoothVisit {self.id} - Booth: {self.booth_id}>"


class BoothInteraction(db.Model):
    """User interactions with booth"""
    __tablename__ = 'booth_interactions'
    
    id = db.Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    booth_id = db.Column(UUID_TYPE, db.ForeignKey('booths.id'), nullable=False)
    
    user_id = db.Column(UUID_TYPE, nullable=False)
    interaction_type = db.Column(db.String(50), nullable=False)  # message, inquiry, callback_request
    
    content = db.Column(db.JSON, default={})
    status = db.Column(db.String(50), default='pending')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime)
    
    __table_args__ = (
        db.Index('idx_booth_interactions_booth', 'booth_id'),
        db.Index('idx_booth_interactions_user', 'user_id'),
        db.Index('idx_booth_interactions_type', 'interaction_type'),
    )
    
    def __repr__(self):
        return f"<BoothInteraction {self.interaction_type} - User: {self.user_id}>"


class BoothAppointment(db.Model):
    """Booth appointment scheduling"""
    __tablename__ = 'booth_appointments'
    
    id = db.Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    booth_id = db.Column(UUID_TYPE, db.ForeignKey('booths.id'), nullable=False)
    
    requester_id = db.Column(UUID_TYPE, nullable=False)
    host_id = db.Column(UUID_TYPE, nullable=False)
    
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    scheduled_time = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=30)
    
    meeting_type = db.Column(db.String(50), default='video')  # video, voice, text
    meeting_link = db.Column(db.String(500))
    meeting_password = db.Column(db.String(50))
    
    status = db.Column(db.String(50), default='scheduled')  # scheduled, completed, cancelled, no-show
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_booth_appointments_booth', 'booth_id'),
        db.Index('idx_booth_appointments_time', 'scheduled_time'),
        db.Index('idx_booth_appointments_status', 'status'),
    )
    
    def __repr__(self):
        return f"<BoothAppointment {self.scheduled_time} - {self.title}>"


class ExhibitionVisit(db.Model):
    """General exhibition visit tracking"""
    __tablename__ = 'exhibition_visits'
    
    id = db.Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    exhibition_id = db.Column(UUID_TYPE, db.ForeignKey('exhibitions.id'), nullable=False)
    
    visitor_type = db.Column(db.String(50), nullable=False)
    visitor_id = db.Column(UUID_TYPE)
    
    session_id = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(45))
    
    entry_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    exit_time = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Integer, default=0)
    
    booths_visited = db.Column(db.Integer, default=0)
    device_info = db.Column(db.JSON, default={})
    
    __table_args__ = (
        db.Index('idx_exhibition_visits_exhibition', 'exhibition_id'),
        db.Index('idx_exhibition_visits_time', 'entry_time'),
    )
    
    def __repr__(self):
        return f"<ExhibitionVisit {self.entry_time} - Exhibition: {self.exhibition_id}>"


# =============================================================================
# Helper Functions
# =============================================================================

def init_exhibition_db(app=None):
    """
    Initialize exhibition database
    Create default ENUM values
    """
    if app:
        db.init_app(app)
    
    # Create exhibition statuses
    exhibition_statuses = ['draft', 'upcoming', 'active', 'paused', 'completed', 'cancelled']
    for status in exhibition_statuses:
        existing = ExhibitionStatus.query.filter_by(status=status).first()
        if not existing:
            db.session.add(ExhibitionStatus(status=status))
    
    # Create booth types
    booth_types = ['standard', 'premium', 'vip', '3d', 'interactive']
    for btype in booth_types:
        existing = BoothType.query.filter_by(booth_type=btype).first()
        if not existing:
            db.session.add(BoothType(booth_type=btype))
    
    db.session.commit()
