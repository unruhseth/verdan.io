from flask import Flask, request
from .config import Config
from .extensions import db, migrate, jwt
from flask_cors import CORS, cross_origin
from .utils.app_scanner import scan_and_register_apps



def create_app():
    app = Flask(__name__, subdomain_matching=True)
    app.config.from_object(Config)
    
    # Update CORS configuration using config values
    CORS(app, 
         resources={r"/*": {
             "origins": app.config['CORS_ORIGINS'],
             "methods": app.config['CORS_METHODS'],
             "allow_headers": app.config['CORS_ALLOWED_HEADERS'],
             "supports_credentials": app.config['CORS_SUPPORTS_CREDENTIALS']
         }})

    # Import all models first
    from app.models.account import Account
    from app.models.user import User
    from app.models.app_model import App
    from app.models.user_app import UserApp
    from app.apps.multi_control.models import (
        Field, Equipment, Zone, IrrigationPlan,
        Alert, Log, Firmware
    )
    from app.apps.inventory.models import create_app_tables

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Import and register blueprints
    from app.routes.auth import auth_bp
    from app.routes.accounts import account_bp
    from app.routes.admin import admin_bp
    from app.routes.apps import apps_bp
    from app.apps.task_manager.routes import task_bp
    from app.apps.multi_control.routes import multi_control_bp
    from app.apps.inventory.routes import inventory_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(account_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(apps_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(multi_control_bp)
    app.register_blueprint(inventory_bp)

    # Scan and register installed apps
    with app.app_context():
        scan_and_register_apps()

    return app

