# models/gamification.py
"""
Section 3: Trust & Professional Gamification System (Trust & Gamification)
- Dynamic Scoring Engine
- Badges (Badges)
- Seasonal Challenges
- Personal Progress
"""
from . import db
from datetime import datetime
import pytz

tehran_tz = pytz.timezone('Asia/Tehran')


class UserBadge(db.Model):
    """User Badges"""
    __tablename__ = 'user_badges'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    badge_type = db.Column(db.String(50), nullable=False)  # e.g., 'export_expert', 'top_seller'
    badge_name = db.Column(db.String(100), nullable=False)  # e.g., 'Export Expert to Oman'
    badge_icon = db.Column(db.String(20))  # emoji or icon name
    earned_at = db.Column(db.DateTime, default=lambda: datetime.now(tehran_tz))
    description = db.Column(db.Text)
    
    # Relationship
    user = db.relationship('User', back_populates='badges')


class UserProgress(db.Model):
    """User Personal Progress Dashboard"""
    __tablename__ = 'user_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    
    # Total Gamification Score
    total_points = db.Column(db.Integer, default=0)
    
    # User Level (Level)
    level = db.Column(db.Integer, default=1)
    
    # Progress to Next Level (0-100 percent)
    progress_to_next_level = db.Column(db.Integer, default=0)
    
    # Activity Statistics
    completed_profile = db.Column(db.Boolean, default=False)
    successful_trades = db.Column(db.Integer, default=0)
    content_created = db.Column(db.Integer, default=0)  # Number of Useful Content
    referrals = db.Column(db.Integer, default=0)  # Number of Successful Referrals
    
    # Last Activity
    last_activity = db.Column(db.DateTime, default=lambda: datetime.now(tehran_tz))
    
    # Relationship
    user = db.relationship('User', back_populates='progress')
    
    def calculate_level(self):
        """Calculate Level Based on Total Score"""
        # Simple Formula: Every 1000 points = 1 level
        self.level = (self.total_points // 1000) + 1
        return self.level
    
    def get_next_actions(self):
        """Suggest 3 Next Actions for Upgrade"""
        actions = []
        if not self.completed_profile:
            actions.append("Complete Company Profile (+200 points)")
        if self.successful_trades is None or self.successful_trades < 5:
            actions.append("Complete First Successful Trade (+500 points)")
        if self.content_created is None or self.content_created < 3:
            actions.append("Share Specialized Content (+100 points)")
        if self.referrals is None or self.referrals < 2:
            actions.append("Refer Business Partner (+150 points)")
        return actions[:3]


class SeasonalChallenge(db.Model):
    """Seasonal Challenges with Tangible Rewards"""
    __tablename__ = 'seasonal_challenges'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    reward_type = db.Column(db.String(50))  # e.g., 'discount', 'priority', 'credit'
    reward_value = db.Column(db.String(100))  # e.g., '20% off logistics'
    is_active = db.Column(db.Boolean, default=True)
    
    # Participants
    participants = db.relationship('ChallengeParticipant', back_populates='challenge', cascade='all, delete-orphan')


class ChallengeParticipant(db.Model):
    """Participants in Seasonal Challenges"""
    __tablename__ = 'challenge_participants'
    
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('seasonal_challenges.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    progress = db.Column(db.Integer, default=0)  # Progress Percentage
    completed = db.Column(db.Boolean, default=False)
    reward_claimed = db.Column(db.Boolean, default=False)
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(tehran_tz))
    
    # Relationships
    challenge = db.relationship('SeasonalChallenge', back_populates='participants')
    user = db.relationship('User', backref='challenge_participations')
