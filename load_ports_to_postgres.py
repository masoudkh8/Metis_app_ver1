#!/usr/bin/env python3
"""
Script to load port data from JSON file to PostgreSQL
"""
import os
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

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

# Path to JSON file
JSON_FILE_PATH = os.path.join(os.path.dirname(__file__), 'static', 'files', 'ports_of_the_world_wpi.json')


def load_ports_to_postgres():
    """Load port data from JSON to PostgreSQL"""
    
    # Check if JSON file exists
    if not os.path.exists(JSON_FILE_PATH):
        print(f"❌ JSON file not found: {JSON_FILE_PATH}")
        return
    
    # Create database connection
    try:
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        print(f"✅ Connected to database: {DATABASE_URL.split('@')[-1]}")
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return
    
    # Read JSON file
    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ JSON file loaded successfully")
    except Exception as e:
        print(f"❌ Error reading JSON file: {e}")
        session.close()
        return
    
    # Check data structure (GeoJSON)
    if isinstance(data, dict) and 'features' in data:
        features = data['features']
        print(f"📊 Number of records found: {len(features)}")
    else:
        print("❌ Invalid JSON file structure (must be GeoJSON)")
        session.close()
        return
    
    # Create ports table if it doesn't exist (PostgreSQL syntax)
    create_table_sql = text("""
    CREATE TABLE IF NOT EXISTS ports (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        country VARCHAR(50) NOT NULL,
        latitude FLOAT NOT NULL,
        longitude FLOAT NOT NULL
    );
    """)
    
    try:
        with engine.connect() as conn:
            conn.execute(create_table_sql)
            conn.commit()
        print("✅ Table 'ports' created (or already exists)")
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        session.close()
        return
    
    # Insert data
    inserted_count = 0
    skipped_count = 0
    
    insert_query = text("""
        INSERT INTO ports (name, country, latitude, longitude)
        VALUES (:name, :country, :latitude, :longitude)
    """)
    
    check_query = text("""
        SELECT COUNT(*) FROM ports 
        WHERE name = :name AND country = :country
    """)
    
    for feature in features:
        try:
            props = feature.get('properties', {})
            coords = feature.get('geometry', {}).get('coordinates', [])
            
            name = props.get('PORT_NAME')
            country = props.get('COUNTRY')
            longitude = coords[0] if len(coords) > 0 else None
            latitude = coords[1] if len(coords) > 1 else None
            
            # Check required data
            if not name or not country or latitude is None or longitude is None:
                skipped_count += 1
                continue
            
            # Check for duplicates
            with engine.connect() as conn:
                result = conn.execute(check_query, {"name": name, "country": country})
                count = result.scalar()
                
                if count > 0:
                    skipped_count += 1
                    continue
                
                # Insert new record
                conn.execute(insert_query, {
                    "name": name, 
                    "country": country, 
                    "latitude": float(latitude), 
                    "longitude": float(longitude)
                })
                conn.commit()
                inserted_count += 1
                
        except Exception as e:
            print(f"⚠️ Error processing record: {e}")
            skipped_count += 1
            continue
    
    session.close()
    
    # Final report
    print("\n" + "="*50)
    print(f"✅ Operation completed successfully!")
    print(f"   Records inserted: {inserted_count}")
    print(f"   Records skipped: {skipped_count}")
    print("="*50)


if __name__ == "__main__":
    load_ports_to_postgres()
