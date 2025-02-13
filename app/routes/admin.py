from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.user import User
from app.models.app_model import App
from app.models.user_app import UserApp
from app.utils.auth_helpers import any_admin_required, high_level_admin_required
from werkzeug.security import generate_password_hash
from app.models import Account
from flask_jwt_extended import get_jwt
from flask_jwt_extended import jwt_required
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

# # 1. View all users and their assigned apps
# @admin_bp.route('/users', methods=['GET'])
# @admin_required
# def get_all_users():
#     users = User.query.all()
#     user_list = []

#     for user in users:
#         user_data = {
#             "id": user.id,
#             "name": user.name,
#             "email": user.email,
#             "role": user.role,
#             "apps": [{"id": ua.app.id, "name": ua.app.name} for ua in user.user_apps]
#         }
#         user_list.append(user_data)

#     return jsonify({"users": user_list}), 200

@admin_bp.route('/accounts/<int:account_id>/users', methods=['GET'])
@jwt_required()
def get_users_for_account(account_id):
    """Get all users tied to a specific account."""
    # Get the user's role and account_id from JWT claims
    claims = get_jwt()
    user_role = claims.get("role", "")
    user_account_id = claims.get("account_id")

    # Access control based on role
    if user_role not in ["master_admin", "admin", "account_admin", "user"]:
        return jsonify({"error": "Unauthorized"}), 403

    # For non-admin roles, verify they're accessing their own account
    if user_role not in ["master_admin", "admin"] and user_account_id != account_id:
        return jsonify({"error": "You can only view users in your own account"}), 403

    # Get users for the account
    users = User.query.filter_by(account_id=account_id).all()

    # Format response with only the required fields
    user_list = [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
        for user in users
    ]

    return jsonify(user_list), 200


# # 2. Assign an app to a user
# @admin_bp.route('/assign_app', methods=['POST'])
# @admin_required
# def assign_app():
#     data = request.get_json()
#     user_id = data.get('user_id')
#     app_id = data.get('app_id')

#     if not user_id or not app_id:
#         return jsonify({"error": "User ID and App ID are required"}), 400

#     user = User.query.get(user_id)
#     app = App.query.get(app_id)

#     if not user or not app:
#         return jsonify({"error": "Invalid User ID or App ID"}), 404

#     # Check if the user already has the app
#     existing_assignment = UserApp.query.filter_by(user_id=user_id, app_id=app_id).first()
#     if existing_assignment:
#         return jsonify({"message": "User already has this app"}), 200

#     # Assign the app to the user
#     new_user_app = UserApp(user_id=user_id, app_id=app_id)
#     db.session.add(new_user_app)
#     db.session.commit()

#     return jsonify({"message": f"App '{app.name}' assigned to user '{user.name}'"}), 201


# # 3. Remove an app from a user
# @admin_bp.route('/remove_app', methods=['DELETE'])
# @admin_required
# def remove_app():
#     data = request.get_json()
#     user_id = data.get('user_id')
#     app_id = data.get('app_id')

#     if not user_id or not app_id:
#         return jsonify({"error": "User ID and App ID are required"}), 400

#     user_app = UserApp.query.filter_by(user_id=user_id, app_id=app_id).first()

#     if not user_app:
#         return jsonify({"error": "This app is not assigned to the user"}), 404

#     db.session.delete(user_app)
#     db.session.commit()

#     return jsonify({"message": "App removed successfully"}), 200


# @admin_bp.route('/user_apps/<int:user_id>', methods=['GET'])
# @admin_required
# def get_user_apps(user_id):
#     user = User.query.get(user_id)

#     if not user:
#         return jsonify({"error": "User not found"}), 404

#     user_apps = UserApp.query.filter_by(user_id=user_id).all()
#     apps = [{"app_id": ua.app_id, "user_id": ua.user_id} for ua in user_apps]

#     return jsonify({"user_id": user_id, "apps": apps})


@admin_bp.route('/accounts/<int:account_id>/users', methods=['POST'])
@any_admin_required
def create_user(account_id):
    """Create a new user under a specific account."""
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    phone_number = data.get("phone_number")
    password = data.get("password")
    role = data.get("role", "user")

    # Additional role validation for account_admin
    claims = get_jwt()
    if claims.get("role") == "account_admin" and role not in ["user"]:
        return jsonify({"error": "Account admins can only create user roles"}), 403

    if not password:
        return jsonify({"error": "Password is required"}), 400
    
    phone_number = phone_number if phone_number and phone_number.strip() else None
    email = email if email and email.strip() else None

    password_hash = generate_password_hash(password)

    new_user = User(
        account_id=account_id,
        name=name,
        email=email,
        phone_number=phone_number,
        password_hash=password_hash,
        role=role,
    )
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"User {name} created successfully", "id": new_user.id}), 201




