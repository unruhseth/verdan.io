from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.app_model import App
from app.models.user_app import UserApp
from app.utils.auth_helpers import user_required

apps_bp = Blueprint('apps', __name__, url_prefix='/apps')

@apps_bp.route('/available', methods=['GET'])
@user_required
def get_available_apps():
    """Get all available applications in the system"""
    apps = App.query.filter_by(is_active=True).all()
    return jsonify([app.to_dict() for app in apps]), 200

@apps_bp.route('/installed', methods=['GET'])
@user_required
def get_installed_apps():
    """Get all installed applications for a specific account"""
    account_id = request.args.get('account_id')
    
    if not account_id:
        return jsonify({"error": "Account ID is required"}), 400
        
    try:
        account_id = int(account_id)
    except ValueError:
        return jsonify({"error": "Account ID must be a valid integer"}), 400
    
    # Get all installed apps for the account
    installed_apps = (
        db.session.query(App)
        .join(UserApp, App.app_key == UserApp.app_name)
        .filter(
            UserApp.account_id == account_id,
            UserApp.is_installed == True,
            App.is_active == True
        )
        .all()
    )
    
    return jsonify([app.to_dict() for app in installed_apps]), 200 