"""
Unit tests for the Flask application.
Tests cover models, routes, and utilities.
"""

import unittest
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, User, Order, Port, PremiumRequest
from models.user import Role
from models.order import OrderStatus
from datetime import datetime
import pytz


class BaseTestCase(unittest.TestCase):
    """Base test case with common setup."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        # Use PostgreSQL for tests (required for JSONB support)
        test_db_url = os.environ.get('TEST_DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/testdb')
        self.app.config['SQLALCHEMY_DATABASE_URI'] = test_db_url
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['D_STATE'] = 1  # Debug mode for SMS
        self.app.config['SECRET_KEY'] = 'test-secret-key-for-testing'
        
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
        self.ctx = self.app.app_context()
        self.ctx.push()
    
    def tearDown(self):
        """Tear down test fixtures."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        if hasattr(self, 'ctx'):
            self.ctx.pop()


class TestUserModel(BaseTestCase):
    """Test cases for User model."""
    
    def test_create_user(self):
        """Test creating a new user."""
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hashed_password',
            role=Role.BUYER
        )
        db.session.add(user)
        db.session.commit()
        
        found_user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(found_user)
        self.assertEqual(found_user.email, 'test@example.com')
        self.assertEqual(found_user.role, Role.BUYER)
    
    def test_user_role_enum(self):
        """Test Role enum values."""
        # Test new role values from CONTEXT_MASTER_BRIEF
        self.assertEqual(Role.BUYER.value, 'buyer')
        self.assertEqual(Role.PRODUCER.value, 'producer')
        self.assertEqual(Role.BROKER.value, 'broker')
        self.assertEqual(Role.ADMIN.value, 'admin')
    
    def test_role_has_value(self):
        """Test Role.has_value static method."""
        self.assertTrue(Role.has_value('buyer'))
        self.assertTrue(Role.has_value('admin'))
        self.assertFalse(Role.has_value('unknown'))
    
    def test_user_is_active_default(self):
        """Test that is_active defaults to True."""
        user = User(
            username='testuser2',
            email='test2@example.com',
            password_hash='hash',
            role=Role.PRODUCER
        )
        db.session.add(user)
        db.session.commit()
        
        self.assertTrue(user.is_active)
    
    def test_user_is_premium_default(self):
        """Test that is_premium defaults to False."""
        user = User(
            username='testuser3',
            email='test3@example.com',
            password_hash='hash',
            role=Role.BROKER
        )
        db.session.add(user)
        db.session.commit()
        
        self.assertFalse(user.is_premium)
    
    def test_user_unique_username(self):
        """Test that username must be unique."""
        user1 = User(
            username='duplicate',
            email='user1@example.com',
            password_hash='hash1',
            role=Role.BUYER
        )
        db.session.add(user1)
        db.session.commit()
        
        user2 = User(
            username='duplicate',
            email='user2@example.com',
            password_hash='hash2',
            role=Role.PRODUCER
        )
        db.session.add(user2)
        
        with self.assertRaises(Exception):
            db.session.commit()
    
    def test_user_unique_email(self):
        """Test that email must be unique."""
        user1 = User(
            username='user1',
            email='duplicate@example.com',
            password_hash='hash1',
            role=Role.BUYER
        )
        db.session.add(user1)
        db.session.commit()
        
        user2 = User(
            username='user2',
            email='duplicate@example.com',
            password_hash='hash2',
            role=Role.PRODUCER
        )
        db.session.add(user2)
        
        with self.assertRaises(Exception):
            db.session.commit()


