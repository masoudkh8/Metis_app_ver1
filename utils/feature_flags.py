"""
Feature Flag Management System for TradeGlobal Platform

This module provides a comprehensive feature flag system with:
- Database-backed feature flags
- User targeting (by ID, role, percentage)
- A/B testing support
- Environment-specific flags
- Audit logging
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from flask import current_app, g
from models import db


class FeatureFlag(db.Model):
    """Feature Flag Model"""
    
    __tablename__ = 'feature_flags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    enabled = db.Column(db.Boolean, default=False)
    
    # Targeting options
    enabled_for_all = db.Column(db.Boolean, default=False)  # If True, enabled for everyone
    enabled_for_roles = db.Column(db.JSON, default=list)  # List of roles
    enabled_for_user_ids = db.Column(db.JSON, default=list)  # List of user IDs
    rollout_percentage = db.Column(db.Integer, default=0)  # 0-100
    
    # Environment specific
    environments = db.Column(db.JSON, default=lambda: ['development', 'testing', 'production'])
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100))
    
    # Audit
    audit_log = db.relationship('FeatureFlagAudit', backref='flag', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'enabled': self.enabled,
            'enabled_for_all': self.enabled_for_all,
            'enabled_for_roles': self.enabled_for_roles,
            'enabled_for_user_ids': self.enabled_for_user_ids,
            'rollout_percentage': self.rollout_percentage,
            'environments': self.environments,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def is_enabled_for_user(self, user=None) -> bool:
        """Check if feature is enabled for a specific user"""
        if not self.enabled:
            return False
        
        # Check environment
        env = current_app.config.get('ENVIRONMENT', 'development')
        if env not in self.environments:
            return False
        
        # Check if enabled for all
        if self.enabled_for_all:
            return True
        
        # Check user-specific conditions
        if user:
            # Check by user ID
            if user.id in self.enabled_for_user_ids:
                return True
            
            # Check by role
            if hasattr(user, 'role') and user.role in self.enabled_for_roles:
                return True
            
            # Check rollout percentage (hash-based consistent rollout)
            if self.rollout_percentage > 0:
                user_hash = hash(f"{self.name}-{user.id}") % 100
                if user_hash < self.rollout_percentage:
                    return True
        
        return False
    
    @classmethod
    def is_enabled(cls, name: str, user=None) -> bool:
        """Class method to check if a feature is enabled"""
        from sqlalchemy import select
        stmt = select(cls).where(cls.name == name)
        flag = db.session.execute(stmt).scalar_one_or_none()
        if not flag:
            # Return default value from config if flag doesn't exist
            return current_app.config.get(f'FEATURE_{name.upper()}', False)
        return flag.is_enabled_for_user(user)


class FeatureFlagAudit(db.Model):
    """Audit log for feature flag changes"""
    
    __tablename__ = 'feature_flag_audit'
    
    id = db.Column(db.Integer, primary_key=True)
    flag_id = db.Column(db.Integer, db.ForeignKey('feature_flags.id'), nullable=False)
    action = db.Column(db.String(50))  # created, updated, enabled, disabled
    old_value = db.Column(db.JSON)
    new_value = db.Column(db.JSON)
    changed_by = db.Column(db.String(100))
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    reason = db.Column(db.Text)


# Feature Flag Manager
class FeatureFlagManager:
    """Manager class for feature flag operations"""
    
    @staticmethod
    def create_flag(
        name: str,
        description: str = '',
        enabled: bool = False,
        enabled_for_all: bool = False,
        enabled_for_roles: Optional[List[str]] = None,
        enabled_for_user_ids: Optional[List[int]] = None,
        rollout_percentage: int = 0,
        environments: Optional[List[str]] = None,
        created_by: str = 'system'
    ) -> FeatureFlag:
        """Create a new feature flag"""
        flag = FeatureFlag(
            name=name,
            description=description,
            enabled=enabled,
            enabled_for_all=enabled_for_all,
            enabled_for_roles=enabled_for_roles or [],
            enabled_for_user_ids=enabled_for_user_ids or [],
            rollout_percentage=rollout_percentage,
            environments=environments or ['development', 'testing', 'production'],
            created_by=created_by
        )
        db.session.add(flag)
        
        # Create audit log
        audit = FeatureFlagAudit(
            flag=flag,
            action='created',
            new_value=flag.to_dict(),
            changed_by=created_by,
            reason='Initial creation'
        )
        db.session.add(audit)
        db.session.commit()
        
        return flag
    
    @staticmethod
    def update_flag(
        flag_id: int,
        updates: Dict[str, Any],
        changed_by: str = 'system',
        reason: str = ''
    ) -> Optional[FeatureFlag]:
        """Update an existing feature flag"""
        from sqlalchemy import select
        stmt = select(FeatureFlag).where(FeatureFlag.id == flag_id)
        flag = db.session.execute(stmt).scalar_one_or_none()
        if not flag:
            return None
        
        old_value = flag.to_dict()
        
        for key, value in updates.items():
            if hasattr(flag, key):
                setattr(flag, key, value)
        
        flag.updated_at = datetime.now()
        
        # Create audit log
        audit = FeatureFlagAudit(
            flag=flag,
            action='updated',
            old_value=old_value,
            new_value=flag.to_dict(),
            changed_by=changed_by,
            reason=reason
        )
        db.session.add(audit)
        db.session.commit()
        
        return flag
    
    @staticmethod
    def toggle_flag(flag_id: int, enabled: bool, changed_by: str = 'system', reason: str = '') -> Optional[FeatureFlag]:
        """Toggle a feature flag on/off"""
        return FeatureFlagManager.update_flag(
            flag_id=flag_id,
            updates={'enabled': enabled},
            changed_by=changed_by,
            reason=reason
        )
    
    @staticmethod
    def get_flag(name: str) -> Optional[FeatureFlag]:
        """Get a feature flag by name"""
        return FeatureFlag.query.filter_by(name=name).first()
    
    @staticmethod
    def get_all_flags() -> List[FeatureFlag]:
        """Get all feature flags"""
        return FeatureFlag.query.all()
    
    @staticmethod
    def delete_flag(flag_id: int) -> bool:
        """Delete a feature flag"""
        from sqlalchemy import select
        stmt = select(FeatureFlag).where(FeatureFlag.id == flag_id)
        flag = db.session.execute(stmt).scalar_one_or_none()
        if flag:
            db.session.delete(flag)
            db.session.commit()
            return True
        return False


# Flask extension integration
def init_feature_flags(app):
    """Initialize feature flags with Flask app"""
    with app.app_context():
        db.create_all()
        
        # Create some default feature flags for demonstration
        default_flags = [
            {
                'name': 'new_dashboard',
                'description': 'Enable new dashboard design',
                'enabled': False,
                'enabled_for_all': False,
                'rollout_percentage': 0
            },
            {
                'name': 'ai_recommendations',
                'description': 'Enable AI-powered product recommendations',
                'enabled': False,
                'enabled_for_roles': ['admin', 'premium'],
                'rollout_percentage': 25
            },
            {
                'name': 'dark_mode',
                'description': 'Enable dark mode theme',
                'enabled': True,
                'enabled_for_all': True
            }
        ]
        
        for flag_data in default_flags:
            existing = FeatureFlag.query.filter_by(name=flag_data['name']).first()
            if not existing:
                FeatureFlagManager.create_flag(**flag_data)


# Template helper
def feature_flag(name: str) -> bool:
    """Template helper to check feature flag in templates"""
    from flask_login import current_user
    return FeatureFlag.is_enabled(name, current_user if current_user.is_authenticated else None)
