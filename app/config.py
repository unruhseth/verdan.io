import os
from dotenv import load_dotenv
import stripe


# Load environment variables from .env file
load_dotenv()




class Config:
    # Environment
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = ENV == "development"
    TESTING = ENV == "testing"
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    
    # Server Configuration
    SERVER_NAME = os.getenv("SERVER_NAME", "localhost:5000")
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # CORS Settings
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", FRONTEND_URL).split(",")
    CORS_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    CORS_ALLOWED_HEADERS = ["Content-Type", "Authorization"]
    CORS_SUPPORTS_CREDENTIALS = True
    
    # External Services
    SORACOM_API_KEY = os.getenv("SORACOM_API_KEY")
    SORACOM_TOKEN = os.getenv("SORACOM_TOKEN")
    SORACOM_BASE_URL = os.getenv("SORACOM_BASE_URL", "https://api-sandbox.soracom.io/v1")
    
    # Stripe Configuration
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
    stripe.api_key = STRIPE_SECRET_KEY

    # App Configuration
    APP_STORAGE_PATH = os.getenv("APP_STORAGE_PATH", "app/apps")
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
