"""
Database initialization module.
This module initializes the database by dropping all existing tables and creating new ones.
"""

from app import app, db

def init_db():
    """
    Initializes the database by dropping all existing tables and creating new ones.
    """
    with app.app_context():
        db.drop_all()
        print("Dropped all existing tables")
        
        db.create_all()
        print("Created new database tables successfully!")

if __name__ == "__main__":
    init_db()