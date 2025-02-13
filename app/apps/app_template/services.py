from .models import create_app_tables
from app.extensions import db
from typing import Optional, Tuple, List, Dict, Any


class AppNameService:
    """Service class for app-specific business logic"""
    
    @staticmethod
    def get_tables(account_id: int):
        """Get the table models for this account"""
        return create_app_tables(account_id)
    
    # Add your service methods below 