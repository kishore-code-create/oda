# config.py - Configuration for OilSpillPortal

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'portal-dev-key-change')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

class DatabaseConfig:
    """Database configuration"""
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'oil_spill_portal_db')

class GoogleOAuthConfig:
    """Google OAuth configuration"""
    CLIENT_SECRETS_FILE = os.getenv('GOOGLE_CLIENT_SECRETS_FILE', 'client_secret.json')
    CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
    CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
    REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5001/auth/google/callback')
    
    SCOPES = [
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/gmail.send",
        "openid"
    ]

class FileUploadConfig:
    """File upload configuration"""
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB

class SecurityConfig:
    """Security configuration"""
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
    OAUTHLIB_INSECURE_TRANSPORT = os.getenv('OAUTHLIB_INSECURE_TRANSPORT', '0')

def get_config():
    """Get configuration based on environment"""
    return Config()
