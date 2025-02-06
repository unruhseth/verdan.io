from flask import Flask, request
from .config import Config
from .extensions import db, migrate, jwt


def create_app():
    app = Flask(__name__, subdomain_matching=True)
    app.config.from_object(Config)
    app.config['SERVER_NAME'] = 'localhost:5000'

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Ensure models are correctly imported after initializing the app context
    from app.models.account import Account
    from app.models.user import User
    from app.models.app_model import App  # Updated import
    from app.models.user_app import UserApp

    # Ensure blueprints are imported after initializing the app context
    from app.routes.auth import auth_bp
    from app.routes.account import account_bp
    from app.routes.admin import admin_bp  # Import the new admin routes
    from app.routes.device import device_bp
    from app.routes.sim_card import sim_card_bp  # Import SIM card routes
    from app.routes.device_groups import device_groups_bp
    from app.routes.ota_update import ota_bp
    from app.routes.subscription import subscription_bp
    from app.routes.stripe_routes import stripe_bp





    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(account_bp, url_prefix="/account")
    app.register_blueprint(admin_bp, url_prefix="/admin")  # Add admin routes
    app.register_blueprint(device_bp, url_prefix="/devices")
    app.register_blueprint(sim_card_bp, url_prefix="")  # No prefix needed
    app.register_blueprint(device_groups_bp)
    app.register_blueprint(ota_bp)
    app.register_blueprint(subscription_bp)
    app.register_blueprint(stripe_bp)





   
    

    return app

