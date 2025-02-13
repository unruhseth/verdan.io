from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt

def high_level_admin_required(fn):
    """Decorator for endpoints that should only be accessible by master_admin and admin roles"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        role = claims.get("role", "")

        if role not in ["master_admin", "admin"]:
            return jsonify({"message": "Higher level admin access required"}), 403

        return fn(*args, **kwargs)
    
    return wrapper

def any_admin_required(fn):
    """Decorator for endpoints that can be accessed by any admin role"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        role = claims.get("role", "")

        if role not in ["admin", "account_admin", "master_admin"]:
            return jsonify({"message": "Admin access required"}), 403

        # For account_admin, verify they're accessing their own account
        if role == "account_admin":
            account_id = kwargs.get('account_id')
            user_claims = get_jwt()
            user_account_id = user_claims.get('account_id')
            
            if not account_id or not user_account_id or account_id != user_account_id:
                return jsonify({"message": "Access restricted to your own account"}), 403

        return fn(*args, **kwargs)
    
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()  # ✅ Retrieve full claims instead of just identity
        role = claims.get("role", "")

        if role != "admin":
            return jsonify({"message": "Admin access required"}), 403

        return fn(*args, **kwargs)
    
    return wrapper

def master_admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        role = claims.get("role", "")

        if role != "master_admin":
            return jsonify({"message": "Master admin access required"}), 403

        return fn(*args, **kwargs)
    
    return wrapper

def account_admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        role = claims.get("role", "")

        if role != "account_admin":
            return jsonify({"message": "Account admin access required"}), 403

        return fn(*args, **kwargs)
    
    return wrapper

def user_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        role = claims.get("role", "")

        if role not in ["user", "admin", "master_admin", "account_admin"]:
            return jsonify({"message": "User access required"}), 403

        return fn(*args, **kwargs)
    
    return wrapper
