#!/usr/bin/env python3
"""
Migration script to fix is_active column type from INTEGER to BOOLEAN
Run this script to update your production database on Render
"""

import psycopg2
import os
from urllib.parse import urlparse

def run_migration():
    """Run the database migration"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        print("Set it with: export DATABASE_URL='your-postgresql-url'")
        return False
    
    # Parse the database URL
    result = urlparse(database_url)
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        
        cur = conn.cursor()
        
        print("📊 Checking current schema...")
        
        # Check current type
        cur.execute("""
            SELECT column_name, data_type, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'accounts' AND column_name = 'is_active';
        """)
        
        before = cur.fetchone()
        print(f"   Before: {before}")
        
        if before and before[1] == 'boolean':
            print("✅ Column is already BOOLEAN type. No migration needed!")
            cur.close()
            conn.close()
            return True
        
        print("\n🔧 Running migration...")
        
        # Run the migration
        cur.execute("""
            ALTER TABLE accounts 
            ALTER COLUMN is_active TYPE BOOLEAN 
            USING CASE 
                WHEN is_active = 0 THEN FALSE 
                ELSE TRUE 
            END;
        """)
        
        cur.execute("""
            ALTER TABLE accounts 
            ALTER COLUMN is_active SET DEFAULT TRUE;
        """)
        
        # Commit the changes
        conn.commit()
        
        # Verify the change
        cur.execute("""
            SELECT column_name, data_type, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'accounts' AND column_name = 'is_active';
        """)
        
        after = cur.fetchone()
        print(f"   After: {after}")
        
        cur.close()
        conn.close()
        
        print("\n✅ Migration completed successfully!")
        print("   The is_active column is now BOOLEAN type.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Database Migration: Fix is_active Column Type")
    print("="*60)
    print()
    
    success = run_migration()
    
    if success:
        print("\n🎉 All done! Your database schema is now fixed.")
        print("   Restart your Render service to apply the changes.")
    else:
        print("\n⚠️  Migration failed. Please check the error above.")
