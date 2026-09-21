# config.py
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # Session / cookies
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # Pagination
    ITEMS_PER_PAGE = 20

    # App metadata
    APP_VERSION = '1.0.0'
    APP_NAME = 'LabMS'

    # Currency — used by the `money` Jinja filter.
    # Leave blank '' for plain numbers (e.g. 1500.00).
    # Set to 'Rs.' / 'PKR' / '₨' / '$' to prefix amounts with a symbol.
    APP_CURRENCY = os.getenv('APP_CURRENCY', '')


class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_ENV = 'development'


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    LOGIN_DISABLED = False


class ProductionConfig(Config):
    DEBUG = False
    FLASK_ENV = 'production'

    @property
    def SESSION_COOKIE_SECURE(self):
        return True


config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}