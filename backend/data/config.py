"""
Configuration module for application settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Check if we're in a testing environment
is_testing = os.environ.get('FLASK_TESTING') == 'True'

class Config:
    """Configuration class containing database and email settings."""
    
    # Use SQLite for testing, otherwise use the configured database
    if is_testing:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    else:
        SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "False") == "True"

    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")