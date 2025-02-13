#!/usr/bin/env python
import os
import shutil
import yaml
import click
import re
from pathlib import Path
from app import create_app
from app.extensions import db
from app.models.app_model import App
from datetime import datetime
import importlib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIAppImporter:
    def __init__(self, source_dir: str, api_dir: str = None):
        self.source_dir = Path(source_dir)
        self.api_dir = Path(api_dir) if api_dir else Path('app/apps')
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def validate_app_structure(self) -> bool:
        """Validate the source app has all required files"""
        required_files = [
            '__init__.py',
            'models.py',
            'routes.py',
            'services.py',
            'install.py',
            'app.yaml'
        ]
        
        for file in required_files:
            if not (self.source_dir / file).exists():
                logger.error(f"Missing required file: {file}")
                return False
                
        # Validate app.yaml structure
        config = self.load_config()
        if not config:
            return False
            
        required_fields = ['name', 'title', 'version']
        for field in required_fields:
            if field not in config['app']:
                logger.error(f"Missing required field in app.yaml: {field}")
                return False
        
        return True

    def load_config(self) -> dict:
        """Load app configuration from app.yaml"""
        config_path = self.source_dir / 'app.yaml'
        try:
            with open(config_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading app.yaml: {e}")
            return {}

    def register_app_in_system(self, config: dict) -> bool:
        """Register the app in the database"""
        try:
            app_name = config['app']['name']
            existing_app = App.query.filter_by(app_key=app_name).first()
            
            if existing_app:
                logger.info(f"Updating existing app: {app_name}")
                existing_app.title = config['app']['title']
                existing_app.description = config['app'].get('description', '')
                existing_app.version = config['app'].get('version', '1.0.0')
                existing_app.monthly_price = config['app'].get('pricing', {}).get('monthly', 0)
                existing_app.yearly_price = config['app'].get('pricing', {}).get('yearly', 0)
                existing_app.updated_at = datetime.utcnow()
            else:
                logger.info(f"Registering new app: {app_name}")
                new_app = App(
                    app_key=app_name,
                    title=config['app']['title'],
                    description=config['app'].get('description', ''),
                    version=config['app'].get('version', '1.0.0'),
                    monthly_price=config['app'].get('pricing', {}).get('monthly', 0),
                    yearly_price=config['app'].get('pricing', {}).get('yearly', 0),
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(new_app)
            
            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Error registering app: {str(e)}")
            db.session.rollback()
            return False

    def copy_app_files(self, app_name: str):
        """Copy app files to the API directory"""
        target_dir = self.api_dir / app_name
        
        # Remove existing directory if it exists
        if target_dir.exists():
            shutil.rmtree(target_dir)
        
        # Copy app files
        shutil.copytree(self.source_dir, target_dir)
        logger.info(f"Copied app files to {target_dir}")

    def update_init_file(self, app_name: str):
        """Update __init__.py to register the blueprint"""
        init_file = Path('app/__init__.py')
        if not init_file.exists():
            logger.error("Could not find app/__init__.py")
            return False
        
        with open(init_file) as f:
            content = f.read()
        
        # Add import statement if not present
        import_line = f"from app.apps.{app_name}.routes import {app_name}_bp"
        if import_line not in content:
            import_section = content.find("# Import and register blueprints")
            if import_section == -1:
                import_section = content.find("from app.routes")
            
            content = content[:import_section] + import_line + "\n" + content[import_section:]
        
        # Add blueprint registration if not present
        register_line = f"app.register_blueprint({app_name}_bp)"
        if register_line not in content:
            register_section = content.find("# Register blueprints")
            if register_section == -1:
                register_section = content.find("app.register_blueprint(")
            
            while content[register_section-1] != "\n":
                register_section = content.find("app.register_blueprint(", register_section + 1)
            
            content = content[:register_section] + register_line + "\n" + content[register_section:]
        
        with open(init_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Updated __init__.py to register {app_name}_bp")
        return True

    def import_app(self) -> bool:
        """Import the app into the API"""
        try:
            # Validate app structure
            if not self.validate_app_structure():
                return False
            
            # Load configuration
            config = self.load_config()
            if not config:
                return False
            
            app_name = config['app']['name']
            
            # Copy app files
            self.copy_app_files(app_name)
            
            # Register app in database
            if not self.register_app_in_system(config):
                return False
            
            # Update __init__.py
            if not self.update_init_file(app_name):
                return False
            
            logger.info(f"Successfully imported app: {app_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing app: {str(e)}")
            return False

    def __del__(self):
        """Clean up app context"""
        try:
            self.app_context.pop()
        except:
            pass

@click.command()
@click.argument('source_dir', type=click.Path(exists=True))
@click.option('--api-dir', type=click.Path(), help='Path to the API directory')
@click.option('--force', is_flag=True, help='Force overwrite existing app')
@click.option('--dry-run', is_flag=True, help='Test import without making changes')
def import_app(source_dir, api_dir, force, dry_run):
    """Import an app into the Verdan API"""
    logger.info(f"Importing app from {source_dir}")
    
    importer = APIAppImporter(source_dir, api_dir)
    
    if dry_run:
        logger.info("Dry run - no changes will be made")
        valid = importer.validate_app_structure()
        config = importer.load_config()
        logger.info(f"App validation: {'Success' if valid else 'Failed'}")
        logger.info(f"Config validation: {'Success' if config else 'Failed'}")
        return
    
    success = importer.import_app()
    if success:
        logger.info("App import completed successfully")
    else:
        logger.error("App import failed")
        exit(1)

if __name__ == '__main__':
    import_app() 