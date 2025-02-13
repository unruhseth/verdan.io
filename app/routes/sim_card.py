# from flask import Blueprint, request, jsonify
# from flask_jwt_extended import jwt_required
# from app.models.device_models import SIMCard
# from app.extensions import db
# from app.services.soracom_service import soracom_request

# sim_card_bp = Blueprint("sim_card", __name__)

# # Get all SIM cards
# @sim_card_bp.route("/sim_cards", methods=["GET"])
# @jwt_required()
# def get_all_sim_cards():
#     """Retrieve SIM cards from Soracom API"""
#     soracom_sims = soracom_request("GET", "/subscribers")

#     if "error" in soracom_sims:
#         return soracom_sims  # Return error response

#     # Format Soracom SIM data to match Verdan's structure
#     formatted_sims = [
#         {
#             "imsi": sim["imsi"],
#             "msisdn": sim.get("msisdn", "Unknown"),
#             "ipAddress": sim.get("ipAddress", "Unknown"),
#             "apn": sim.get("apn", "Unknown"),
#             "status": sim.get("status", "Unknown")
#         }
#         for sim in soracom_sims
#     ]
    
#     return jsonify(formatted_sims), 200

# # Create a new SIM card
# @sim_card_bp.route("/sim_cards", methods=["POST"])
# @jwt_required()
# def create_sim_card():
#     """Generate and register a new SIM in Soracom Sandbox"""

#     # Step 1: Generate a new dummy SIM
#     generated_sim = soracom_request("POST", "/sandbox/subscribers/create")

#     if "error" in generated_sim:
#         return generated_sim  # Return error response

#     imsi = generated_sim["imsi"]
#     passcode = generated_sim["registrationSecret"]

#     # Step 2: Register the generated SIM
#     registration_response = soracom_request(
#         "POST", f"/subscribers/{imsi}/register", {"registrationSecret": passcode}
#     )

#     if "error" in registration_response:
#         return registration_response  # Return error response

#     # Step 3: Save to Database
#     new_sim = SIMCard(
#         id=registration_response["imsi"],  # Using IMSI as the primary key
#         iccid=registration_response.get("iccid", "Unknown"),
#         status="ready",
#         user_id=2,  # Change this dynamically if needed
#         app_id=1  # Change this dynamically if needed
#     )

#     db.session.add(new_sim)
#     db.session.commit()

#     return jsonify({
#         "message": "SIM registered successfully!",
#         "imsi": registration_response["imsi"],
#         "iccid": registration_response.get("iccid", "Unknown"),
#         "msisdn": registration_response.get("msisdn", "Unknown"),
#     }), 201

