# config.py - Configuration for RealTimeDetection

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'realtime-dev-key-change')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'results')

class GIBSConfig:
    """GIBS Service configuration"""
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'static', 'downloads')
    API_KEY = os.getenv('GIBS_API_KEY', '')
    BASE_URL = os.getenv('GIBS_BASE_URL', 'https://map1.vis.earthdata.nasa.gov/wmts-webmerc')

class ModelConfig:
    """Model configuration"""
    MODEL_PATH = os.getenv('MODEL_PATH', os.path.join(os.path.dirname(__file__), 'file.pth'))
    DEVICE = os.getenv('DEVICE', 'cpu')  # 'cuda' or 'cpu'

class SecurityConfig:
    """Security configuration"""
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')