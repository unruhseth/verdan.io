from flask import Blueprint, request, jsonify
from app.extensions import db
from .models import create_app_tables
from .install import install_app_name, uninstall_app_name
from app.utils.auth_helpers import any_admin_required
import logging

# Replace 'app_name' with your app's name
app_name_bp = Blueprint("app_name", __name__, url_prefix="/app_name")
logger = logging.getLogger(__name__)


@app_name_bp.route("/install", methods=["POST"])
@any_admin_required
def install_app():
    """Install this app for an account"""
    data = request.json
    account_id = data.get("account_id")
    if not account_id:
        return jsonify({"error": "Account ID is required"}), 400
    
    if install_app_name(account_id):
        return jsonify({"message": "App installed successfully"}), 200
    else:
        return jsonify({"error": "Installation failed"}), 400


@app_name_bp.route("/uninstall", methods=["POST"])
@any_admin_required
def uninstall_app():
    """Uninstall this app for an account"""
    data = request.json
    account_id = data.get("account_id")
    if not account_id:
        return jsonify({"error": "Account ID is required"}), 400
    
    if uninstall_app_name(account_id):
        return jsonify({"message": "App uninstalled successfully"}), 200
    else:
        return jsonify({"error": "Uninstallation failed"}), 400


# Add your app-specific routes below 