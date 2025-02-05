from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt

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
