from app import create_app
from app.extensions import db
from app.models.user_app import UserApp
from datetime import datetime
import importlib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AppInstaller:
    def __init__(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def install_app(self, app_name: str, account_id: int):
        """
        Install a specific app for an account
        
        Args:
            app_name: The name of the app to install (e.g., 'multi_control', 'task_manager')
            account_id: The ID of the account to install the app for
        """
        try:
            # Import the app's install module
            install_module = importlib.import_module(f'app.apps.{app_name}.install')
            install_func = getattr(install_module, f'install_{app_name}')
            
            # Check if app is already installed
            existing_app = UserApp.query.filter_by(
                account_id=account_id,
                app_name=app_name
            ).first()
            
            if existing_app and existing_app.is_installed:
                logger.info(f"App {app_name} is already installed for account {account_id}")
                return True

            # Run the app's install function
            success = install_func(account_id)
            
            if success:
                # Create or update UserApp record
                if not existing_app:
                    user_app = UserApp(
                        account_id=account_id,
                        app_name=app_name,
                        is_installed=True,
                        installed_at=datetime.utcnow()
                    )
                    db.session.add(user_app)
                else:
                    existing_app.is_installed = True
                    existing_app.installed_at = datetime.utcnow()
                    existing_app.uninstalled_at = None
                
                db.session.commit()
                logger.info(f"Successfully installed {app_name} for account {account_id}")
                return True
            else:
                logger.error(f"Failed to install {app_name} for account {account_id}")
                return False
                
        except ImportError:
            logger.error(f"App {app_name} not found in the apps directory")
            return False
        except AttributeError:
            logger.error(f"Install function not found for app {app_name}")
            return False
        except Exception as e:
            logger.error(f"Error installing {app_name}: {str(e)}")
            db.session.rollback()
            return False

    def uninstall_app(self, app_name: str, account_id: int):
        """
        Uninstall a specific app for an account
        """
        try:
            # Import the app's install module
            install_module = importlib.import_module(f'app.apps.{app_name}.install')
            uninstall_func = getattr(install_module, f'uninstall_{app_name}')
            
            # Check if app is installed
            existing_app = UserApp.query.filter_by(
                account_id=account_id,
                app_name=app_name
            ).first()
            
            if not existing_app or not existing_app.is_installed:
                logger.info(f"App {app_name} is not installed for account {account_id}")
                return True

            # Run the app's uninstall function
            success = uninstall_func(account_id)
            
            if success:
                existing_app.is_installed = False
                existing_app.uninstalled_at = datetime.utcnow()
                db.session.commit()
                logger.info(f"Successfully uninstalled {app_name} for account {account_id}")
                return True
            else:
                logger.error(f"Failed to uninstall {app_name} for account {account_id}")
                return False
                
        except ImportError:
            logger.error(f"App {app_name} not found in the apps directory")
            return False
        except AttributeError:
            logger.error(f"Uninstall function not found for app {app_name}")
            return False
        except Exception as e:
            logger.error(f"Error uninstalling {app_name}: {str(e)}")
            db.session.rollback()
            return False

    def __del__(self):
        self.app_context.pop() 