"""
Seed Data Script - Populates database with sample exhibitions, booths, and trading pairs.
Run this script to initialize the system with demo data for testing.

Usage:
    python scripts/seed_data.py
"""
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, '/workspace')

from app import create_app
from models import db
from models.exhibition import Exhibition, Booth, BoothType, ExhibitionStatus
from models.trading import TradingPair, OrderType, OrderSide, OrderStatus


def create_exhibitions():
    """Create sample exhibitions."""
    print("Creating exhibitions...")
    
    exhibitions_data = [
        {
            'title_en': 'Global Tech Expo 2024',
            'title_fa': 'Global Tech Expo 2024',
            'description_en': "The world's largest technology exhibition featuring cutting-edge innovations.",
            'description_fa': "The world's largest technology exhibition featuring cutting-edge innovations.",
            'start_date': datetime.utcnow(),
            'end_date': datetime.utcnow() + timedelta(days=30),
            'has_virtual_tour': True,
            'has_3d_booths': True,
            'has_live_chat': True,
            'has_video_conference': True,
            'banner_url': '/static/images/tech-expo-banner.jpg',
            'thumbnail_url': '/static/images/tech-expo-logo.png',
            'theme_color': '#1a56db',
            'settings': {
                'max_booths': 500,
                'registration_deadline': (datetime.utcnow() + timedelta(days=25)).isoformat(),
                'organizer': 'Metisma Events',
                'contact_email': 'expo@metisma.com',
                'website_url': 'https://metisma.com/expo/tech-2024',
                'social_media': {'twitter': '@metisma', 'linkedin': 'metisma'},
                'tags': ['technology', 'innovation', 'AI', 'blockchain']
            },
            'status_id': 1
        },
        {
            'title_en': 'International Trade Fair 2024',
            'title_fa': 'International Trade Fair 2024',
            'description_en': 'Connect with global traders and explore international business opportunities.',
            'description_fa': 'Connect with global traders and explore international business opportunities.',
            'start_date': datetime.utcnow() + timedelta(days=15),
            'end_date': datetime.utcnow() + timedelta(days=45),
            'has_virtual_tour': True,
            'has_3d_booths': True,
            'has_live_chat': True,
            'has_video_conference': False,
            'banner_url': '/static/images/trade-fair-banner.jpg',
            'thumbnail_url': '/static/images/trade-fair-logo.png',
            'theme_color': '#059669',
            'settings': {
                'max_booths': 1000,
                'registration_deadline': (datetime.utcnow() + timedelta(days=10)).isoformat(),
                'organizer': 'Metisma Trade',
                'contact_email': 'trade@metisma.com',
                'website_url': 'https://metisma.com/expo/trade-2024',
                'social_media': {'twitter': '@metismatrade', 'linkedin': 'metisma-trade'},
                'tags': ['trade', 'international', 'B2B', 'export']
            },
            'status_id': 1
        },
        {
            'title_en': 'Startup Pitch Arena',
            'title_fa': 'Startup Pitch Arena',
            'description_en': 'Watch innovative startups pitch their ideas to investors.',
            'description_fa': 'Watch innovative startups pitch their ideas to investors.',
            'start_date': datetime.utcnow() + timedelta(days=7),
            'end_date': datetime.utcnow() + timedelta(days=9),
            'has_virtual_tour': False,
            'has_3d_booths': False,
            'has_live_chat': True,
            'has_video_conference': True,
            'banner_url': '/static/images/startup-arena-banner.jpg',
            'thumbnail_url': '/static/images/startup-arena-logo.png',
            'theme_color': '#dc2626',
            'settings': {
                'max_booths': 100,
                'registration_deadline': (datetime.utcnow() + timedelta(days=5)).isoformat(),
                'organizer': 'Metisma Ventures',
                'contact_email': 'ventures@metisma.com',
                'website_url': 'https://metisma.com/expo/startup-arena',
                'social_media': {'twitter': '@metismaventures'},
                'tags': ['startup', 'pitch', 'investment', 'innovation']
            },
            'status_id': 1
        }
    ]
    
    created = []
    for data in exhibitions_data:
        exhibition = Exhibition(**data)
        exhibition.id = uuid.uuid4()
        db.session.add(exhibition)
        created.append(exhibition)
        print(f"  ✓ Created: {data['title_en']}")
    
    db.session.commit()
    return created


