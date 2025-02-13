import os
from app.extensions import db
from app.models.app_model import App

def is_valid_app_directory(path):
    """
    Check if a directory is a valid Flask app by looking for required files.
    A valid app directory must have at least routes.py or __init__.py
    """
    required_files = ['routes.py', '__init__.py']
    directory_files = os.listdir(path)
    return any(file in directory_files for file in required_files)

def format_app_name(directory_name):
    """Convert directory name to a proper app name"""
    # Convert snake_case to Title Case
    return ' '.join(word.capitalize() for word in directory_name.split('_'))

def scan_and_register_apps():
    """
    Scan the /apps/ directory and register any new apps in the database.
    This function should be called when the Flask app starts.
    """
    try:
        # Get the absolute path to the apps directory
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        apps_dir = os.path.join(current_dir, 'apps')
        
        # Scan for app directories
        for item in os.listdir(apps_dir):
            item_path = os.path.join(apps_dir, item)
            
            # Skip if not a directory or not a valid app directory
            if not os.path.isdir(item_path) or not is_valid_app_directory(item_path):
                continue
                
            app_name = format_app_name(item)
            app_key = item.lower()  # Use directory name as app_key
            
            # Check if app already exists
            existing_app = App.query.filter_by(app_key=app_key).first()
            if not existing_app:
                # Create new app record
                new_app = App(
                    name=app_name,
                    description="No description available.",
                    icon_url=None,
                    app_key=app_key,
                    is_active=True
                )
                db.session.add(new_app)
        
        db.session.commit()
        print(f"Successfully scanned and registered apps from {apps_dir}")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"Error scanning and registering apps: {str(e)}")
        return False 