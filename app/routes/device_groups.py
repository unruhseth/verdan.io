# from flask import Blueprint, request, jsonify
# from app.extensions import db
# from app.models.device_models import DeviceGroup, Device

# device_groups_bp = Blueprint("device_groups", __name__)

# @device_groups_bp.route("/device_groups", methods=["POST"])
# def create_device_group():
#     data = request.json
#     new_group = DeviceGroup(name=data["name"])
#     db.session.add(new_group)
#     db.session.commit()
    
#     return jsonify({"id": new_group.id, "message": "Device group created!"}), 201

# @device_groups_bp.route("/device_groups/<int:group_id>/add_device", methods=["POST"])
# def add_device_to_group(group_id):
#     data = request.json
#     device_id = data.get("device_id")

#     # Check if both group and device exist
#     group = DeviceGroup.query.get(group_id)
#     device = Device.query.get(device_id)

#     if not group or not device:
#         return jsonify({"error": "Group or Device not found"}), 404

#     # Add device to the group
#     group.devices.append(device)
#     db.session.commit()

#     return jsonify({"message": f"Device {device_id} added to group {group_id}"}), 200