def create_booths(exhibitions):
    """Create sample booths for exhibitions."""
    print("\nCreating booths...")
    
    booth_templates = [
        {
            'title_en': 'AI Solutions Hub',
            'title_fa': 'AI Solutions Hub',
            'description_en': 'Leading AI solutions for enterprise automation.',
            'description_fa': 'Leading AI solutions for enterprise automation.',
            'type_id': 2,  # Premium
            'owner_type': 'company',
            'booth_number': 'A101',
            'location_x': 100,
            'location_y': 50,
            'gallery_images': ['/static/images/booths/techcorp-1.jpg', '/static/images/booths/techcorp-2.jpg'],
            'video_urls': ['https://youtube.com/watch?v=demo1'],
            'contact_info': {
                'email': 'info@techcorp-ai.example.com',
                'phone': '+1-555-0101',
                'website': 'https://techcorp-ai.example.com'
            },
            'social_media': {'linkedin': 'techcorp-ai', 'twitter': '@techcorpai'},
            'featured_products': ['AI Chatbots', 'ML Platforms', 'Computer Vision'],
            'services_offered': ['Consulting', 'Integration', 'Training'],
            'chat_enabled': True,
            'appointment_enabled': True,
            'model_3d_url': '/static/models/booth-premium.glb'
        },
        {
            'title_en': 'Global Trade Partners',
            'title_fa': 'Global Trade Partners',
            'description_en': 'Your gateway to international trade and export services.',
            'description_fa': 'Your gateway to international trade and export services.',
            'type_id': 1,  # Standard
            'owner_type': 'company',
            'booth_number': 'B205',
            'location_x': 200,
            'location_y': 100,
            'gallery_images': ['/static/images/booths/gtp-1.jpg'],
            'contact_info': {
                'email': 'contact@gtp-intl.example.com',
                'phone': '+1-555-0102',
                'website': 'https://gtp-intl.example.com'
            },
            'social_media': {'linkedin': 'gtp-international'},
            'featured_products': ['Export Consulting', 'Market Analysis', 'Trade Finance'],
            'services_offered': ['B2B Matching', 'Legal Support'],
            'chat_enabled': True,
            'appointment_enabled': True
        },
        {
            'title_en': 'Blockchain Innovations',
            'title_fa': 'Blockchain Innovations',
            'description_en': 'Next-generation blockchain solutions for finance and supply chain.',
            'description_fa': 'Next-generation blockchain solutions for finance and supply chain.',
            'type_id': 2,  # Premium
            'owner_type': 'company',
            'booth_number': 'C310',
            'location_x': 300,
            'location_y': 150,
            'gallery_images': ['/static/images/booths/chaintech-1.jpg', '/static/images/booths/chaintech-2.jpg'],
            'video_urls': ['https://youtube.com/watch?v=demo2'],
            'contact_info': {
                'email': 'hello@chaintech-labs.example.com',
                'phone': '+1-555-0103',
                'website': 'https://chaintech-labs.example.com'
            },
            'social_media': {'twitter': '@chaintechlabs', 'telegram': 'chaintech'},
            'featured_products': ['Smart Contracts', 'DeFi Platforms', 'Supply Chain Tracking'],
            'services_offered': ['Audit', 'Development', 'Advisory'],
            'chat_enabled': True,
            'appointment_enabled': True,
            'model_3d_url': '/static/models/booth-premium.glb'
        },
        {
            'title_en': 'E-commerce Solutions',
            'title_fa': 'E-commerce Solutions',
            'description_en': 'Complete e-commerce platforms and digital marketing tools.',
            'description_fa': 'Complete e-commerce platforms and digital marketing tools.',
            'type_id': 3,  # Startup
            'owner_type': 'company',
            'booth_number': 'D415',
            'location_x': 50,
            'location_y': 200,
            'gallery_images': ['/static/images/booths/shopflow-1.jpg'],
            'contact_info': {
                'email': 'support@shopflow.example.com',
                'website': 'https://shopflow.example.com'
            },
            'social_media': {'instagram': 'shopflow_official'},
            'featured_products': ['E-commerce Platform', 'Payment Gateway', 'Analytics'],
            'services_offered': ['Setup', 'Integration', 'Support'],
            'chat_enabled': True,
            'appointment_enabled': False
        }
    ]
    
    created = []
    for i, exhibition in enumerate(exhibitions):
        for j, template in enumerate(booth_templates):
            booth_data = template.copy()
            booth_data['exhibition_id'] = str(exhibition.id)
            booth_data['owner_id'] = uuid.uuid4()  # Random owner ID for demo
            
            # Add variation per exhibition
            booth_data['title_en'] = f"{template['title_en']} - Hall {i+1}"
            booth_data['booth_number'] = f"{chr(65+i)}{j+1:03d}"
            booth_data['location_x'] = (i * 100 + j * 50) % 500
            booth_data['location_y'] = (j * 80 + i * 40) % 400
            
            booth = Booth(**booth_data)
            booth.id = uuid.uuid4()
            db.session.add(booth)
            created.append(booth)
            print(f"  ✓ Created: {booth_data['title_en']} in {exhibition.title_en}")
    
    db.session.commit()
    return created


