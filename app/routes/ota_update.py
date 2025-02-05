from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.device_models import OTAUpdate, DeviceGroup

ota_bp = Blueprint("ota_updates", __name__)

@ota_bp.route("/ota_updates", methods=["POST"])
def create_ota_update():
    """Create a new OTA update for a device group"""
    data = request.json
    group_id = data.get("group_id")
    version = data.get("version")

    # Validate that the device group exists
    group = DeviceGroup.query.get(group_id)
    if not group:
        return jsonify({"error": "Device group not found"}), 404

    # Create the OTA update
    new_update = OTAUpdate(group_id=group_id, version=version, status="pending")
    db.session.add(new_update)
    db.session.commit()

    return jsonify({
        "message": f"OTA Update {new_update.id} created for Group {group_id}",
        "ota_update_id": new_update.id
    }), 201

@ota_bp.route("/ota_updates", methods=["GET"])
def get_ota_updates():
    """Retrieve all OTA updates"""
    updates = OTAUpdate.query.all()
    updates_list = [{
        "id": update.id,
        "group_id": update.group_id,
        "version": update.version,
        "status": update.status,
        "timestamp": update.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    } for update in updates]

    return jsonify(updates_list), 200

@ota_bp.route("/ota_updates/<int:update_id>", methods=["GET"])
def get_single_ota_update(update_id):
    """Retrieve a single OTA update by ID"""
    update = OTAUpdate.query.get(update_id)
    if not update:
        return jsonify({"error": "OTA update not found"}), 404

    return jsonify({
        "id": update.id,
        "group_id": update.group_id,
        "version": update.version,
        "status": update.status,
        "timestamp": update.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    }), 200

