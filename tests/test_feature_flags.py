"""
Test suite for Feature Flag System
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from app import create_app
from models import db
from utils.feature_flags import FeatureFlag, FeatureFlagAudit, FeatureFlagManager


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    
    with app.app_context():
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['ENVIRONMENT'] = 'testing'
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def init_flags(app):
    """Initialize some test flags"""
    with app.app_context():
        flag1 = FeatureFlagManager.create_flag(
            name='test_feature',
            description='Test feature flag',
            enabled=True,
            enabled_for_all=True
        )
        
        flag2 = FeatureFlagManager.create_flag(
            name='beta_feature',
            description='Beta feature for specific users',
            enabled=True,
            enabled_for_all=False,
            enabled_for_user_ids=[1, 2, 3],
            rollout_percentage=50
        )
        
        flag3 = FeatureFlagManager.create_flag(
            name='disabled_feature',
            description='Disabled feature',
            enabled=False
        )
        
        yield [flag1, flag2, flag3]


class TestFeatureFlagModel:
    """Test FeatureFlag model"""
    
    def test_create_flag(self, app):
        with app.app_context():
            flag = FeatureFlagManager.create_flag(
                name='new_feature',
                description='A new feature',
                enabled=True
            )
            
            assert flag.name == 'new_feature'
            assert flag.description == 'A new feature'
            assert flag.enabled is True
            assert flag.id is not None
    
    def test_flag_to_dict(self, app):
        with app.app_context():
            flag = FeatureFlagManager.create_flag(
                name='test_flag',
                description='Test description',
                enabled=True,
                enabled_for_all=True,
                rollout_percentage=50
            )
            
            flag_dict = flag.to_dict()
            
            assert flag_dict['name'] == 'test_flag'
            assert flag_dict['description'] == 'Test description'
            assert flag_dict['enabled'] is True
            assert flag_dict['enabled_for_all'] is True
            assert flag_dict['rollout_percentage'] == 50
    
    def test_is_enabled_for_all(self, app):
        with app.app_context():
            flag = FeatureFlagManager.create_flag(
                name='global_feature',
                enabled=True,
                enabled_for_all=True
            )
            
            # Should be enabled for any user
            assert flag.is_enabled_for_user(None) is True
            mock_user = Mock(id=999)
            assert flag.is_enabled_for_user(mock_user) is True
    
    def test_is_enabled_for_specific_users(self, app):
        with app.app_context():
            flag = FeatureFlagManager.create_flag(
                name='user_feature',
                enabled=True,
                enabled_for_all=False,
                enabled_for_user_ids=[1, 2, 3]
            )
            
            user1 = Mock(id=1)
            user2 = Mock(id=2)
            user4 = Mock(id=4)
            
            assert flag.is_enabled_for_user(user1) is True
            assert flag.is_enabled_for_user(user2) is True
            assert flag.is_enabled_for_user(user4) is False
    
    def test_is_enabled_for_roles(self, app):
        with app.app_context():
            flag = FeatureFlagManager.create_flag(
                name='role_feature',
                enabled=True,
                enabled_for_all=False,
                enabled_for_roles=['admin', 'premium']
            )
            
            admin_user = Mock(id=1, role='admin')
            premium_user = Mock(id=2, role='premium')
            regular_user = Mock(id=3, role='user')
            
            assert flag.is_enabled_for_user(admin_user) is True
            assert flag.is_enabled_for_user(premium_user) is True
            assert flag.is_enabled_for_user(regular_user) is False
    
    def test_rollout_percentage(self, app):
        with app.app_context():
            flag = FeatureFlagManager.create_flag(
                name='rollout_feature',
                enabled=True,
                enabled_for_all=False,
                rollout_percentage=50
            )
            
            # Test that some users get it and some don't (statistically)
            enabled_count = 0
            for i in range(100):
                user = Mock(id=i)
                if flag.is_enabled_for_user(user):
                    enabled_count += 1
            
            # Should be approximately 50% (with some variance)
            assert 30 <= enabled_count <= 70
    
    def test_disabled_flag(self, app):
        with app.app_context():
            flag = FeatureFlagManager.create_flag(
                name='disabled',
                enabled=False,
                enabled_for_all=True
            )
            
            # Even with enabled_for_all, if enabled=False, it should be disabled
            assert flag.is_enabled_for_user(None) is False
    
    def test_environment_filtering(self, app):
        with app.app_context():
            flag = FeatureFlagManager.create_flag(
                name='env_feature',
                enabled=True,
                enabled_for_all=True,
                environments=['production']
            )
            
            # In testing environment, should be disabled
            assert flag.is_enabled_for_user(None) is False


class TestFeatureFlagManager:
    """Test FeatureFlagManager operations"""
    
    def test_update_flag(self, app, init_flags):
        with app.app_context():
            flag = FeatureFlag.query.filter_by(name='test_feature').first()
            
            updated = FeatureFlagManager.update_flag(
                flag_id=flag.id,
                updates={'enabled': False, 'description': 'Updated description'},
                changed_by='test_user',
                reason='Testing update'
            )
            
            assert updated is not None
            assert updated.enabled is False
            assert updated.description == 'Updated description'
    
    def test_toggle_flag(self, app, init_flags):
        with app.app_context():
            flag = FeatureFlag.query.filter_by(name='test_feature').first()
            
            # Toggle off
            updated = FeatureFlagManager.toggle_flag(
                flag_id=flag.id,
                enabled=False,
                changed_by='test_user'
            )
            assert updated.enabled is False
            
            # Toggle on
            updated = FeatureFlagManager.toggle_flag(
                flag_id=flag.id,
                enabled=True,
                changed_by='test_user'
            )
            assert updated.enabled is True
    
    def test_get_flag(self, app, init_flags):
        with app.app_context():
            flag = FeatureFlagManager.get_flag('test_feature')
            assert flag is not None
            assert flag.name == 'test_feature'
    
    def test_get_all_flags(self, app, init_flags):
        with app.app_context():
            flags = FeatureFlagManager.get_all_flags()
            assert len(flags) == 3
    
    def test_delete_flag(self, app, init_flags):
        with app.app_context():
            flag = FeatureFlag.query.filter_by(name='test_feature').first()
            result = FeatureFlagManager.delete_flag(flag.id)
            assert result is True
            
            # Verify deletion
            deleted_flag = FeatureFlag.query.filter_by(name='test_feature').first()
            assert deleted_flag is None
    
    def test_audit_log_created(self, app):
        with app.app_context():
            flag = FeatureFlagManager.create_flag(
                name='audit_test',
                description='Test audit',
                created_by='test_user'
            )
            
            audits = FeatureFlagAudit.query.filter_by(flag_id=flag.id).all()
            assert len(audits) >= 1
            assert audits[0].action == 'created'
            assert audits[0].changed_by == 'test_user'


class TestFeatureFlagClassMethod:
    """Test FeatureFlag.is_enabled class method"""
    
    def test_existing_flag(self, app, init_flags):
        with app.app_context():
            result = FeatureFlag.is_enabled('test_feature')
            assert result is True
    
    def test_nonexistent_flag_default_false(self, app):
        with app.app_context():
            result = FeatureFlag.is_enabled('nonexistent_flag')
            assert result is False
    
    def test_nonexistent_flag_with_config(self, app):
        app.config['FEATURE_NONEXISTENT'] = True
        
        with app.app_context():
            result = FeatureFlag.is_enabled('nonexistent')
            assert result is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
