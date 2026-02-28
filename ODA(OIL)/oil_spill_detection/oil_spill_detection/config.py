# config.py - Centralized configuration for all Flask apps
# Import this in your Flask app instead of hardcoding values

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

class DatabaseConfig:
    """Database configuration"""
    MYSQL_HOST = os.getenv('DB_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('DB_PORT', 5432))
    MYSQL_USER = os.getenv('DB_USER', 'postgres')
    MYSQL_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    MYSQL_DB = os.getenv('DB_NAME', 'oil_spill_db')

    @staticmethod
    def get_connection_string():
        """Get SQLAlchemy connection string"""
        return f"postgresql+psycopg2://{DatabaseConfig.MYSQL_USER}:{DatabaseConfig.MYSQL_PASSWORD}@{DatabaseConfig.MYSQL_HOST}:{DatabaseConfig.MYSQL_PORT}/{DatabaseConfig.MYSQL_DB}"

class AWSConfig:
    """AWS configuration"""
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    S3_BUCKET = os.getenv('AWS_S3_BUCKET', '')

class GoogleOAuthConfig:
    """Google OAuth configuration"""
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5001/auth/google/callback')

class RoboflowConfig:
    """Roboflow API configuration"""
    API_KEY = os.getenv('ROBOFLOW_API_KEY', '')

class SecurityConfig:
    """Security configuration"""
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')

class LoggingConfig:
    """Logging configuration"""
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', '/var/log/oil-spill-app/app.log')

def get_config():
    """Get configuration based on environment"""
    return Config()
