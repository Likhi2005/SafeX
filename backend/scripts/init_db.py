#!/usr/bin/env python3
"""
Database initialization script for SafeX.
Run this to create the database schema.
"""

from backend.app import create_app
from backend.models import db
import logging

def init_database():
    """Initialize the database schema."""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Print table info
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📊 Created tables: {tables}")
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            return False
    
    return True

if __name__ == '__main__':
    init_database()