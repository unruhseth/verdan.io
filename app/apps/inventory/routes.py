from flask import Blueprint, request, jsonify
from app.extensions import db
from .models import create_app_tables
from .services import InventoryService
from app.utils.auth_helpers import any_admin_required
from flask_jwt_extended import jwt_required, get_jwt
from flask_cors import cross_origin
from uuid import UUID
import logging
from .install import install_inventory, uninstall_inventory

inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")
logger = logging.getLogger(__name__)

# Category Routes
@inventory_bp.route("/categories", methods=["POST"])
@cross_origin()
@jwt_required()
def create_category():
    """Create a new category"""
    try:
        data = request.json
        account_id = data.pop("account_id")
        success, result = InventoryService.create_category(account_id, data)
        
        if success:
            return jsonify(result), 201
        return jsonify(result), 400
    except Exception as e:
        logger.error(f"Error creating category: {str(e)}")
        return jsonify({"error": str(e)}), 500

@inventory_bp.route("/categories/tree", methods=["GET"])
@cross_origin()
@jwt_required()
def get_category_tree():
    """Get category hierarchy"""
    try:
        account_id = request.args.get("account_id", type=int)
        if not account_id:
            return jsonify({"error": "account_id is required"}), 400
            
        tree = InventoryService.get_category_tree(account_id)
        return jsonify(tree), 200
    except Exception as e:
        logger.error(f"Error getting category tree: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Item Routes
@inventory_bp.route("/items", methods=["POST"])
@cross_origin()
@jwt_required()
def create_item():
    """Create a new inventory item"""
    try:
        data = request.json
        account_id = data.pop("account_id")
        success, result = InventoryService.create_item(account_id, data)
        
        if success:
            return jsonify(result), 201
        return jsonify(result), 400
    except Exception as e:
        logger.error(f"Error creating item: {str(e)}")
        return jsonify({"error": str(e)}), 500

@inventory_bp.route("/items", methods=["GET"])
@cross_origin()
@jwt_required()
def list_items():
    """List all items for an account"""
    try:
        account_id = request.args.get("account_id", type=int)
        if not account_id:
            return jsonify({"error": "account_id is required"}), 400
            
        items = InventoryService.list_items(account_id)
        return jsonify(items), 200
    except Exception as e:
        logger.error(f"Error listing items: {str(e)}")
        return jsonify({"error": str(e)}), 500

@inventory_bp.route("/items/<item_id>", methods=["GET"])
@cross_origin()
@jwt_required()
def get_item(item_id):
    """Get a specific item"""
    try:
        account_id = request.args.get("account_id", type=int)
        if not account_id:
            return jsonify({"error": "account_id is required"}), 400
            
        item = InventoryService.get_item(account_id, item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404
        return jsonify(item), 200
    except Exception as e:
        logger.error(f"Error getting item: {str(e)}")
        return jsonify({"error": str(e)}), 500

@inventory_bp.route("/items/<item_id>", methods=["PUT"])
@cross_origin()
@jwt_required()
def update_item(item_id):
    """Update an item"""
    try:
        data = request.json
        account_id = data.pop("account_id")
        success, result = InventoryService.update_item(account_id, item_id, data)
        
        if success:
            return jsonify(result), 200
        return jsonify(result), 400
    except Exception as e:
        logger.error(f"Error updating item: {str(e)}")
        return jsonify({"error": str(e)}), 500

@inventory_bp.route("/items/<item_id>", methods=["DELETE"])
@cross_origin()
@jwt_required()
def delete_item(item_id):
    """Delete an item"""
    try:
        claims = get_jwt()
        account_id = claims.get('account_id')
        if not account_id:
            return jsonify({"error": "Account ID not found in token"}), 400
            
        success, message = InventoryService.delete_item(account_id, item_id)
        if success:
            return jsonify({"message": message}), 200
        return jsonify({"error": message}), 400
    except Exception as e:
        logger.error(f"Error deleting item: {str(e)}")
        return jsonify({"error": str(e)}), 500

@inventory_bp.route("/items/search", methods=["GET"])
@cross_origin()
@jwt_required()
def search_items():
    """Search inventory items with filters"""
    try:
        account_id = request.args.get("account_id", type=int)
        query = request.args.get("query")
        category_id = request.args.get("category_id")
        status = request.args.get("status")
        
        if not account_id:
            return jsonify({"error": "account_id is required"}), 400
            
        if category_id:
            category_id = UUID(category_id)
            
        items = InventoryService.search_items(
            account_id=account_id,
            query=query,
            category_id=category_id,
            status=status
        )
        return jsonify(items), 200
    except Exception as e:
        logger.error(f"Error searching items: {str(e)}")
        return jsonify({"error": str(e)}), 500

@inventory_bp.route("/items/low-stock", methods=["GET"])
@cross_origin()
@jwt_required()
def get_low_stock_items():
    """Get items that are at or below their reorder point"""
    try:
        account_id = request.args.get("account_id", type=int)
        if not account_id:
            return jsonify({"error": "account_id is required"}), 400
            
        items = InventoryService.get_low_stock_items(account_id)
        return jsonify(items), 200
    except Exception as e:
        logger.error(f"Error getting low stock items: {str(e)}")
        return jsonify({"error": str(e)}), 500

@inventory_bp.route("/items/<item_id>/quantity", methods=["POST"])
@cross_origin()
@jwt_required()
def update_item_quantity(item_id):
    """Update item quantity"""
    try:
        data = request.json
        account_id = data.get("account_id")
        quantity_change = data.get("quantity_change")
        transaction_type = data.get("type")
        reference = data.get("reference")
        notes = data.get("notes")
        
        if not all([account_id, quantity_change, transaction_type]):
            return jsonify({"error": "Missing required fields"}), 400
            
        success, result = InventoryService.update_item_quantity(
            account_id=account_id,
            item_id=UUID(item_id),
            quantity_change=quantity_change,
            transaction_type=transaction_type,
            reference=reference,
            notes=notes
        )
        
        if success:
            return jsonify(result), 200
        return jsonify(result), 400
    except Exception as e:
        logger.error(f"Error updating item quantity: {str(e)}")
        return jsonify({"error": str(e)}), 500

@inventory_bp.route("/items/<item_id>/transactions", methods=["GET"])
@cross_origin()
@jwt_required()
def get_item_transactions(item_id):
    """Get recent transactions for an item"""
    try:
        account_id = request.args.get("account_id", type=int)
        limit = request.args.get("limit", type=int, default=10)
        
        if not account_id:
            return jsonify({"error": "account_id is required"}), 400
            
        transactions = InventoryService.get_item_transactions(
            account_id=account_id,
            item_id=UUID(item_id),
            limit=limit
        )
        return jsonify(transactions), 200
    except Exception as e:
        logger.error(f"Error getting item transactions: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Installation Routes
@inventory_bp.route("/install", methods=["POST"])
@cross_origin()
@jwt_required()
@any_admin_required
def install_app():
    """Install this app for an account"""
    data = request.json
    account_id = data.get("account_id")
    if not account_id:
        return jsonify({"error": "Account ID is required"}), 400
    
    if install_inventory(account_id):
        return jsonify({"message": "App installed successfully"}), 200
    else:
        return jsonify({"error": "Installation failed"}), 400

@inventory_bp.route("/uninstall", methods=["POST"])
@cross_origin()
@jwt_required()
@any_admin_required
def uninstall_app():
    """Uninstall this app for an account"""
    data = request.json
    account_id = data.get("account_id")
    if not account_id:
        return jsonify({"error": "Account ID is required"}), 400
    
    if uninstall_inventory(account_id):
        return jsonify({"message": "App uninstalled successfully"}), 200
    else:
        return jsonify({"error": "Uninstallation failed"}), 400

 