class TestOrderModel(BaseTestCase):
    """Test cases for Order model."""
    
    def test_create_order(self):
        """Test creating a new order."""
        # First create users
        buyer = User(username='buyer', email='buyer@test.com', password_hash='hash', role=Role.BUYER)
        seller = User(username='seller', email='seller@test.com', password_hash='hash', role=Role.PRODUCER)
        db.session.add_all([buyer, seller])
        db.session.commit()
        
        order = Order(
            product='Wheat',
            quantity_tons=100.0,
            price_per_ton=500.0,
            total_price=50000.0,
            origin_port='Bandar Abbas',
            destination_port='Dubai',
            buyer_id=buyer.id,
            seller_id=seller.id,
            status=OrderStatus.PENDING
        )
        db.session.add(order)
        db.session.commit()
        
        found_order = Order.query.filter_by(product='Wheat').first()
        self.assertIsNotNone(found_order)
        self.assertEqual(found_order.quantity_tons, 100.0)
        self.assertEqual(found_order.status, OrderStatus.PENDING)
    
    def test_order_status_enum(self):
        """Test OrderStatus enum values."""
        self.assertEqual(OrderStatus.PENDING.value, 'pending')
        self.assertEqual(OrderStatus.CONFIRMED.value, 'confirmed')
        self.assertEqual(OrderStatus.IN_TRANSIT.value, 'in_transit')
        self.assertEqual(OrderStatus.DELIVERED.value, 'delivered')
        self.assertEqual(OrderStatus.CANCELLED.value, 'cancelled')
    
    def test_order_calculate_total(self):
        """Test order total price calculation."""
        buyer = User(username='buyer2', email='buyer2@test.com', password_hash='hash', role=Role.BUYER)
        seller = User(username='seller2', email='seller2@test.com', password_hash='hash', role=Role.PRODUCER)
        db.session.add_all([buyer, seller])
        db.session.commit()
        
        order = Order(
            product='Rice',
            quantity_tons=50.0,
            price_per_ton=800.0,
            total_price=0.0,
            origin_port='Bushehr',
            destination_port='Mumbai',
            buyer_id=buyer.id,
            seller_id=seller.id
        )
        
        order.calculate_total()
        self.assertEqual(order.total_price, 40000.0)
    
    def test_order_default_status(self):
        """Test that order status defaults to PENDING."""
        buyer = User(username='buyer3', email='buyer3@test.com', password_hash='hash', role=Role.BUYER)
        seller = User(username='seller3', email='seller3@test.com', password_hash='hash', role=Role.PRODUCER)
        db.session.add_all([buyer, seller])
        db.session.commit()
        
        order = Order(
            product='Corn',
            quantity_tons=25.0,
            price_per_ton=300.0,
            total_price=7500.0,
            origin_port='Chabahar',
            destination_port='Karachi',
            buyer_id=buyer.id,
            seller_id=seller.id
        )
        db.session.add(order)
        db.session.commit()
        
        self.assertEqual(order.status, OrderStatus.PENDING)


class TestPortModel(BaseTestCase):
    """Test cases for Port model."""
    
    def test_create_port(self):
        """Test creating a new port."""
        port = Port(
            name='Bandar Abbas',
            country='Iran',
            latitude=27.1832,
            longitude=56.2666
        )
        db.session.add(port)
        db.session.commit()
        
        found_port = Port.query.filter_by(name='Bandar Abbas').first()
        self.assertIsNotNone(found_port)
        self.assertEqual(found_port.country, 'Iran')
        self.assertAlmostEqual(found_port.latitude, 27.1832, places=4)


class TestPremiumRequestModel(BaseTestCase):
    """Test cases for PremiumRequest model."""
    
    def test_create_premium_request(self):
        """Test creating a premium request."""
        user = User(username='premium_user', email='premium@test.com', password_hash='hash', role=Role.BUYER)
        db.session.add(user)
        db.session.commit()
        
        request = PremiumRequest(
            user_id=user.id,
            requested_phone='09178001811'
        )
        db.session.add(request)
        db.session.commit()
        
        found_request = PremiumRequest.query.filter_by(user_id=user.id).first()
        self.assertIsNotNone(found_request)
        self.assertEqual(found_request.requested_phone, '09178001811')
        self.assertEqual(found_request.status, 'pending')
        self.assertFalse(found_request.phone_verified)
        self.assertFalse(found_request.email_verified)
    
    def test_premium_request_defaults(self):
        """Test PremiumRequest default values."""
        user = User(username='premium_user2', email='premium2@test.com', password_hash='hash', role=Role.PRODUCER)
        db.session.add(user)
        db.session.commit()
        
        request = PremiumRequest(
            user_id=user.id,
            requested_phone='09123456789'
        )
        db.session.add(request)
        db.session.commit()
        
        self.assertEqual(request.status, 'pending')
        self.assertFalse(request.phone_verified)
        self.assertFalse(request.email_verified)
        self.assertFalse(request.docs_verified)
        self.assertFalse(request.payment_verified)


class TestUserRoutes(BaseTestCase):
    """Test cases for user routes."""
    
    def test_login_page_loads(self):
        """Test that login page loads successfully."""
        response = self.client.get('/users/login')
        self.assertEqual(response.status_code, 200)
    
    def test_register_page_loads(self):
        """Test that register page loads successfully."""
        response = self.client.get('/users/register')
        self.assertEqual(response.status_code, 200)
    
    def test_profile_requires_login(self):
        """Test that profile page requires login."""
        response = self.client.get('/users/profile', follow_redirects=True)
        self.assertEqual(response.status_code, 200)


class TestAppCreation(BaseTestCase):
    """Test cases for app creation."""
    
    def test_app_is_created(self):
        """Test that the app is created successfully."""
        self.assertIsNotNone(self.app)
        self.assertTrue(self.app.testing)
    
    def test_database_is_initialized(self):
        """Test that database tables are created."""
        with self.app.app_context():
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            self.assertIn('user', tables)
            self.assertIn('orders', tables)


if __name__ == '__main__':
    unittest.main()
