from app.extensions import db
from .models import create_multi_control_model, create_enum_type
from app.models.user_app import UserApp
from sqlalchemy import text, inspect
from datetime import datetime


def install_multi_control(account_id):
    """Install the multi control app for a specific account"""
    try:
        # Create enum type first
        create_enum_type()
        
        # Create the model and table
        MultiControlModel = create_multi_control_model(account_id)
        
        inspector = inspect(db.engine)
        table_name = f"multi_controls_{account_id}"
        
        if not inspector.has_table(table_name):
            MultiControlModel.__table__.create(db.engine)
            
        # Mark the app as installed in user_apps table
        user_app = UserApp.query.filter_by(
            account_id=account_id,
            app_name="multi_control"
        ).first()
        
        if not user_app:
            user_app = UserApp(
                account_id=account_id,
                app_name="multi_control",
                installed_at=datetime.utcnow(),
                is_installed=True
            )
            db.session.add(user_app)
        else:
            user_app.is_installed = True
            user_app.installed_at = datetime.utcnow()
            user_app.uninstalled_at = None
            db.session.add(user_app)
            db.session.commit()

        return True
    except Exception as e:
        print(f"Installation failed: {e}")
        db.session.rollback()
        return False


def uninstall_multi_control(account_id):
    """Uninstall the multi control app for a specific account"""
    try:
        # To be implemented: Remove the table and update user_apps if needed
        return True
    except Exception as e:
        print(f"Uninstallation failed: {e}")
        return False 