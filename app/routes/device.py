from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.extensions import db
from app.models.device_models import Device
from app.services.soracom_service import soracom_request



device_bp = Blueprint("device", __name__)

# Ensure only admin users can manage devices
def admin_required():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admins only"}), 403

# Create a new device
@device_bp.route("/", methods=["POST"])
@jwt_required()
def create_device():
    admin_required()
    
    data = request.json
    new_device = Device(
        name=data["name"],
        app_id=data["app_id"]
    )
    db.session.add(new_device)
    db.session.commit()
    
    return jsonify({"message": "Device created", "device_id": new_device.id}), 201

# Get all devices (Admin only)
@device_bp.route("/", methods=["GET"])
@jwt_required()
def get_all_devices():
    admin_required()
    
    devices = Device.query.all()
    return jsonify([{"id": d.id, "name": d.name, "status": d.status} for d in devices])

# Get a specific device
@device_bp.route("/<int:device_id>", methods=["GET"])
@jwt_required()
def get_device(device_id):
    device = Device.query.get(device_id)
    if not device:
        return jsonify({"error": "Device not found"}), 404
    
    return jsonify({
        "id": device.id,
        "name": device.name,
        "status": device.status,
        "app_id": device.app_id,
        "sim_card_id": device.sim_card_id
    })

# Update a device
@device_bp.route("/<int:device_id>", methods=["PUT"])
@jwt_required()
def update_device(device_id):
    admin_required()
    
    device = Device.query.get(device_id)
    if not device:
        return jsonify({"error": "Device not found"}), 404
    
    data = request.json
    if "name" in data:
        device.name = data["name"]
    if "status" in data:
        device.status = data["status"]
    
    db.session.commit()
    return jsonify({"message": "Device updated successfully"})

# Delete a device
@device_bp.route("/<int:device_id>", methods=["DELETE"])
@jwt_required()
def delete_device(device_id):
    admin_required()
    
    device = Device.query.get(device_id)
    if not device:
        return jsonify({"error": "Device not found"}), 404
    
    db.session.delete(device)
    db.session.commit()
    
    return jsonify({"message": "Device deleted successfully"})

# Assign a SIM card to a device
@device_bp.route("/<int:device_id>/assign_sim", methods=["POST"])
@jwt_required()
def assign_sim(device_id):
    """Assign a SIM to a device"""

    data = request.json
    imsi = data.get("imsi")  # We now use Soracom IMSI instead of sim_card_id

    if not imsi:
        return jsonify({"error": "IMSI is required"}), 400

    # Check if the Soracom SIM exists
    sim_data = soracom_request("GET", f"/subscribers/{imsi}")

    if "error" in sim_data:
        return sim_data  # Return error response

    # Find the device in Verdan
    device = Device.query.get(device_id)

    if not device:
        return jsonify({"error": "Device not found"}), 404

    # Assign the Soracom IMSI to the device
    device.sim_card_id = imsi
    db.session.commit()

    return jsonify({
        "message": f"SIM {imsi} assigned to device {device_id}",
        "device_id": device_id,
        "imsi": imsi
    }), 200

# Activate a device
@device_bp.route("/<int:device_id>/activate", methods=["POST"])
@jwt_required()
def activate_device(device_id):
    admin_required()
    
    device = Device.query.get(device_id)
    if not device:
        return jsonify({"error": "Device not found"}), 404

    device.status = "active"
    db.session.commit()
    
    return jsonify({"message": "Device activated"})

# Deactivate a device
@device_bp.route("/<int:device_id>/deactivate", methods=["POST"])
@jwt_required()
def deactivate_device(device_id):
    admin_required()
    
    device = Device.query.get(device_id)
    if not device:
        return jsonify({"error": "Device not found"}), 404

    device.status = "inactive"
    db.session.commit()
    
    return jsonify({"message": "Device deactivated"})
