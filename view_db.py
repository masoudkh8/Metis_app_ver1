#!/usr/bin/env python3
"""
PostgreSQL Database Viewer Script
This script is used to view tables and data in PostgreSQL
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

# Get database URL from environment variable - PostgreSQL only
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("❌ Error: DATABASE_URL is not set in .env file!")
    print("Example: postgresql://user:password@localhost:5432/ports_db")
    exit(1)

# Check that URL starts with postgresql://
if not DATABASE_URL.startswith('postgresql://'):
    print(f"❌ Error: DATABASE_URL must start with postgresql://")
    print(f"Current value: {DATABASE_URL}")
    exit(1)

try:
    engine = create_engine(DATABASE_URL)
    print(f"✅ Connected to database: {DATABASE_URL.split('@')[-1]}")
except Exception as e:
    print(f"❌ Error connecting to database: {e}")
    exit(1)

with engine.connect() as conn:
    # List tables
    print("\n📊 Available tables:")
    result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """))
    tables = result.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"  - {table_name}")
        
        # Display first 5 rows of each table
        try:
            result = conn.execute(text(f'SELECT * FROM {table_name} LIMIT 5'))
            rows = result.fetchall()
            
            if rows:
                # Column names
                columns = [desc[0] for desc in result.cursor.description]
                print(f"     Columns: {', '.join(columns)}")
                print(f"     Records (showing first 5): {len(rows)}")
            else:
                print(f"     (Table is empty)")
        except Exception as e:
            print(f"     ⚠️ Error reading table: {e}")

print("\n✅ End of database information display")