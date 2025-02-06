from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from datetime import datetime
from app.models import User, Subscription
from app.utils.auth_helpers import admin_required
from app.extensions import db
from app.models.app_model import App
from datetime import datetime, timedelta


# Create Blueprint for subscriptions
subscription_bp = Blueprint("subscription", __name__)

# -----------------------------------
# 🚀 USER SUBSCRIPTION ROUTES
# -----------------------------------

@subscription_bp.route("/subscription/start", methods=["POST"])
@jwt_required()
def start_subscription():
    user_id = get_jwt_identity()  
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if user.subscription_status == "Active":
        return jsonify({"message": "Subscription is already active"}), 400

    # Create new subscription
    new_subscription = Subscription(
        user_id=user.id,
        status="Active",
        type=user.subscription_type,  
        price=10.00,  # Default price (Admins can modify)
        created_at=datetime.utcnow()
    )

    db.session.add(new_subscription)
    db.session.commit()

    return jsonify({"message": "Subscription started successfully!"}), 201


@subscription_bp.route("/subscription/pause", methods=["POST"])
@jwt_required()
def pause_subscription():
    data = request.json
    user_id = get_jwt_identity()
    app_id = data.get("app_id")  # Get the app ID from request JSON

    subscription = Subscription.query.filter_by(user_id=user_id, app_id=app_id).first()

    if not subscription or subscription.status != "Active":
        return jsonify({"error": "No active subscription found for this app"}), 400

    subscription.status = "Paused"
    db.session.commit()

    return jsonify({"message": f"Subscription for app {app_id} paused successfully!"})


@subscription_bp.route("/subscription/resume", methods=["POST"])
@jwt_required()
def resume_subscription():
    data = request.json
    user_id = get_jwt_identity()
    app_id = data.get("app_id")  # Get the app ID from request JSON

    subscription = Subscription.query.filter_by(user_id=user_id, app_id=app_id).first()

    if not subscription or subscription.status != "Paused":
        return jsonify({"error": "No paused subscription found for this app"}), 400

    subscription.status = "Active"
    db.session.commit()

    return jsonify({"message": f"Subscription for app {app_id} resumed successfully!"})


@subscription_bp.route("/subscription/status", methods=["GET"])
@jwt_required()
def get_subscription_status():
    user_id = get_jwt_identity()
    app_id = request.args.get("app_id", type=int)  # Get app_id from query params

    subscription = Subscription.query.filter_by(user_id=user_id, app_id=app_id).first()

    if not subscription:
        return jsonify({"error": "No subscription found for this app"}), 404

    return jsonify({
        "subscription_status": subscription.status,
        "subscription_type": subscription.subscription_type
    })


@subscription_bp.route("/subscription/user/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user_subscriptions(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    subscriptions = Subscription.query.filter_by(user_id=user_id).all()
    return jsonify([sub.to_dict() for sub in subscriptions]), 200


@subscription_bp.route("/subscription/list", methods=["GET"])
@jwt_required()
def get_user_subscriptions_list():
    user_id = get_jwt_identity()
    user_subscriptions = Subscription.query.filter_by(user_id=user_id).all()

    if not user_subscriptions:
        return jsonify({"message": "No subscriptions found"}), 404

    subscription_list = []
    for sub in user_subscriptions:
        app = App.query.get(sub.app_id)
        subscription_list.append({
            "subscription_id": sub.id,
            "app_name": app.name if app else "Unknown",
            "subscription_type": sub.subscription_type,
            "status": sub.status,
            "price": sub.custom_price,
            "billing_cycle": sub.billing_cycle,
            "next_billing_date": sub.next_billing_date,
            "created_at": sub.created_at,
            "updated_at": sub.updated_at
        })

    return jsonify(subscription_list), 200

# -----------------------------------
# 👑 ADMIN SUBSCRIPTION ROUTES
# -----------------------------------

@subscription_bp.route("/admin/subscription/pause", methods=["POST"])
@jwt_required()
@admin_required
def admin_pause_subscription():
    data = request.json
    user_id = data.get("user_id")
    app_id = data.get("app_id")

    subscription = Subscription.query.filter_by(user_id=user_id, app_id=app_id).first()

    if not subscription or subscription.status != "Active":
        return jsonify({"error": "No active subscription found for this app"}), 400

    subscription.status = "Paused"
    db.session.commit()

    return jsonify({"message": "Subscription paused successfully by admin!"})



@subscription_bp.route("/admin/subscription/cancel", methods=["POST"])
@jwt_required()
@admin_required
def admin_cancel_subscription():
    data = request.json
    user_id = data.get("user_id")
    app_id = data.get("app_id")

    subscription = Subscription.query.filter_by(user_id=user_id, app_id=app_id).first()

    if not subscription:
        return jsonify({"error": "Subscription not found for this app"}), 404

    subscription.status = "Canceled"
    db.session.commit()

    return jsonify({"message": f"Subscription for user {user_id} on app {app_id} has been canceled!"})



@subscription_bp.route("/admin/subscription/price", methods=["POST"])
@jwt_required()
@admin_required
def admin_update_subscription_price():
    data = request.json
    user_id = data.get("user_id")
    app_id = data.get("app_id")
    new_price = data.get("price")

    if not new_price or new_price <= 0:
        return jsonify({"error": "Invalid price"}), 400

    subscription = Subscription.query.filter_by(user_id=user_id, app_id=app_id).first()

    if not subscription:
        return jsonify({"error": "Subscription not found"}), 404

    subscription.custom_price = new_price  # Make sure the column name is correct
    db.session.commit()

    return jsonify({
        "message": f"Subscription price for user {user_id} on app {app_id} updated to ${new_price}"
    })


@subscription_bp.route("/subscription/create", methods=["POST"])
@jwt_required()
@admin_required
def create_subscription():
    data = request.json
    user = User.query.get(data["user_id"])
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if "app_id" not in data:
        return jsonify({"error": "Missing app_id"}), 400

    app = App.query.get(data["app_id"])
    if not app:
        return jsonify({"error": "Invalid app_id"}), 400

    next_billing_date = datetime.utcnow() + timedelta(days=30)  # Assuming monthly billing cycle

    new_subscription = Subscription(
        user_id=data["user_id"],
        app_id=data["app_id"],
        subscription_type=data["subscription_type"],
        status="Active",
        billing_cycle="Monthly",
        next_billing_date=next_billing_date,  # Ensure this is populated
        custom_price=data["custom_price"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.session.add(new_subscription)
    db.session.commit()

    return jsonify({"message": "Subscription created successfully!"}), 201

@subscription_bp.route("/subscriptions", methods=["GET"])
@jwt_required()
@admin_required
def get_all_subscriptions_admin():
    subscriptions = Subscription.query.all()

    if not subscriptions:
        return jsonify({"message": "No subscriptions found"}), 404

    subscription_list = []
    for sub in subscriptions:
        user = User.query.get(sub.user_id)
        app = App.query.get(sub.app_id)
        subscription_list.append({
            "subscription_id": sub.id,
            "user_id": user.id if user else None,
            "user_name": user.name if user else "Unknown",
            "app_name": app.name if app else "Unknown",
            "subscription_type": sub.subscription_type,
            "status": sub.status,
            "price": sub.custom_price,
            "billing_cycle": sub.billing_cycle,
            "next_billing_date": sub.next_billing_date,
            "created_at": sub.created_at,
            "updated_at": sub.updated_at
        })

    return jsonify(subscription_list), 200


