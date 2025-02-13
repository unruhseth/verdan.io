from flask import Blueprint, request, jsonify
from app.models.account import Account
from app.extensions import db
from app.utils.auth_helpers import high_level_admin_required


account_bp = Blueprint("account", __name__)

@account_bp.route("/", methods=["POST"])
@high_level_admin_required
def create_account():
    data = request.json
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
    """Update an existing account's details."""
    account = Account.query.get(account_id)
    
    if not account:
        return jsonify({"error": "Account not found"}), 404
    
    data = request.json
    
    # Update fields if they are provided in the request
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
    """Delete an existing account."""
    account = Account.query.get(account_id)
    
    if not account:
        return jsonify({"error": "Account not found"}), 404
    
    db.session.delete(account)
    db.session.commit()
    
    return jsonify({"message": "Account deleted successfully"}), 200
