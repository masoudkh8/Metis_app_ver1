# config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")
    D_STATE = os.environ.get("DEBUG_STATE", "0") == "1"
    
    # API Keys - should be set in environment variables
    AMOOTSMS_TOKEN = os.environ.get("AMOOTSMS_TOKEN", "")
    KAVENEGAR_API_KEY = os.environ.get("KAVENEGAR_API_KEY", "")
    
    SECRET_KEY = os.environ.get("SECRET_KEY")
    
    # Session Management - Professional Settings
    PERMANENT_SESSION_LIFETIME = int(os.environ.get("SESSION_TIMEOUT_MINUTES", "5")) * 60  # Default 30 minutes
    SESSION_REFRESH_EACH_REQUEST = True  # Refresh session on each request
    
    # Database configuration - PostgreSQL or SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    if not SQLALCHEMY_DATABASE_URI:
        # Fallback to SQLite in instance folder if DATABASE_URL not set
        basedir = os.path.abspath(os.path.dirname(__file__))
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'test.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email configuration
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "True").lower() in ("true", "1", "yes")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "")
    # ===== خطوط جدید برای پشتیبانی بهتر =====
    MAIL_ASCII_ATTACHMENTS = False  # پشتیبانی از کاراکترهای غیر انگلیسی در پیوست‌ها
    MAIL_SUPPRESS_SEND = False  # در توسعه اگر True باشد، ایمیل فقط در کنسول چاپ می‌شود


    # File upload settings
    basedir = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    PROFILE_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'profiles')
    MAGAZINE_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'magazines')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
    ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB max for profile images
    
    # reCAPTCHA Configuration
    RECAPTCHA_SITE_KEY = os.environ.get("RECAPTCHA_SITE_KEY", "")
    RECAPTCHA_SECRET_KEY = os.environ.get("RECAPTCHA_SECRET_KEY", "")
    RECAPTCHA_ENABLED = os.environ.get("RECAPTCHA_ENABLED", "False").lower() in ("true", "1", "yes")
    
    # Redis Configuration
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    
    # Celery Configuration
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'UTC'
    
    # Flask-Caching Configuration
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_URL = os.environ.get("CACHE_REDIS_URL", "redis://localhost:6379/0")
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes default timeout
    
    # SocketIO Configuration
    SOCKETIO_MESSAGE_QUEUE = os.environ.get("SOCKETIO_MESSAGE_QUEUE", "redis://localhost:6379/0")
    SOCKETIO_ASYNC_MODE = os.environ.get("SOCKETIO_ASYNC_MODE", "gevent")
    SOCKETIO_CORS_ALLOWED_ORIGINS = os.environ.get("SOCKETIO_CORS_ALLOWED_ORIGINS", "*")
    
    # Rate Limiting Configuration
    RATELIMIT_ENABLED = os.environ.get("RATELIMIT_ENABLED", "True").lower() in ("true", "1", "yes")
    RATELIMIT_STORAGE_URL = os.environ.get("RATELIMIT_STORAGE_URL", "redis://localhost:6379/1")
    RATELIMIT_STRATEGY = "moving-window"
    RATELIMIT_DEFAULT = "100 per hour"  # Default rate limit
    RATELIMIT_AUTHENTICATED = "200 per hour"  # Rate limit for authenticated users
    RATELIMIT_HEADERS_ENABLED = True  # Include rate limit headers in response
    
    # Internationalization (i18n) Configuration
    BABEL_DEFAULT_LOCALE = 'fa_IR'  # Default to Persian
    BABEL_TRANSLATION_DIRECTORIES = os.path.join(basedir, 'translations')
    LANGUAGES = ['fa_IR', 'en']
    DEFAULT_LANGUAGE = 'fa_IR'