@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@any_admin_required
def update_user(user_id):
    """Update user details."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check if account_admin is trying to modify user from different account
    claims = get_jwt()
    if claims.get("role") == "account_admin" and user.account_id != claims.get("account_id"):
        return jsonify({"error": "Cannot modify users from different accounts"}), 403

    data = request.get_json()
    
    # Role validation for account_admin
    new_role = data.get("role")
    if claims.get("role") == "account_admin" and new_role and new_role != "user":
        return jsonify({"error": "Account admins can only manage user roles"}), 403

    user.name = data.get("name", user.name)
    user.email = data.get("email", user.email)
    user.phone_number = data.get("phone_number", user.phone_number)
    user.role = new_role if new_role else user.role

    db.session.commit()
    return jsonify({"message": f"User {user.name} updated successfully"}), 200


@admin_bp.route('/users/<int:user_id>/reset_password', methods=['PUT'])
@any_admin_required
def reset_user_password(user_id):
    """Admin resets a user's password."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check if account_admin is trying to modify user from different account
    claims = get_jwt()
    if claims.get("role") == "account_admin" and user.account_id != claims.get("account_id"):
        return jsonify({"error": "Cannot modify users from different accounts"}), 403

    data = request.get_json()
    new_password = data.get("new_password")

    if not new_password:
        return jsonify({"error": "New password is required"}), 400

    user.password_hash = generate_password_hash(new_password)

    db.session.commit()
    return jsonify({"message": f"Password reset successfully for {user.email}"}), 200



@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@any_admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check if account_admin is trying to delete user from different account
    claims = get_jwt()
    if claims.get("role") == "account_admin":
        if user.account_id != claims.get("account_id"):
            return jsonify({"error": "Cannot delete users from different accounts"}), 403
        if user.role != "user":
            return jsonify({"error": "Account admins can only delete user roles"}), 403

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted successfully"}), 200


# @admin_bp.route('/users/<int:user_id>', methods=['PUT'])
# @admin_required
# def update_user(user_id):
#     user = User.query.get(user_id)
#     if not user:
#         return jsonify({"error": "User not found"}), 404

#     data = request.get_json()
#     user.email = data.get("email", user.email)
#     user.role = data.get("role", user.role)

#     if "password" in data:
#         from werkzeug.security import generate_password_hash
#         user.password_hash = generate_password_hash(data["password"])

#     db.session.commit()
#     return jsonify({"message": f"User {user.email} updated successfully"}), 200



@admin_bp.route('/accounts', methods=['GET'])
@high_level_admin_required
def get_all_accounts():
    """Get a list of all accounts in the system."""
    accounts = Account.query.all()

    account_list = [
        {"id": acc.id, "name": acc.name, "created_at": acc.created_at}
        for acc in accounts
    ]

    return jsonify(account_list), 200

@admin_bp.route('/accounts/<int:account_id>', methods=['GET'])
@high_level_admin_required
def get_account(account_id):
    """Fetch details of a single account."""
    account = Account.query.get(account_id)

    if not account:
        return jsonify({"error": "Account not found"}), 404

    account_data = {
        "id": account.id,
        "name": account.name,
        "created_at": account.created_at,
    }

    return jsonify(account_data), 200

@admin_bp.route('/apps', methods=['GET'])
@high_level_admin_required
def get_all_apps():
    """Get a list of all applications in the system (high-level admin access only)"""
    apps = App.query.all()
    return jsonify([{
        "id": app.app_key,
        "name": app.name,
        "description": app.description,
        "icon_url": app.icon_url
    } for app in apps]), 200

@admin_bp.route('/accounts/<int:account_id>/apps', methods=['GET'])
@any_admin_required
def get_account_apps(account_id):
    """Get all apps (installed and available) for a specific account"""
    # Get all available apps
    all_apps = App.query.all()
    
    # Get installed apps for this account
    installed_apps = (
        db.session.query(UserApp)
        .filter(
            UserApp.account_id == account_id,
            UserApp.is_installed == True
        )
        .all()
    )
    
    # Create a set of installed app keys for quick lookup
    installed_app_keys = {ua.app_name for ua in installed_apps}
    
    # Format response with installation status
    app_list = []
    for app in all_apps:
        app_data = app.to_admin_dict()
        app_data['is_installed'] = app.app_key in installed_app_keys
        app_list.append(app_data)
    
    return jsonify(app_list), 200

