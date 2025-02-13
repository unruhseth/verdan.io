from flask import Blueprint, request, jsonify
from app.models.account import Account
from app.models.user import User
from app.extensions import db
from app.utils.auth_helpers import high_level_admin_required, any_admin_required
from flask_jwt_extended import jwt_required, get_jwt
from werkzeug.security import generate_password_hash

account_bp = Blueprint("accounts", __name__, url_prefix="/accounts")

# Account Management (High-Level Admin Only)
@account_bp.route("/", methods=["POST"])
@high_level_admin_required
def create_account():
    """Create a new account (high-level admin only)"""
    data = request.json

    # Check if account with same name or subdomain already exists
    existing_account = Account.query.filter(
        (Account.name == data["name"]) | (Account.subdomain == data["subdomain"])
    ).first()

    if existing_account:
        error_field = "name" if existing_account.name == data["name"] else "subdomain"
        return jsonify({
            "error": f"An account with this {error_field} already exists",
            "field": error_field
        }), 409

    new_account = Account(
        name=data["name"],
        subdomain=data["subdomain"]
    )
    db.session.add(new_account)
    db.session.commit()
    return jsonify({"message": "Account created successfully", "id": new_account.id}), 201

@account_bp.route("/<int:account_id>", methods=["PUT"])
@high_level_admin_required
def update_account(account_id):
    """Update account details (high-level admin only)"""
    account = Account.query.get(account_id)
    
    if not account:
        return jsonify({"error": "Account not found"}), 404
    
    data = request.json
    
    if "name" in data:
        account.name = data["name"]
    if "subdomain" in data:
        account.subdomain = data["subdomain"]
    
    db.session.commit()
    return jsonify({
        "message": "Account updated successfully",
        "account": {
            "id": account.id,
            "name": account.name,
            "subdomain": account.subdomain,
            "created_at": account.created_at
        }
    }), 200

@account_bp.route("/<int:account_id>", methods=["DELETE"])
@high_level_admin_required
def delete_account(account_id):
    """Delete an account (high-level admin only)"""
    account = Account.query.get(account_id)
    
    if not account:
        return jsonify({"error": "Account not found"}), 404
    
    db.session.delete(account)
    db.session.commit()
    
    return jsonify({"message": "Account deleted successfully"}), 200

# User Management
@account_bp.route('/<int:account_id>/users', methods=['GET'])
@jwt_required()
def list_account_users(account_id):
    """List users in an account (accessible by all roles with proper access)"""
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

@account_bp.route('/<int:account_id>/users', methods=['POST'])
@any_admin_required
def create_account_user(account_id):
    """Create a new user in an account (admin only)"""
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    phone_number = data.get("phone_number")
    password = data.get("password")
    role = data.get("role", "user")

    # Additional role validation for account_admin
    claims = get_jwt()
    if claims.get("role") == "account_admin":
        if account_id != claims.get("account_id"):
            return jsonify({"error": "Cannot create users in other accounts"}), 403
        if role != "user":
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

@account_bp.route('/<int:account_id>/users/<int:user_id>', methods=['PUT'])
@any_admin_required
def update_account_user(account_id, user_id):
    """Update user details (admin only)"""
    user = User.query.get(user_id)
    if not user or user.account_id != account_id:
        return jsonify({"error": "User not found"}), 404

    # Check if account_admin is trying to modify user from different account
    claims = get_jwt()
    if claims.get("role") == "account_admin" and account_id != claims.get("account_id"):
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

@account_bp.route('/<int:account_id>/users/<int:user_id>/reset-password', methods=['PUT'])
@any_admin_required
def reset_account_user_password(account_id, user_id):
    """Reset user password (admin only)"""
    user = User.query.get(user_id)
    if not user or user.account_id != account_id:
        return jsonify({"error": "User not found"}), 404

    # Check if account_admin is trying to modify user from different account
    claims = get_jwt()
    if claims.get("role") == "account_admin" and account_id != claims.get("account_id"):
        return jsonify({"error": "Cannot modify users from different accounts"}), 403

    data = request.get_json()
    new_password = data.get("new_password")

    if not new_password:
        return jsonify({"error": "New password is required"}), 400

    user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"message": f"Password reset successfully for {user.email}"}), 200

@account_bp.route('/<int:account_id>/users/<int:user_id>', methods=['DELETE'])
@any_admin_required
def delete_account_user(account_id, user_id):
    """Delete a user (admin only)"""
    user = User.query.get(user_id)
    if not user or user.account_id != account_id:
        return jsonify({"error": "User not found"}), 404

    # Check if account_admin is trying to delete user from different account
    claims = get_jwt()
    if claims.get("role") == "account_admin":
        if account_id != claims.get("account_id"):
            return jsonify({"error": "Cannot delete users from different accounts"}), 403
        if user.role != "user":
            return jsonify({"error": "Account admins can only delete user roles"}), 403

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted successfully"}), 200 