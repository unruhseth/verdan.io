# from flask import Blueprint, request, jsonify
# import stripe
# import os
# from dotenv import load_dotenv
# from flask_jwt_extended import jwt_required
# from app.utils.auth_helpers import admin_required

# load_dotenv()
# stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# stripe_bp = Blueprint("stripe", __name__)

# # 1️⃣ Create a new product
# @stripe_bp.route("/stripe/product", methods=["POST"])
# @jwt_required()
# @admin_required
# def create_stripe_product():
#     data = request.json
#     name = data.get("name")
#     description = data.get("description", "")

#     if not name:
#         return jsonify({"error": "Product name is required"}), 400

#     try:
#         product = stripe.Product.create(name=name, description=description)
#         return jsonify({"product_id": product["id"], "name": product["name"]}), 201

#     except stripe.error.StripeError as e:
#         return jsonify({"error": str(e)}), 400

# # 2️⃣ Create a price for a product
# @stripe_bp.route("/stripe/price", methods=["POST"])
# @jwt_required()
# @admin_required
# def create_stripe_price():
#     data = request.json
#     product_id = data.get("product_id")
#     unit_amount = data.get("unit_amount")
#     currency = data.get("currency", "usd")
#     interval = data.get("interval", "month")

#     if not product_id or not unit_amount or unit_amount <= 0:
#         return jsonify({"error": "Invalid product_id or unit_amount"}), 400

#     try:
#         price = stripe.Price.create(
#             product=product_id,
#             unit_amount=unit_amount,
#             currency=currency,
#             recurring={"interval": interval},
#         )
#         return jsonify({"price_id": price["id"], "unit_amount": price["unit_amount"]}), 201

#     except stripe.error.StripeError as e:
#         return jsonify({"error": str(e)}), 400

# # 3️⃣ List all products
# @stripe_bp.route("/stripe/products", methods=["GET"])
# @jwt_required()
# @admin_required
# def list_stripe_products():
#     try:
#         products = stripe.Product.list(limit=10)
#         return jsonify(products)

#     except stripe.error.StripeError as e:
#         return jsonify({"error": str(e)}), 400

# # 4️⃣ List all prices for a product
# @stripe_bp.route("/stripe/prices/<product_id>", methods=["GET"])
# @jwt_required()
# @admin_required
# def list_stripe_prices(product_id):
#     try:
#         prices = stripe.Price.list(product=product_id)
#         return jsonify(prices)

#     except stripe.error.StripeError as e:
#         return jsonify({"error": str(e)}), 400