@admin_bp.route('/accounts/<int:account_id>/apps/install', methods=['POST'])
@high_level_admin_required
def install_app_for_account(account_id):
    """Install an app for a specific account"""
    data = request.get_json()
    
    if not data or 'app_id' not in data:
        return jsonify({"error": "app_id is required"}), 400
        
    app_id = data['app_id']
    
    # Check if app exists
    app = App.query.filter_by(app_key=app_id, is_active=True).first()
    if not app:
        return jsonify({"error": "App not found or inactive"}), 404
    
    # Check if already installed
    existing_install = UserApp.query.filter_by(
        account_id=account_id,
        app_name=app_id
    ).first()
    
    if existing_install and existing_install.is_installed:
        return jsonify({"message": "App already installed"}), 200
    
    try:
        # Dynamically import and call the install function
        try:
            module = __import__(f'app.apps.{app_id}.install', fromlist=[''])
            install_func = getattr(module, f'install_{app_id}')
        except (ImportError, AttributeError) as e:
            return jsonify({"error": f"App installation module not found: {str(e)}"}), 500
        
        # Call the app's install function
        success = install_func(account_id)
        
        if success:
            # Update or create UserApp record
            if not existing_install:
                user_app = UserApp(
                    account_id=account_id,
                    app_name=app_id,
                    installed_at=datetime.utcnow(),
                    is_installed=True
                )
                db.session.add(user_app)
            else:
                existing_install.is_installed = True
                existing_install.installed_at = datetime.utcnow()
                existing_install.uninstalled_at = None
            
            db.session.commit()
            return jsonify({"message": "App installed successfully"}), 200
        else:
            return jsonify({"error": "Installation failed"}), 500
            
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Installation failed: {str(e)}"}), 500

@admin_bp.route('/accounts/<int:account_id>/apps/installed', methods=['GET'])
@any_admin_required
def get_account_installed_apps(account_id):
    """Get only installed apps for a specific account"""
    # Get installed apps for this account
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
    
    # Format response with only required fields
    app_list = [{
        "id": app.app_key,
        "name": app.name,
        "icon_url": app.icon_url
    } for app in installed_apps]
    
    return jsonify(app_list), 200

@admin_bp.route('/accounts/<int:account_id>/apps/uninstall', methods=['POST'])
@high_level_admin_required
def uninstall_app_for_account(account_id):
    """Uninstall an app for a specific account"""
    data = request.get_json()
    
    if not data or 'app_id' not in data:
        return jsonify({"error": "app_id is required"}), 400
        
    app_id = data['app_id']
    
    # Check if app exists and is installed
    user_app = UserApp.query.filter_by(
        account_id=account_id,
        app_name=app_id,
        is_installed=True
    ).first()
    
    if not user_app:
        return jsonify({"error": "App not installed"}), 404
    
    try:
        # Dynamically import and call the uninstall function
        try:
            module = __import__(f'app.apps.{app_id}.install', fromlist=[''])
            uninstall_func = getattr(module, f'uninstall_{app_id}')
        except (ImportError, AttributeError) as e:
            return jsonify({"error": f"App uninstallation module not found: {str(e)}"}), 500
        
        # Call the app's uninstall function
        success = uninstall_func(account_id)
        
        if success:
            user_app.is_installed = False
            user_app.uninstalled_at = datetime.utcnow()
            db.session.commit()
            return jsonify({"message": "App uninstalled successfully"}), 200
        else:
            return jsonify({"error": "Uninstallation failed"}), 500
            
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Uninstallation failed: {str(e)}"}), 500

@admin_bp.route('/apps/<string:app_id>', methods=['DELETE'])
@high_level_admin_required
def delete_app(app_id):
    """Delete an app from the system entirely"""
    try:
        # First check if the app exists
        app = App.query.filter_by(app_key=app_id).first()
        if not app:
            return jsonify({"error": "App not found"}), 404

        # Get all installations of this app
        installations = UserApp.query.filter_by(app_name=app_id).all()
        
        # Remove all installations
        for installation in installations:
            db.session.delete(installation)
        
        # Remove the app itself
        db.session.delete(app)
        db.session.commit()
        
        return jsonify({
            "message": f"App '{app.name}' and all its installations have been removed from the system"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete app: {str(e)}"}), 500
