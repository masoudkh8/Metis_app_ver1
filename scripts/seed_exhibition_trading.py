#!/usr/bin/env python3
"""
Seed script for Exhibition and Trading modules
Creates sample data for testing and demo purposes
Run with: python scripts/seed_exhibition_trading.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db
from models.exhibition import Exhibition, Booth, BoothType, ExhibitionStatus
from models.trading import TradingPair, MarketData, TradingSetting
from datetime import datetime, timedelta
import random
from decimal import Decimal

def seed_data():
    app = create_app()
    
    with app.app_context():
        print("🌱 Starting data seeding...")
        
        # === Seed Exhibitions ===
        print("\n📊 Creating exhibitions...")
        
        exhibitions_data = [
            {
                'title_fa': 'International Technology Exhibition',
                'title_en': 'International Technology Exhibition',
                'description_fa': 'The largest technology exhibition in the Middle East',
                'description_en': 'The largest technology exhibition in the Middle East',
                'status': 'active'
            },
            {
                'title_fa': 'Petrochemical Industries Exhibition',
                'title_en': 'Petrochemical Industries Exhibition',
                'description_fa': 'Specialized exhibition for petrochemical and energy industries',
                'description_en': 'Specialized exhibition for petrochemical and energy industries',
                'status': 'active'
            },
            {
                'title_fa': 'Consumer Goods Exhibition',
                'title_en': 'Consumer Goods Exhibition',
                'description_fa': 'Exhibition for consumer and household products',
                'description_en': 'Exhibition for consumer and household products',
                'status': 'active'
            }
        ]
        
        exhibitions = []
        for ex_data in exhibitions_data:
            # Get status object from enum table
            status_obj = ExhibitionStatus.query.filter_by(status=ex_data['status']).first()
            if not status_obj:
                print(f"Warning: Status '{ex_data['status']}' not found, using first available")
                status_obj = ExhibitionStatus.query.first()
            
            exhibition = Exhibition(
                title_fa=ex_data['title_fa'],
                title_en=ex_data['title_en'],
                description_fa=ex_data['description_fa'],
                description_en=ex_data['description_en'],
                start_date=datetime.now() - timedelta(days=5),
                end_date=datetime.now() + timedelta(days=25),
                status_id=status_obj.id if status_obj else 1
            )
            db.session.add(exhibition)
            exhibitions.append(exhibition)
        
        db.session.commit()
        print(f"✅ Created {len(exhibitions)} exhibitions")
        
        # === Seed Booths ===
        print("\n🏪 Creating booths...")
        
        booth_titles = [
            ('Information Technology', 'Information Technology'),
            ('Artificial Intelligence', 'Artificial Intelligence'),
            ('Blockchain', 'Blockchain'),
            ('Renewable Energy', 'Renewable Energy'),
            ('Food Industries', 'Food Industries'),
            ('Pharmaceuticals', 'Pharmaceuticals'),
            ('Automotive', 'Automotive'),
            ('Textiles', 'Textiles'),
            ('Construction', 'Construction'),
            ('Agriculture', 'Agriculture')
        ]
        
        booths = []
        for i, (title_fa, title_en) in enumerate(booth_titles):
            exhibition = exhibitions[i % len(exhibitions)]
            
            # Get booth type from enum table
            booth_type_name = 'premium' if i < 3 else 'standard'
            booth_type_obj = BoothType.query.filter_by(booth_type=booth_type_name).first()
            
            booth = Booth(
                title_fa=title_fa,
                title_en=title_en,
                description_fa=f'Specialized booth for {title_fa} with modern products',
                description_en=f'Specialized booth for {title_en} with modern products',
                exhibition_id=exhibition.id,
                owner_type='user',
                owner_id=1,
                type_id=booth_type_obj.id if booth_type_obj else 1,
                is_active=True,
                approval_status='approved',
                booth_number=f'B-{i+1:03d}',
                slug=f'booth-{i+1}',
                gallery_images=[],
                video_urls=[],
                featured_products=[],
                services_offered=[],
                contact_info={},
                model_3d_config={}
            )
            db.session.add(booth)
            booths.append(booth)
        
        db.session.commit()
        print(f"✅ Created {len(booths)} booths")
        
        # === Seed Trading Pairs ===
        print("\n💹 Creating trading pairs...")
        
        trading_pairs_data = [
            ('BTC', 'USDT', 'Bitcoin', 'Tether'),
            ('ETH', 'USDT', 'Ethereum', 'Tether'),
            ('BNB', 'USDT', 'Binance Coin', 'Tether'),
            ('SOL', 'USDT', 'Solana', 'Tether'),
            ('ADA', 'USDT', 'Cardano', 'Tether'),
            ('XRP', 'USDT', 'Ripple', 'Tether'),
            ('DOT', 'USDT', 'Polkadot', 'Tether'),
            ('DOGE', 'USDT', 'Dogecoin', 'Tether'),
            ('AVAX', 'USDT', 'Avalanche', 'Tether'),
            ('MATIC', 'USDT', 'Polygon', 'Tether')
        ]
        
        base_prices = {
            'BTC': 43000,
            'ETH': 2300,
            'BNB': 310,
            'SOL': 98,
            'ADA': 0.52,
            'XRP': 0.62,
            'DOT': 7.2,
            'DOGE': 0.08,
            'AVAX': 36,
            'MATIC': 0.85
        }
        
        pairs = []
        for base, quote, base_name, quote_name in trading_pairs_data:
            symbol = f"{base}/{quote}"
            current_price = base_prices.get(base, 100)
            
            pair = TradingPair(
                base_currency=base,
                quote_currency=quote,
                symbol=symbol,
                base_asset_name=base_name,
                quote_asset_name=quote_name,
                current_price=Decimal(str(current_price)),
                price_change_24h=Decimal(str(random.uniform(-5, 8))),
                volume_24h=Decimal(str(random.uniform(1000000, 50000000))),
                high_24h=Decimal(str(current_price * 1.05)),
                low_24h=Decimal(str(current_price * 0.95)),
                tick_size=Decimal('0.01') if current_price > 10 else Decimal('0.0001'),
                min_order_size=Decimal('0.001'),
                max_order_size=Decimal('1000'),
                maker_fee=Decimal('0.001'),
                taker_fee=Decimal('0.001'),
                status='active',
                is_marquee=i < 5
            )
            db.session.add(pair)
            pairs.append(pair)
        
        db.session.commit()
        print(f"✅ Created {len(pairs)} trading pairs")
        
        # === Seed Market Data ===
        print("\n📈 Creating historical market data...")
        
        for pair in pairs[:3]:
            base_price = float(pair.current_price)
            market_data_points = []
            
            for hours_ago in range(100, 0, -1):
                timestamp = datetime.now() - timedelta(hours=hours_ago)
                price_change = random.uniform(-0.02, 0.02)
                price = base_price * (1 + price_change)
                base_price = price
                
                market_data = MarketData(
                    pair_id=pair.id,
                    timestamp=timestamp,
                    open_price=Decimal(str(price)),
                    high_price=Decimal(str(price * random.uniform(1.001, 1.01))),
                    low_price=Decimal(str(price * random.uniform(0.99, 0.999))),
                    close_price=Decimal(str(price)),
                    volume=Decimal(str(random.uniform(100, 10000)))
                )
                market_data_points.append(market_data)
            
            db.session.bulk_save_objects(market_data_points)
        
        db.session.commit()
        print("✅ Created historical market data")
        
        # === Seed Trading Settings ===
        print("\n⚙️ Creating trading settings...")
        
        settings = TradingSetting(
            trading_enabled=True,
            maintenance_mode=False,
            default_maker_fee=Decimal('0.001'),
            default_taker_fee=Decimal('0.001'),
            min_trade_amount=Decimal('1'),
            max_trade_amount=Decimal('1000000'),
            withdrawal_fee_btc=Decimal('0.0005'),
            withdrawal_fee_eth=Decimal('0.005'),
            allowed_countries=['IR', 'AE', 'TR', 'IQ', 'AF'],
            kyc_required_for_withdrawal=True,
            max_withdrawal_daily=Decimal('100000')
        )
        db.session.add(settings)
        db.session.commit()
        print("✅ Created trading settings")
        
        print("\n" + "="*50)
        print("🎉 Seeding completed successfully!")
        print("="*50)
        print(f"\nSummary:")
        print(f"  • Exhibitions: {len(exhibitions)}")
        print(f"  • Booths: {len(booths)}")
        print(f"  • Trading Pairs: {len(pairs)}")
        print(f"  • Market Data Points: {len(pairs[:3]) * 100}")
        print(f"\nYou can now visit:")
        print(f"  • Exhibition Hall: http://localhost:5000/exhibition/")
        print(f"  • Trading Market: http://localhost:5000/trading/")

if __name__ == '__main__':
    seed_data()
