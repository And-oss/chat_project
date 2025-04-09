import os
from app import app, db

def init_db():
    with app.app_context():
        db.drop_all()
        print("Dropped all existing tables")
        
        db.create_all()
        print("Created new database tables successfully!")

if __name__ == "__main__":
    init_db() 