def create_trading_pairs():
    """Create sample trading pairs."""
    print("\nCreating trading pairs...")
    
    pairs_data = [
        {
            'base_asset': 'BTC',
            'quote_asset': 'USDT',
            'symbol': 'BTC/USDT',
            'min_order_size': Decimal('0.0001'),
            'max_order_size': Decimal('100'),
            'price_precision': 2,
            'quantity_precision': 6,
            'is_active': True,
            'is_featured': True
        },
        {
            'base_asset': 'ETH',
            'quote_asset': 'USDT',
            'symbol': 'ETH/USDT',
            'min_order_size': Decimal('0.001'),
            'max_order_size': Decimal('1000'),
            'price_precision': 2,
            'quantity_precision': 5,
            'is_active': True,
            'is_featured': True
        },
        {
            'base_asset': 'META',
            'quote_asset': 'USDT',
            'symbol': 'META/USDT',
            'min_order_size': Decimal('1'),
            'max_order_size': Decimal('100000'),
            'price_precision': 4,
            'quantity_precision': 2,
            'is_active': True,
            'is_featured': True
        },
        {
            'base_asset': 'GOLD',
            'quote_asset': 'USDT',
            'symbol': 'GOLD/USDT',
            'min_order_size': Decimal('0.01'),
            'max_order_size': Decimal('1000'),
            'price_precision': 2,
            'quantity_precision': 4,
            'is_active': True,
            'is_featured': False
        }
    ]
    
    created = []
    for data in pairs_data:
        pair = TradingPair(**data)
        pair.id = uuid.uuid4()
        db.session.add(pair)
        created.append(pair)
        print(f"  ✓ Created: {data['symbol']}")
    
    db.session.commit()
    return created


def main():
    """Main seed function."""
    app = create_app()
    
    with app.app_context():
        # Import db inside app context to ensure proper binding
        from models import db as db_instance
        
        print("=" * 60)
        print("Starting database seeding...")
        print("=" * 60)
        
        # Check if data already exists
        existing_exhibitions = Exhibition.query.with_session(db_instance.session).count()
        existing_booths = Booth.query.with_session(db_instance.session).count()
        existing_pairs = TradingPair.query.with_session(db_instance.session).count()
        
        if existing_exhibitions > 0 or existing_booths > 0 or existing_pairs > 0:
            print("\n⚠️  Database already contains data!")
            print(f"   Exhibitions: {existing_exhibitions}")
            print(f"   Booths: {existing_booths}")
            print(f"   Trading Pairs: {existing_pairs}")
            
            response = input("\nDo you want to continue? This will add MORE data. (y/n): ")
            if response.lower() != 'y':
                print("Seeding cancelled.")
                return
        
        try:
            # Create sample data
            exhibitions = create_exhibitions()
            create_booths(exhibitions)
            create_trading_pairs()
            
            print("\n" + "=" * 60)
            print("✅ Seeding completed successfully!")
            print("=" * 60)
            print(f"\nSummary:")
            print(f"  • Exhibitions: {Exhibition.query.with_session(db_instance.session).count()}")
            print(f"  • Booths: {Booth.query.with_session(db_instance.session).count()}")
            print(f"  • Trading Pairs: {TradingPair.query.with_session(db_instance.session).count()}")
            print(f"\nYou can now start exploring the platform!")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            db_instance.session.rollback()
            raise


if __name__ == '__main__':
    main()
