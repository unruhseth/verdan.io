from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from app.models.user import User
from app.extensions import db

auth_bp = Blueprint("auth", __name__)

# User Registration
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    existing_user = User.query.filter_by(email=data["email"]).first()
    if existing_user:
        return jsonify({"error": "User already exists"}), 400

    hashed_password = generate_password_hash(data["password"])
    new_user = User(
        account_id=data["account_id"],
        email=data["email"],
        password_hash=hashed_password,
        name=data["name"],
        role="user"
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully!"}), 201

# User Login
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()

    if not user or not check_password_hash(user.password_hash, data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(
        identity=str(user.id),  # Make sure this is a string
        additional_claims={
            "account_id": user.account_id,
            "role": user.role
        }
    )
    return jsonify({"token": token, "role": user.role})


@auth_bp.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    from flask_jwt_extended import get_jwt_identity, get_jwt
    user_id_str = get_jwt_identity()     # This is now a string
    user_id = int(user_id_str)           # Convert to int if needed

    claims = get_jwt()
    account_id = claims["account_id"]
    role = claims["role"]

    return {
        "message": "Welcome!",
        "user_id": user_id,
        "account_id": account_id,
        "role": role
    }, 200

