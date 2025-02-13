from app.extensions import db
from .models import create_task_model
from app.models.user_app import UserApp
from sqlalchemy import text, inspect
from datetime import datetime

def install_task_manager(account_id):
    """Install the task manager app for a specific account"""
    try:
        # Create the task model for this account
        TaskModel = create_task_model(account_id)
        
        # Create the table if it doesn't exist
        inspector = inspect(db.engine)
        table_name = f"tasks_{account_id}"
        
        if not inspector.has_table(table_name):
            # The TaskStatus enum already exists, so we can create the table directly
            TaskModel.__table__.create(db.engine)
            
        # Mark the app as installed in user_apps table
        user_app = UserApp.query.filter_by(
            account_id=account_id,
            app_name="task_manager"
        ).first()
        
        if not user_app:
            user_app = UserApp(
                account_id=account_id,
                app_name="task_manager",
                is_installed=True
            )
            db.session.add(user_app)
        else:
            user_app.is_installed = True
            user_app.uninstalled_at = None  # Clear any previous uninstall timestamp
            
        db.session.commit()
            
        return True, "Task Manager installed successfully"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def uninstall_task_manager(account_id):
    """Uninstall the task manager app for a specific account while preserving data"""
    try:
        # Update the user_apps table
        user_app = UserApp.query.filter_by(
            account_id=account_id,
            app_name="task_manager"
        ).first()
        
        if user_app:
            user_app.is_installed = False
            user_app.uninstalled_at = datetime.utcnow()
            db.session.commit()
            
        return True, "Task Manager uninstalled successfully. Data will be retained for 1 year."
    except Exception as e:
        db.session.rollback()
        return False, str(e) 