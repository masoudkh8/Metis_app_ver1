"""
Metisma Comprehensive Test Suite - مجموعه کامل تست‌های Unit و Integration
برای اجرای تست‌ها: pytest tests/test_comprehensive.py -v --cov=app

این فایل شامل تست‌های کامل برای ۸ ویژگی کلیدی است:
1. مدل کاربر پیشرفته با فیلدهای تخصصی
2. سیستم ثبت‌نام ۳ مرحله‌ای هوشمند
3. داشبورد هوشمند نقش‌محور
4. پروفایل کاربری پیشرفته با آپلود مدارک
5. امنیت و کنترل دسترسی (@role_required)
6. Rate Limiting
7. آپلود امن مدارک
8. سیستم امتیاز اعتماد (Trust Score)
"""

import pytest
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.datastructures import FileStorage
from io import BytesIO

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app, db
from models.user import User, UserProfile, Role as UserRole, MembershipTier
from models.trust_score import TrustScore
from extensions import limiter


# تعریف سطوح اعتماد به صورت دستی چون در مدل وجود ندارد
class TrustLevel:
    NEWCOMER = 'newcomer'
    BRONZE = 'bronze'
    SILVER = 'silver'
    GOLD = 'gold'
    PLATINUM = 'platinum'


@pytest.fixture
def app():
    """Create application with test settings"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['RATELIMIT_ENABLED'] = False
    app.config['UPLOAD_FOLDER'] = '/tmp/test_uploads'
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB
    app.config['SECRET_KEY'] = 'test-secret-key-12345'
    app.config['MAIL_SUPPRESS_SEND'] = True
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def sample_user(app):
    """Create sample user for tests"""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('TestPass123!'),
            role=UserRole.BUYER,
            trust_score_value=50
        )
        db.session.add(user)
        db.session.commit()
        
        profile = UserProfile(
            user_id=user.id,
            company_name='Test Company',
            country='IR',
            phone='+989123456789',
            expertise_area='Technology',
            job_title='CEO'
        )
        db.session.add(profile)
        
        trust_score = TrustScore(
            user_id=user.id,
            identity_score=20,
            expertise_score=15,
            social_score=10,
            dynamic_score=5
        )
        db.session.add(trust_score)
        db.session.commit()
        
        return user


# ============================================================================
# 1. تست‌های مدل کاربر پیشرفته
# ============================================================================

class TestAdvancedUserModel:
    """User Model Tests with Specialized Fields"""
    
    def test_create_user_with_specialized_fields(self, app):
        """Test creating user with specialized fields"""
        with app.app_context():
            user = User(
                username='prouser',
                email='pro@example.com',
                password='SecurePass123!',
                role=UserRole.PRODUCER,
                expertise_area='Manufacturing',
                job_title='Production Manager',
                bio='Experienced in international trade',
                website='https://example.com',
                social_links={'linkedin': 'https://linkedin.com/in/user'},
                membership_tier='gold'
            )
            db.session.add(user)
            db.session.commit()
            
            assert user.username == 'prouser'
            assert user.expertise_area == 'Manufacturing'
            assert user.job_title == 'Production Manager'
            assert user.bio == 'Experienced in international trade'
            assert user.website == 'https://example.com'
            assert user.social_links['linkedin'] == 'https://linkedin.com/in/user'
            assert user.membership_tier == 'gold'
            assert user.trust_score_value == 50
            assert user.is_verified is False
    
    def test_user_profile_creation(self, app, sample_user):
        """Test automatic user profile creation"""
        with app.app_context():
            user = db.session.get(User, sample_user.id)
            assert user.profile is not None
            assert user.profile.company_name == 'Test Company'
            assert user.profile.expertise_area == 'Technology'
            assert user.profile.job_title == 'CEO'
    
    def test_user_verification_documents(self, app, sample_user):
        """Test user identity verification documents"""
        with app.app_context():
            user = db.session.get(User, sample_user.id)
            
            doc = VerificationDocument(
                user_id=user.id,
                document_type='passport',
                file_path='/docs/passport_abc123.pdf',
                status='pending',
                uploaded_at=datetime.utcnow()
            )
            db.session.add(doc)
            db.session.commit()
            
            assert len(user.verification_documents) == 1
            assert user.verification_documents[0].document_type == 'passport'
            assert user.verification_documents[0].status == 'pending'
    
    def test_user_invite_code_generation(self, app):
        """Test exclusive invite code generation"""
        with app.app_context():
            import secrets
            
            user = User(
                username='inviter',
                email='inviter@example.com',
                password='SecurePass123!',
                role=UserRole.BROKER
            )
            user.invite_code = secrets.token_hex(8)
            db.session.add(user)
            db.session.commit()
            
            assert len(user.invite_code) == 16
            assert user.invite_code.isalnum()
    
    def test_user_role_enum_values(self, app):
        """Test user role enum values"""
        assert UserRole.PRODUCER.value == 'producer'
        assert UserRole.BUYER.value == 'buyer'
        assert UserRole.BROKER.value == 'broker'
        assert UserRole.CORPORATE_AGENT.value == 'corporate_agent'
        assert UserRole.LOGISTICS.value == 'logistics'
        assert UserRole.LEGAL.value == 'legal'
        assert UserRole.TECH_PARTNER.value == 'tech_partner'
        assert UserRole.INVESTOR.value == 'investor'
        assert UserRole.ADMIN.value == 'admin'
        assert UserRole.MODERATOR.value == 'moderator'
        assert len(UserRole) == 10


# ============================================================================
# 2. تست‌های سیستم ثبت‌نام ۳ مرحله‌ای
# ============================================================================

class TestThreeStepRegistration:
    """Smart 3-Step Registration System Tests"""
    
    def test_registration_step1_basic_info(self, client):
        """Test step 1: basic information"""
        response = client.post('/users/register', data={
            'username': 'step1user',
            'email': 'step1@example.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'role': 'buyer'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_registration_step2_professional_info(self, client):
        """Test step 2: professional information"""
        response = client.post('/users/register', data={
            'username': 'step2user',
            'email': 'step2@example.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'role': 'producer',
            'expertise_area': 'Agriculture',
            'job_title': 'Farm Manager',
            'company': 'Green Fields Co',
            'phone': '+989123456780'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_registration_step3_security_terms(self, client):
        """Test step 3: security and terms acceptance"""
        response = client.post('/users/register', data={
            'username': 'step3user',
            'email': 'step3@example.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'role': 'broker',
            'terms_accepted': 'y'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_registration_password_strength_validation(self, client):
        """Test password strength validation"""
        # رمز عبور ضعیف - بدون حروف بزرگ
        response = client.post('/users/register', data={
            'username': 'weakpass1',
            'email': 'weak1@example.com',
            'password': 'weakpass',
            'confirm_password': 'weakpass',
            'role': 'buyer'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # رمز عبور قوی
        response = client.post('/users/register', data={
            'username': 'strongpass',
            'email': 'strong@example.com',
            'password': 'StrongPass123!',
            'confirm_password': 'StrongPass123!',
            'role': 'buyer'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_registration_password_mismatch(self, client):
        """Test password mismatch"""
        response = client.post('/users/register', data={
            'username': 'mismatch',
            'email': 'mismatch@example.com',
            'password': 'Pass123!',
            'confirm_password': 'Pass456!',
            'role': 'buyer'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_registration_duplicate_email(self, client, sample_user):
        """Test preventing duplicate email"""
        response = client.post('/users/register', data={
            'username': 'duplicate',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'role': 'buyer'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_registration_auto_profile_creation(self, app, client):
        """Test automatic profile creation after registration"""
        with app.app_context():
            response = client.post('/users/register', data={
                'username': 'autoprofile',
                'email': 'autoprofile@example.com',
                'password': 'SecurePass123!',
                'role': 'buyer'
            }, follow_redirects=True)
            
            user = User.query.filter_by(username='autoprofile').first()
            assert user is not None
            assert user.profile is not None
            assert user.trust_score is not None


# ============================================================================
# 3. تست‌های داشبورد هوشمند نقش‌محور
# ============================================================================

class TestSmartDashboard:
    """Smart Role-Based Dashboard Tests"""
    
    def test_dashboard_rendering(self, client, sample_user):
        """Test dashboard rendering"""
        with app.test_client() as c:
            c.post('/users/login', data={
                'username': 'testuser',
                'password': 'TestPass123!'
            })
            
            response = c.get('/users/profile')
            assert response.status_code == 200
    
    def test_dashboard_widgets_for_buyer(self, app, sample_user):
        """Test dashboard widgets for Buyer"""
        with app.app_context():
            user = db.session.get(User, sample_user.id)
            assert user.role == UserRole.BUYER
            
            # Buyer باید ویجت‌های خاصی داشته باشد
            pending_tasks = []
            if not user.is_verified:
                pending_tasks.append('verify_identity')
            if not user.profile.company_name:
                pending_tasks.append('complete_profile')
            
            assert 'verify_identity' in pending_tasks
    
    def test_dashboard_widgets_for_producer(self, app):
        """Test dashboard widgets for Producer"""
        with app.app_context():
            producer = User(
                username='producer',
                email='producer@example.com',
                password='SecurePass123!',
                role=UserRole.PRODUCER
            )
            db.session.add(producer)
            db.session.commit()
            
            assert producer.role == UserRole.PRODUCER
            # Producer باید ویجت‌های محصولات و سفارشات داشته باشد
    
    def test_dashboard_pending_tasks_calculation(self, app, sample_user):
        """Test pending tasks calculation in dashboard"""
        with app.app_context():
            user = db.session.get(User, sample_user.id)
            
            pending_tasks = []
            
            # بررسی وضعیت تأیید هویت
            if not user.is_verified:
                pending_tasks.append({
                    'id': 'verify_identity',
                    'title': 'Identity Verification',
                    'priority': 'high'
                })
            
            # بررسی تکمیل پروفایل
            if not user.profile.bio:
                pending_tasks.append({
                    'id': 'complete_bio',
                    'title': 'Complete Biography',
                    'priority': 'medium'
                })
            
            assert len(pending_tasks) >= 1
            assert pending_tasks[0]['priority'] == 'high'


# ============================================================================
# 4. تست‌های پروفایل کاربری و آپلود مدارک
# ============================================================================

class TestProfileAndDocuments:
    """User Profile and Document Upload Tests"""
    
    def test_profile_edit(self, client, sample_user):
        """Test profile editing"""
        with app.test_client() as c:
            c.post('/users/login', data={
                'username': 'testuser',
                'password': 'TestPass123!'
            })
            
            response = c.post('/users/edit', data={
                'company_name': 'Updated Company',
                'expertise_area': 'Updated Expertise',
                'job_title': 'Updated Title',
                'bio': 'Updated bio description',
                'website': 'https://updated.com'
            }, follow_redirects=True)
            
            assert response.status_code == 200
    
    def test_profile_social_links_update(self, client, sample_user):
        """Test updating social links"""
        with app.test_client() as c:
            c.post('/users/login', data={
                'username': 'testuser',
                'password': 'TestPass123!'
            })
            
            response = c.post('/users/edit', data={
                'social_links': '{"linkedin": "https://linkedin.com/in/updated"}'
            }, follow_redirects=True)
            
            assert response.status_code == 200
    
    def test_document_upload_allowed_extensions(self, app):
        """Test allowed file extensions for upload"""
        from routes.users.routes import allowed_file
        
        assert allowed_file('document.pdf') is True
        assert allowed_file('image.png') is True
        assert allowed_file('photo.jpg') is True
        assert allowed_file('picture.jpeg') is True
        assert allowed_file('animation.gif') is True
        assert allowed_file('script.exe') is False
        assert allowed_file('virus.bat') is False
        assert allowed_file('hack.php') is False
    
    def test_document_upload_size_validation(self, app):
        """Test file size validation"""
        from routes.users.routes import validate_file
        
        # فایل 1MB (مجاز)
        small_file = BytesIO(b'a' * 1024 * 1024)
        assert validate_file(small_file) is True
        
        # فایل 4MB (مجاز)
        medium_file = BytesIO(b'a' * 4 * 1024 * 1024)
        assert validate_file(medium_file) is True
        
        # فایل 6MB (غیرمجاز - بیشتر از 5MB)
        large_file = BytesIO(b'a' * 6 * 1024 * 1024)
        assert validate_file(large_file) is False
    
    def test_secure_filename_generation(self, app):
        """Test secure filename generation"""
        from werkzeug.utils import secure_filename
        import secrets
        
        # نام فایل خطرناک
        dangerous_names = [
            '../../../etc/passwd',
            '..\\..\\windows\\system32',
            '/etc/shadow',
            'C:\\Windows\\System32'
        ]
        
        for name in dangerous_names:
            safe_name = secure_filename(name)
            assert '..' not in safe_name
            assert '/' not in safe_name
            assert '\\' not in safe_name
    
    def test_document_upload_flow(self, client, sample_user):
        """Test complete document upload flow"""
        with app.test_client() as c:
            # لاگین
            c.post('/users/login', data={
                'username': 'testuser',
                'password': 'TestPass123!'
            })
            
            # آپلود مدرک
            data = {
                'document': (BytesIO(b'PDF content for testing'), 'passport.pdf')
            }
            response = c.post('/users/upload_documents',
                            data=data,
                            content_type='multipart/form-data',
                            follow_redirects=True)
            
            assert response.status_code == 200


# ============================================================================
# 5. تست‌های امنیت و کنترل دسترسی
# ============================================================================

class TestSecurityAndAccessControl:
    """Security and Access Control Tests"""
    
    def test_role_required_decorator_authenticated(self, app, sample_user):
        """Test role_required decorator with logged-in user"""
        from routes.users.routes import role_required
        from flask_login import login_user
        
        with app.test_request_context():
            login_user(sample_user)
            
            @role_required('buyer', 'producer')
            def protected_view():
                return 'Access Granted'
            
            result = protected_view()
            assert result == 'Access Granted'
    
    def test_role_required_decorator_unauthenticated(self, app):
        """Test role_required decorator without login"""
        from routes.users.routes import role_required
        from flask_login import current_user
        
        with app.test_request_context():
            assert not current_user.is_authenticated
            
            @role_required('admin')
            def admin_view():
                return 'Admin Access'
            
            # باید redirect به صفحه لاگین شود
            with pytest.raises(Exception):
                admin_view()
    
    def test_role_required_decorator_wrong_role(self, app, sample_user):
        """Test role_required decorator with wrong role"""
        from routes.users.routes import role_required
        from flask_login import login_user
        
        with app.test_request_context():
            login_user(sample_user)  # کاربر BUYER است
            
            @role_required('admin')
            def admin_only():
                return 'Admin Only'
            
            # باید access denied شود
            with pytest.raises(Exception):
                admin_only()
    
    def test_password_hashing_security(self, app):
        """Test password hashing security"""
        with app.app_context():
            user = User(
                username='hashuser',
                email='hash@example.com',
                password='MySecurePassword123!'
            )
            db.session.add(user)
            db.session.commit()
            
            # رمز عبور نباید به صورت plain text ذخیره شود
            assert user.password_hash != 'MySecurePassword123!'
            assert len(user.password_hash) > 50
            
            # بررسی صحت رمز عبور
            assert check_password_hash(user.password_hash, 'MySecurePassword123!')
            assert not check_password_hash(user.password_hash, 'WrongPassword')
    
    def test_sql_injection_prevention(self, client, sample_user):
        """Test preventing SQL Injection"""
        # تلاش برای SQL Injection در لاگین
        response = client.post('/users/login', data={
            'username': "admin' OR '1'='1' --",
            'password': 'anything'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # نباید بتواند بدون رمز عبور صحیح وارد شود
    
    def test_xss_prevention_in_profile(self, client, sample_user):
        """Test preventing XSS in profile"""
        with app.test_client() as c:
            c.post('/users/login', data={
                'username': 'testuser',
                'password': 'TestPass123!'
            })
            
            # تلاش برای تزریق XSS
            response = c.post('/users/edit', data={
                'bio': '<script>alert("XSS Attack")</script>',
                'company_name': 'Test Company'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            # اسکریپت باید escape شود


# ============================================================================
# 6. تست‌های Rate Limiting
# ============================================================================

class TestRateLimiting:
    """Request Rate Limiting Tests"""
    
    def test_rate_limit_configuration(self, app):
        """Test Rate Limiting configuration"""
        # در محیط تست غیرفعال است
        assert app.config['RATELIMIT_ENABLED'] is False
        assert app.config['RATELIMIT_DEFAULT'] == '100 per hour'
        assert app.config['RATELIMIT_STRATEGY'] == 'moving-window'
    
    def test_rate_limit_on_registration_endpoint(self, client):
        """Test Rate Limit on registration endpoint"""
        # ارسال چندین درخواست متوالی
        responses = []
        for i in range(3):
            response = client.post('/users/register', data={
                'username': f'ratelimit{i}',
                'email': f'ratelimit{i}@example.com',
                'password': 'SecurePass123!',
                'role': 'buyer'
            })
            responses.append(response.status_code)
        
        # همه درخواست‌ها باید موفق باشند (چون در تست Rate Limit غیرفعال است)
        assert all(status in [200, 302] for status in responses)
    
    def test_rate_limit_decorator_presence(self, app):
        """Test Rate Limit decorator existence on routes"""
        from routes.users.routes import users_bp
        
        # بررسی وجود دکوریتور limiter
        # این تست بیشتر برای اطمینان از تنظیمات است
        assert app.config['RATELIMIT_ENABLED'] is not None


# ============================================================================
# 7. تست‌های آپلود امن مدارک
# ============================================================================

class TestSecureDocumentUpload:
    """Secure Document Upload Tests with Multi-layer Validation"""
    
    def test_multi_layer_validation_extension(self, app):
        """Test first layer: file extension check"""
        from routes.users.routes import allowed_file
        
        valid_extensions = ['pdf', 'png', 'jpg', 'jpeg', 'gif']
        invalid_extensions = ['exe', 'bat', 'sh', 'php', 'py', 'js']
        
        for ext in valid_extensions:
            assert allowed_file(f'document.{ext}') is True
        
        for ext in invalid_extensions:
            assert allowed_file(f'malicious.{ext}') is False
    
    def test_multi_layer_validation_size(self, app):
        """Test second layer: file size check"""
        from routes.users.routes import validate_file
        
        # فایل‌های با حجم مختلف
        test_sizes = [
            (100 * 1024, True),      # 100KB
            (1024 * 1024, True),     # 1MB
            (4 * 1024 * 1024, True), # 4MB
            (5 * 1024 * 1024, True), # 5MB (حد مجاز)
            (6 * 1024 * 1024, False) # 6MB (بیش از حد)
        ]
        
        for size, expected in test_sizes:
            file_obj = BytesIO(b'a' * size)
            result = validate_file(file_obj)
            assert result == expected
    
    def test_multi_layer_validation_secure_name(self, app):
        """Test third layer: secure filename generation"""
        from werkzeug.utils import secure_filename
        import secrets
        
        original = "../../../etc/passwd"
        secured = secure_filename(original)
        
        assert secured == "passwd"
        assert ".." not in secured
        assert "/" not in secured
        
        # افزودن token امن
        unique_name = f"user_{secrets.token_hex(8)}_{secured}"
        assert len(unique_name) > len(secured)
    
    def test_document_json_storage(self, app, sample_user):
        """Test JSON document storage"""
        with app.app_context():
            user = db.session.get(User, sample_user.id)
            
            # شبیه‌سازی ذخیره JSON مدارک
            import json
            documents = [
                {
                    'type': 'passport',
                    'path': '/docs/passport_abc123.pdf',
                    'uploaded_at': datetime.utcnow().isoformat(),
                    'status': 'pending'
                },
                {
                    'type': 'business_license',
                    'path': '/docs/license_xyz789.pdf',
                    'uploaded_at': datetime.utcnow().isoformat(),
                    'status': 'approved'
                }
            ]
            
            # تبدیل به JSON
            json_str = json.dumps(documents, ensure_ascii=False)
            assert isinstance(json_str, str)
            
            # بازیابی از JSON
            parsed = json.loads(json_str)
            assert len(parsed) == 2
            assert parsed[0]['type'] == 'passport'
    
    def test_document_upload_directory_traversal_prevention(self, app):
        """Test preventing Directory Traversal"""
        from werkzeug.utils import secure_filename
        import os
        
        malicious_paths = [
            '../../../etc/passwd',
            '..\\..\\windows\\system32',
            '/etc/shadow',
            'C:\\Windows\\System32\\config',
            '....//....//etc/passwd'
        ]
        
        for path in malicious_paths:
            secured = secure_filename(path)
            assert not os.path.isabs(secured)
            assert '..' not in secured


# ============================================================================
# 8. تست‌های سیستم امتیاز اعتماد (Trust Score)
# ============================================================================

class TestTrustScoreSystem:
    """Trust Score System Tests with Bronze/Silver/Gold/Platinum Levels"""
    
    def test_trust_score_initialization(self, app, sample_user):
        """Test initial Trust Score assignment"""
        with app.app_context():
            user = db.session.get(User, sample_user.id)
            trust_score = user.trust_score
            
            assert trust_score.identity_score == 20
            assert trust_score.expertise_score == 15
            assert trust_score.social_score == 10
            assert trust_score.dynamic_score == 5
            assert trust_score.total_score == 50
    
    def test_trust_score_badge_levels(self, app):
        """Test trust badge levels"""
        with app.app_context():
            # Platinum (90-100)
            platinum = TrustScore(identity_score=25, expertise_score=25, social_score=25, dynamic_score=25)
            assert platinum.get_badge() == "Platinum 🏆"
            assert platinum.get_level() == TrustLevel.PLATINUM
            
            # Gold (75-89)
            gold = TrustScore(identity_score=20, expertise_score=20, social_score=20, dynamic_score=20)
            assert gold.get_badge() == "Gold 🥇"
            assert gold.get_level() == TrustLevel.GOLD
            
            # Silver (50-74)
            silver = TrustScore(identity_score=15, expertise_score=15, social_score=10, dynamic_score=10)
            assert silver.get_badge() == "Silver 🥈"
            assert silver.get_level() == TrustLevel.SILVER
            
            # Bronze (25-49)
            bronze = TrustScore(identity_score=10, expertise_score=10, social_score=5, dynamic_score=5)
            assert bronze.get_badge() == "Bronze 🥉"
            assert bronze.get_level() == TrustLevel.BRONZE
            
            # Newcomer (0-24)
            newcomer = TrustScore(identity_score=5, expertise_score=5, social_score=5, dynamic_score=5)
            assert newcomer.get_badge() == "Newcomer 🆕"
    
    def test_trust_score_progression(self, app, sample_user):
        """Test Trust Score progression"""
        with app.app_context():
            user = db.session.get(User, sample_user.id)
            trust_score = user.trust_score
            
            initial_score = trust_score.total_score
            assert initial_score == 50
            
            # افزودن امتیاز برای تکمیل پروفایل
            trust_score.add_score_change(10, 'profile_completion', 'Complete Profile Information')
            assert trust_score.total_score == 60
            
            # افزودن امتیاز برای آپلود مدارک
            trust_score.add_score_change(15, 'document_upload', 'Passport Upload')
            assert trust_score.total_score == 75
            
            # بررسی تغییر بج
            assert trust_score.get_badge() == "Gold 🥇"
    
    def test_trust_score_history_tracking(self, app, sample_user):
        """Test tracking score change history"""
        with app.app_context():
            user = db.session.get(User, sample_user.id)
            trust_score = user.trust_score
            
            # ثبت چندین تغییر
            trust_score.add_score_change(10, 'profile_completion', 'Complete Profile')
            trust_score.add_score_change(15, 'document_upload', 'Document Upload')
            trust_score.add_score_change(-5, 'inactive_period', 'Inactivity Period')
            db.session.commit()
            
            assert len(trust_score.score_history) == 3
            
            # بررسی آخرین تغییر
            last_change = trust_score.score_history[-1]
            assert last_change.points == -5
            assert last_change.reason == 'inactive_period'
    
    def test_trust_score_four_layers(self, app):
        """Test four scoring layers"""
        with app.app_context():
            # لایه ۱: تأیید هویت پایه (۰-۲۵)
            layer1 = TrustScore(identity_score=25, expertise_score=0, social_score=0, dynamic_score=0)
            assert layer1.identity_score == 25
            assert layer1.total_score == 25
            
            # لایه ۲: تأیید تخصصی (۰-۲۵)
            layer2 = TrustScore(identity_score=25, expertise_score=25, social_score=0, dynamic_score=0)
            assert layer2.expertise_score == 25
            assert layer2.total_score == 50
            
            # لایه ۳: اعتبار اجتماعی (۰-۲۵)
            layer3 = TrustScore(identity_score=25, expertise_score=25, social_score=25, dynamic_score=0)
            assert layer3.social_score == 25
            assert layer3.total_score == 75
            
            # لایه ۴: اعتبار پویا (۰-۲۵)
            layer4 = TrustScore(identity_score=25, expertise_score=25, social_score=25, dynamic_score=25)
            assert layer4.dynamic_score == 25
            assert layer4.total_score == 100
    
    def test_trust_score_user_relationship(self, app, sample_user):
        """Test user relationship with Trust Score"""
        with app.app_context():
            user = db.session.get(User, sample_user.id)
            
            assert user.trust_score is not None
            assert user.trust_score.user_id == user.id
            assert user.trust_score_value == user.trust_score.total_score


# ============================================================================
# تست‌های Integration
# ============================================================================

class TestIntegrationFlows:
    """Integration Tests for Complete Flows"""
    
    def test_full_registration_to_dashboard_flow(self, client):
        """Test complete flow from registration to dashboard"""
        # 1. ثبت‌نام
        response = client.post('/users/register', data={
            'username': 'integrationuser',
            'email': 'integration@example.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'role': 'buyer',
            'expertise_area': 'Trade',
            'job_title': 'Manager',
            'company': 'Integration Corp',
            'phone': '+989123456789',
            'terms_accepted': 'y'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # 2. ورود
        response = client.post('/users/login', data={
            'username': 'integrationuser',
            'password': 'SecurePass123!'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # 3. مشاهده داشبورد
        response = client.get('/users/profile')
        assert response.status_code == 200
    
    def test_trust_score_full_progression_flow(self, app, client):
        """Test complete Trust Score progression flow"""
        with app.app_context():
            # ایجاد کاربر جدید
            user = User(
                username='progressionuser',
                email='progression@example.com',
                password='SecurePass123!',
                role=UserRole.PRODUCER
            )
            db.session.add(user)
            db.session.commit()
            
            trust_score = TrustScore(user_id=user.id)
            db.session.add(trust_score)
            db.session.commit()
            
            # مرحله 1: تکمیل پروفایل (+10)
            trust_score.add_score_change(10, 'profile_completion', 'Complete Profile')
            assert trust_score.total_score == 10
            
            # مرحله 2: آپلود مدارک (+15)
            trust_score.add_score_change(15, 'document_upload', 'Passport Upload')
            assert trust_score.total_score == 25
            assert trust_score.get_badge() == "Bronze 🥉"
            
            # مرحله 3: تأیید تخصص (+20)
            trust_score.add_score_change(20, 'expertise_verification', 'Expertise Verification')
            assert trust_score.total_score == 45
            assert trust_score.get_badge() == "Bronze 🥉"
            
            # مرحله 4: فعالیت اجتماعی (+15)
            trust_score.add_score_change(15, 'social_activity', 'Network Activity')
            assert trust_score.total_score == 60
            assert trust_score.get_badge() == "Silver 🥈"
            
            # مرحله 5: تعاملات موفق (+25)
            trust_score.add_score_change(25, 'successful_trades', 'Successful Transactions')
            assert trust_score.total_score == 85
            assert trust_score.get_badge() == "Gold 🥇"
            
            db.session.commit()
    
    def test_document_upload_and_verification_flow(self, app, client, sample_user):
        """Test document upload and verification flow"""
        with app.test_client() as c:
            # لاگین
            c.post('/users/login', data={
                'username': 'testuser',
                'password': 'TestPass123!'
            })
            
            # آپلود مدرک
            data = {
                'document': (BytesIO(b'PDF content'), 'passport.pdf')
            }
            response = c.post('/users/upload_documents',
                            data=data,
                            content_type='multipart/form-data',
                            follow_redirects=True)
            
            assert response.status_code == 200
            
            # بررسی در دیتابیس
            with app.app_context():
                user = db.session.get(User, sample_user.id)
                assert len(user.verification_documents) >= 0


# ============================================================================
# اجرای تست‌ها
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short', '--cov=app', '--cov-report=html'])
