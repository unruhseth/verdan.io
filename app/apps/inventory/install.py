import requests
from flask import current_app
from app.extensions import db
from .models import create_enum_types, Category, Item, Transaction
from app.models.user_app import UserApp
from sqlalchemy import text, inspect
from datetime import datetime

class VerdanInstaller:
    def __init__(self):
        self.api_key = current_app.config['VERDAN_API_KEY']
        self.base_url = current_app.config['VERDAN_BASE_URL']
    
    def register_app(self):
        """Register the inventory tracker app with Verdan platform"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'name': 'inventory_tracker',
            'description': 'Inventory tracking application for Verdan platform',
            'version': '1.0.0',
            'endpoints': [
                {
                    'path': '/api/inventory',
                    'methods': ['GET', 'POST'],
                    'description': 'List all items or create a new item'
                },
                {
                    'path': '/api/inventory/{item_id}',
                    'methods': ['GET', 'PUT', 'DELETE'],
                    'description': 'Get, update or delete specific item'
                },
                {
                    'path': '/api/inventory/{item_id}/adjust',
                    'methods': ['POST'],
                    'description': 'Adjust item quantity'
                }
            ]
        }
        
        try:
            response = requests.post(
                f'{self.base_url}/apps/register',
                headers=headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f'Failed to register app with Verdan: {str(e)}')
    
    def uninstall(self):
        """Uninstall the app from Verdan platform"""
        headers = {
            'Authorization': f'Bearer {self.api_key}'
        }
        
        try:
            response = requests.delete(
                f'{self.base_url}/apps/inventory_tracker',
                headers=headers
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            raise Exception(f'Failed to uninstall app from Verdan: {str(e)}')

def install_inventory(account_id):
    """Install the inventory app for a specific account"""
    try:
        # Create enum types first
        create_enum_types()
        
        # Create tables if they don't exist
        inspector = inspect(db.engine)
        
        if not inspector.has_table('inventory_categories'):
            Category.__table__.create(db.engine)
        if not inspector.has_table('inventory_items'):
            Item.__table__.create(db.engine)
        if not inspector.has_table('inventory_transactions'):
            Transaction.__table__.create(db.engine)
            
        # Mark the app as installed in user_apps table
        user_app = UserApp.query.filter_by(
            account_id=account_id,
            app_name="inventory"
        ).first()
        
        if not user_app:
            user_app = UserApp(
                account_id=account_id,
                app_name="inventory",
                installed_at=datetime.utcnow(),
                is_installed=True
            )
            db.session.add(user_app)
        else:
            user_app.is_installed = True
            user_app.installed_at = datetime.utcnow()
            user_app.uninstalled_at = None
            
        db.session.commit()
        return True
    except Exception as e:
        print(f"Installation failed: {e}")
        db.session.rollback()
        return False


def uninstall_inventory(account_id):
    """Uninstall the inventory app for a specific account"""
    try:
        # Delete all data for this account
        Transaction.query.filter_by(account_id=account_id).delete()
        Item.query.filter_by(account_id=account_id).delete()
        Category.query.filter_by(account_id=account_id).delete()
            
        # Update user_apps record
        user_app = UserApp.query.filter_by(
            account_id=account_id,
            app_name="inventory"
        ).first()
        
        if user_app:
            user_app.is_installed = False
            user_app.uninstalled_at = datetime.utcnow()
            
        db.session.commit()
        return True
    except Exception as e:
        print(f"Uninstallation failed: {e}")
        db.session.rollback()
        return False 