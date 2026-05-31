"""
PostgreSQL Database Setup Script
This script creates tables in PostgreSQL (without data)
"""

import sys
from app import create_app, db
from models import *

def init_postgres_db():
    """Create tables in PostgreSQL without data"""
    app = create_app()
    
    with app.app_context():
        try:
            # Drop all existing tables (for clean start)
            print("🗑️  Dropping old tables...")
            db.drop_all()
            
            # Create new tables
            print("✨ Creating new tables in PostgreSQL...")
            db.create_all()
            
            print("✅ Database successfully initialized!")
            print("📊 Tables created:")
            
            # Get all table names from metadata
            tables = sorted(db.Model.metadata.tables.keys())
            
            for table in tables:
                print(f"   - {table}")
            
            print(f"\n📈 Total tables: {len(tables)}")
            print("\n💡 Note: Database is empty, no data has been inserted.")
            print("   To add data, you can use the load_ports_to_postgres.py script.")
            
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting PostgreSQL setup...")
    print("=" * 50)
    init_postgres_db()
