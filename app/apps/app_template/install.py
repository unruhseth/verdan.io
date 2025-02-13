from app.extensions import db
from .models import create_app_tables
from app.models.user_app import UserApp
from sqlalchemy import text, inspect
from datetime import datetime


def install_app_name(account_id):
    """Install this app for a specific account"""
    try:
        # Create any account-specific tables
        tables = create_app_tables(account_id)
        
        inspector = inspect(db.engine)
        
        # Create each table if it doesn't exist
        for table_name, table_model in tables.items():
            if not inspector.has_table(table_name):
                table_model.__table__.create(db.engine)
            
        # Mark the app as installed in user_apps table
        user_app = UserApp.query.filter_by(
            account_id=account_id,
            app_name="app_name"  # Replace with your app name
        ).first()
        
        if not user_app:
            user_app = UserApp(
                account_id=account_id,
                app_name="app_name",  # Replace with your app name
                installed_at=datetime.utcnow()
            )
            db.session.add(user_app)
            db.session.commit()

        return True
    except Exception as e:
        print(f"Installation failed: {e}")
        return False


def uninstall_app_name(account_id):
    """Uninstall this app for a specific account"""
    try:
        # Get the tables for this account
        tables = create_app_tables(account_id)
        
        # Drop each table
        for table_name, table_model in tables.items():
            table_model.__table__.drop(db.engine)
            
        # Update user_apps record
        user_app = UserApp.query.filter_by(
            account_id=account_id,
            app_name="app_name"  # Replace with your app name
        ).first()
        
        if user_app:
            user_app.is_installed = False
            user_app.uninstalled_at = datetime.utcnow()
            db.session.commit()

        return True
    except Exception as e:
        print(f"Uninstallation failed: {e}")
        return False 