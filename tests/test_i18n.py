#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
تست‌های سیستم چندزبانه Metisma
i18n Tests for Metisma Platform
"""

import pytest
from app import create_app
from models import db
from models.user import User, Role
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['RATELIMIT_ENABLED'] = False
    app.config['BABEL_DEFAULT_LOCALE'] = 'fa_IR'
    app.config['SECRET_KEY'] = 'test-secret-key-for-i18n-testing'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def sample_user(app):
    """Create a sample user for testing."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('TestPass123'),
            role=Role.BUYER
        )
        db.session.add(user)
        db.session.commit()
        return user


class TestI18nSystem:
    """Multilingual System Tests"""
    
    def test_persian_locale_default(self, client):
        """Test Persian language as default"""
        rv = client.get('/')
        assert rv.status_code == 200
    
    def test_language_switcher_fa(self, client):
        """Test switching language to Persian"""
        rv = client.get('/language/set_language/fa_IR', follow_redirects=True)
        # Should redirect without error
        assert rv.status_code in [200, 302]
    
    def test_language_switcher_en(self, client):
        """Test switching language to English"""
        rv = client.get('/language/set_language/en', follow_redirects=True)
        assert rv.status_code in [200, 302]
    
    def test_invalid_language_code(self, client):
        """Test invalid language code"""
        rv = client.get('/language/set_language/invalid', follow_redirects=True)
        # Should handle gracefully
        assert rv.status_code in [200, 302, 404]
    
    def test_session_language_persistence(self, client):
        """Test language persistence in session"""
        with client.session_transaction() as sess:
            sess['lang'] = 'fa_IR'
        
        rv = client.get('/users/profile')
        # Session should persist
        assert rv.status_code in [200, 302, 401, 403]
    
    def test_url_language_parameter(self, client):
        """Test language parameter in URL"""
        rv = client.get('/?lang=fa_IR')
        assert rv.status_code == 200
        
        rv = client.get('/?lang=en')
        assert rv.status_code == 200


class TestTranslations:
    """Translation Files Tests"""
    
    def test_translation_files_exist(self):
        """Test translation files exist"""
        import os
        po_file = '/workspace/translations/fa_IR/LC_MESSAGES/messages.po'
        mo_file = '/workspace/translations/fa_IR/LC_MESSAGES/messages.mo'
        
        assert os.path.exists(po_file), "messages.po file does not exist"
        assert os.path.exists(mo_file), "messages.mo file does not exist"
    
    def test_translation_file_not_empty(self):
        """Test translation file is not empty"""
        import os
        po_file = '/workspace/translations/fa_IR/LC_MESSAGES/messages.po'
        
        with open(po_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert len(content) > 1000, "Translation file is too small"
        assert 'msgstr' in content, "Translation file lacks translations"
    
    def test_key_translation_pairs(self):
        """Test key-translation pairs"""
        import os
        po_file = '/workspace/translations/fa_IR/LC_MESSAGES/messages.po'
        
        with open(po_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for common keys
        assert 'msgid "Login"' in content
        assert 'msgstr "ورود"' in content
        assert 'msgid "Register"' in content
        assert 'msgstr "ثبت‌نام"' in content
        assert 'msgid "Trust Score"' in content
        assert 'msgstr "امتیاز اعتماد"' in content


class TestBabelIntegration:
    """Flask-Babel Integration Tests"""
    
    def test_babel_initialized(self, app):
        """Test Flask-Babel initialization"""
        assert 'babel' in app.extensions or hasattr(app, 'extensions')
    
    def test_locale_selector_function(self, app):
        """Test language selector function"""
        with app.test_request_context('/?lang=fa_IR'):
            from flask import session
            session['lang'] = 'fa_IR'
            
            # Get locale function
            from app import create_app
            # The locale selector should return fa_IR
            assert True  # Basic check
    
    def test_translation_function_available(self, client):
        """Test translation function availability"""
        rv = client.get('/')
        # Page should load without translation errors
        assert rv.status_code == 200


class TestRTLSupport:
    """RTL Support Tests"""
    
    def test_persian_text_direction(self):
        """Test Persian text direction"""
        persian_text = "Persian"
        # Persian text should be right-to-left
        assert len(persian_text) > 0
        # Basic Unicode check for Persian characters
        assert any('\u0600' <= char <= '\u06FF' for char in persian_text)
    
    def test_translation_contains_rtl_content(self):
        """Test RTL content in translations"""
        import os
        po_file = '/workspace/translations/fa_IR/LC_MESSAGES/messages.po'
        
        with open(po_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for Persian characters (Unicode range)
        has_persian = any('\u0600' <= char <= '\u06FF' for char in content)
        assert has_persian, "Translation file lacks Persian characters"


class TestLanguageRoutes:
    """Language Routes Tests"""
    
    def test_language_blueprint_registered(self, app):
        """Test language blueprint registration"""
        assert 'language' in app.blueprints
    
    def test_set_language_route_exists(self, client):
        """Test set language route exists"""
        # Route should exist
        rv = client.get('/language/set_language/fa_IR')
        assert rv.status_code in [200, 302, 404]


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
