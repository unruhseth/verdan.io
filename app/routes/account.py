from flask import Blueprint, request, jsonify
from app.models.account import Account
from app.extensions import db
from app.utils.auth_helpers import admin_required  # Ensure only admin access


account_bp = Blueprint("account", __name__)

@account_bp.route("/create", methods=["POST"])
@admin_required
def create_account():
    data = request.json
    new_account = Account(
        name=data["name"],
        subdomain=data["subdomain"]
    )
    db.session.add(new_account)
    db.session.commit()
    return jsonify({"message": "Account created successfully!", "account_id": new_account.id}), 201
