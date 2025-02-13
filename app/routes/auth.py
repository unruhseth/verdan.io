from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from app.models.user import User
from app.extensions import db
from flask_cors import cross_origin


auth_bp = Blueprint("auth", __name__)

# User Registration
@auth_bp.route("/register", methods=["POST"])
@cross_origin()
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
@cross_origin()
def login():
    try:
        data = request.json
        if not data or "email" not in data or "password" not in data:
            return jsonify({"error": "Email and password are required"}), 400

        user = User.query.filter_by(email=data["email"]).first()

        if not user or not check_password_hash(user.password_hash, data["password"]):
            return jsonify({"error": "Invalid credentials"}), 401

        token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "account_id": user.account_id,
                "role": user.role
            }
        )

        return jsonify({
            "token": token,
            "role": user.role,
            "account_id": user.account_id,
            "name": user.name,
            "email": user.email
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/protected", methods=["GET"])
@cross_origin()
@jwt_required()
def protected():
    try:
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str)
        claims = get_jwt()
        account_id = claims["account_id"]
        role = claims["role"]

        return jsonify({
            "message": "Welcome!",
            "user_id": user_id,
            "account_id": account_id,
            "role": role
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

