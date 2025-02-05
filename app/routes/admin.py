from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.user import User
from app.models.app_model import App
from app.models.user_app import UserApp
from app.utils.auth_helpers import admin_required  # Ensure only admin access
from werkzeug.security import generate_password_hash


admin_bp = Blueprint('admin', __name__)

# 1. View all users and their assigned apps
@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    users = User.query.all()
    user_list = []

    for user in users:
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "apps": [{"id": ua.app.id, "name": ua.app.name} for ua in user.user_apps]
        }
        user_list.append(user_data)

    return jsonify({"users": user_list}), 200


# 2. Assign an app to a user
@admin_bp.route('/assign_app', methods=['POST'])
@admin_required
def assign_app():
    data = request.get_json()
    user_id = data.get('user_id')
    app_id = data.get('app_id')

    if not user_id or not app_id:
        return jsonify({"error": "User ID and App ID are required"}), 400

    user = User.query.get(user_id)
    app = App.query.get(app_id)

    if not user or not app:
        return jsonify({"error": "Invalid User ID or App ID"}), 404

    # Check if the user already has the app
    existing_assignment = UserApp.query.filter_by(user_id=user_id, app_id=app_id).first()
    if existing_assignment:
        return jsonify({"message": "User already has this app"}), 200

    # Assign the app to the user
    new_user_app = UserApp(user_id=user_id, app_id=app_id)
    db.session.add(new_user_app)
    db.session.commit()

    return jsonify({"message": f"App '{app.name}' assigned to user '{user.name}'"}), 201


# 3. Remove an app from a user
@admin_bp.route('/remove_app', methods=['DELETE'])
@admin_required
def remove_app():
    data = request.get_json()
    user_id = data.get('user_id')
    app_id = data.get('app_id')

    if not user_id or not app_id:
        return jsonify({"error": "User ID and App ID are required"}), 400

    user_app = UserApp.query.filter_by(user_id=user_id, app_id=app_id).first()

    if not user_app:
        return jsonify({"error": "This app is not assigned to the user"}), 404

    db.session.delete(user_app)
    db.session.commit()

    return jsonify({"message": "App removed successfully"}), 200


@admin_bp.route('/user_apps/<int:user_id>', methods=['GET'])
@admin_required
def get_user_apps(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    user_apps = UserApp.query.filter_by(user_id=user_id).all()
    apps = [{"app_id": ua.app_id, "user_id": ua.user_id} for ua in user_apps]

    return jsonify({"user_id": user_id, "apps": apps})


@admin_bp.route('/users', methods=['POST'])
@admin_required
def create_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")  # Default to "user" if not provided
    account_id = data.get("account_id")  # Add account ID if needed

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "User already exists"}), 409

    # Hash the password
    from werkzeug.security import generate_password_hash
    password_hash = generate_password_hash(password)

    # Create new user
    new_user = User(email=email, password_hash=password_hash, role=role, account_id=account_id)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"User {email} created successfully"}), 201




@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted successfully"}), 200


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    user.email = data.get("email", user.email)
    user.role = data.get("role", user.role)

    if "password" in data:
        from werkzeug.security import generate_password_hash
        user.password_hash = generate_password_hash(data["password"])

    db.session.commit()
    return jsonify({"message": f"User {user.email} updated successfully"}), 200
