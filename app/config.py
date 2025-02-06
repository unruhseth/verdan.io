import os
from dotenv import load_dotenv
import stripe


# Load environment variables from .env file
load_dotenv()




class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # Add JWT Secret
    SORACOM_API_KEY = os.getenv("SORACOM_API_KEY")
    SORACOM_TOKEN = os.getenv("SORACOM_TOKEN")
    SORACOM_BASE_URL = os.getenv("SORACOM_BASE_URL", "https://api-sandbox.soracom.io/v1")
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
