from flask import Blueprint, request, jsonify
from app.extensions import db
from .models import create_multi_control_model, ControlStatus, Field, Equipment, Zone, IrrigationPlan, Alert, Log, Firmware
from .install import install_multi_control, uninstall_multi_control
from app.utils.auth_helpers import any_admin_required
from app.models.user_app import UserApp
from .services import MultiControlService
from werkzeug.utils import secure_filename
import logging
from datetime import datetime, timedelta

multi_control_bp = Blueprint("multi_controls", __name__, url_prefix="/multi_controls")


def get_multi_control_model(account_id):
    """Helper function to get the correct multi control model for an account"""
    return create_multi_control_model(account_id)


@multi_control_bp.route("/add", methods=["POST"])
def add_multi_control():
    data = request.json

    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    account_id = data.get("account_id")
    title = data.get("title")
    description = data.get("description")

    if not account_id or not title:
        return jsonify({"error": "Account ID and title are required"}), 400
        
    success, result = MultiControlService.create_control(account_id, title, description)
    if success:
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@multi_control_bp.route("/list", methods=["GET"])
def list_multi_controls():
    account_id = request.args.get("account_id")
    if not account_id:
        return jsonify({"error": "Account ID is required"}), 400
    controls = MultiControlService.get_controls(account_id)
    return jsonify(controls), 200


@multi_control_bp.route("/update", methods=["PATCH"])
def update_multi_control():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    account_id = data.get("account_id")
    control_id = data.get("control_id")
    new_status = data.get("new_status")

    if not account_id or not control_id or new_status not in ["ACTIVE", "INACTIVE"]:
        return jsonify({"error": "Invalid data provided"}), 400
    
    success, result = MultiControlService.update_control_status(account_id, control_id, new_status)
    if success:
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@multi_control_bp.route("/delete", methods=["DELETE"])
def delete_multi_control():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    account_id = data.get("account_id")
    control_id = data.get("control_id")

    if not account_id or not control_id:
        return jsonify({"error": "Account ID and control ID are required"}), 400
    
    success, message = MultiControlService.delete_control(account_id, control_id)
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400


@multi_control_bp.route("/install", methods=["POST"])
@any_admin_required

def install_app():
    data = request.json
    account_id = data.get("account_id")
    if not account_id:
        return jsonify({"error": "Account ID is required"}), 400
    
    if install_multi_control(account_id):
        return jsonify({"message": "MultiControl app installed successfully"}), 200
    else:
        return jsonify({"error": "Installation failed"}), 400


@multi_control_bp.route("/uninstall", methods=["POST"])
@any_admin_required

def uninstall_app():
    data = request.json
    account_id = data.get("account_id")
    if not account_id:
        return jsonify({"error": "Account ID is required"}), 400
    
    if uninstall_multi_control(account_id):
        return jsonify({"message": "MultiControl app uninstalled successfully"}), 200
    else:
        return jsonify({"error": "Uninstallation failed"}), 400


# --- Field Management Endpoints ---

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


@multi_control_bp.route('/fields/', methods=['GET'])
def get_fields():
    """GET /fields/ - List all fields with vital info (name, pressure, flow rate, operating zone)"""
    try:
        fields = Field.query.all()
        result = []
        for field in fields:
            result.append({
                'id': field.id,
                'name': field.name,
                'pressure': field.pressure,
                'flow_rate': field.flow_rate,
                'current_zone': field.current_zone
            })
        return jsonify(result), 200
    except Exception as e:
        logging.error("Error fetching fields: %s", e)
        return jsonify({"error": "Error fetching fields"}), 500


@multi_control_bp.route('/fields/<int:field_id>', methods=['GET'])
def get_field_details(field_id):
    """GET /fields/<field_id> - Get full dashboard details of a specific field"""
    try:
        field = db.session.get(Field, field_id)
        if not field:
            return jsonify({"error": "Field not found"}), 404
        field_data = {
            "id": field.id,
            "account_id": field.account_id,
            "name": field.name,
            "latitude": field.latitude,
            "longitude": field.longitude,
            "pressure": field.pressure,
            "flow_rate": field.flow_rate,
            "current_zone": field.current_zone,
            "created_at": field.created_at.isoformat(),
            "kml_file_uploaded": bool(field.kml_file),
            "shp_file_uploaded": bool(field.shp_file)
        }
        return jsonify(field_data), 200
    except Exception as e:
        logging.error("Error fetching field details: %s", e)
        return jsonify({"error": "Error fetching field details"}), 500


@multi_control_bp.route('/fields/upload_kml', methods=['POST'])
def upload_kml():
    """POST /fields/upload_kml - Upload KML file for a field"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        if not allowed_file(file.filename, {'kml'}):
            return jsonify({"error": "Invalid file extension. Only KML files are allowed."}), 400
        
        field_id = request.form.get('field_id')
        if not field_id:
            return jsonify({"error": "Field ID is required"}), 400
            
        field = db.session.get(Field, field_id)
        if not field:
            return jsonify({"error": "Field not found"}), 404
        
        filename = secure_filename(file.filename)  # filename secured, though not stored
        file_data = file.read()
        field.kml_file = file_data
        db.session.commit()
        return jsonify({"message": "KML file uploaded successfully"}), 200

    except Exception as e:
        logging.error("Error uploading KML file: %s", e)
        db.session.rollback()
        return jsonify({"error": "Error uploading KML file"}), 500


@multi_control_bp.route('/fields/upload_shp', methods=['POST'])
def upload_shp():
    """POST /fields/upload_shp - Upload SHP file for a field"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        if not allowed_file(file.filename, {'shp'}):
            return jsonify({"error": "Invalid file extension. Only SHP files are allowed."}), 400
        
        field_id = request.form.get('field_id')
        if not field_id:
            return jsonify({"error": "Field ID is required"}), 400
            
        field = db.session.get(Field, field_id)
        if not field:
            return jsonify({"error": "Field not found"}), 404
        
        filename = secure_filename(file.filename)
        file_data = file.read()
        field.shp_file = file_data
        db.session.commit()
        return jsonify({"message": "SHP file uploaded successfully"}), 200

    except Exception as e:
        logging.error("Error uploading SHP file: %s", e)
        db.session.rollback()
        return jsonify({"error": "Error uploading SHP file"}), 500


@multi_control_bp.route('/fields/', methods=['POST'])
def create_field():
    """POST /fields/ - Create a new field"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        required_fields = ['name', 'account_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        new_field = Field(
            name=data['name'],
            account_id=data['account_id'],
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            pressure=data.get('pressure'),
            flow_rate=data.get('flow_rate'),
            current_zone=data.get('current_zone')
        )

        db.session.add(new_field)
        db.session.commit()

        return jsonify({
            "message": "Field created successfully",
            "id": new_field.id,
            "name": new_field.name
        }), 201
    except Exception as e:
        logging.error("Error creating field: %s", e)
        db.session.rollback()
        return jsonify({"error": "Error creating field"}), 500


# --- Equipment Management Endpoints ---

@multi_control_bp.route('/equipment/', methods=['GET'])
def list_equipment():
    """GET /equipment/ - List all irrigation controllers"""
    try:
        equipment = Equipment.query.all()
        result = []
        for eq in equipment:
            result.append({
                'id': eq.id,
                'name': eq.name,
                'controller_id': eq.controller_id,
                'field_id': eq.field_id,
                'created_at': eq.created_at.isoformat()
            })
        return jsonify(result), 200
    except Exception as e:
        logging.error("Error fetching equipment list: %s", e)
        return jsonify({"error": "Error fetching equipment list"}), 500


@multi_control_bp.route('/equipment/<controller_id>', methods=['GET'])
def get_equipment_details(controller_id):
    """GET /equipment/<controller_id> - Get details of a specific controller"""
    try:
        equipment = Equipment.query.filter_by(controller_id=controller_id).first()
        if not equipment:
            return jsonify({"error": "Equipment not found"}), 404
            
        # Get associated zones for this equipment
        zones_data = [{
            'id': zone.id,
            'name': zone.name,
            'application_rate': zone.application_rate,
            'area': zone.area
        } for zone in equipment.zones]

        equipment_data = {
            "id": equipment.id,
            "name": equipment.name,
            "controller_id": equipment.controller_id,
            "field_id": equipment.field_id,
            "account_id": equipment.account_id,
            "created_at": equipment.created_at.isoformat(),
            "zones": zones_data
        }
        return jsonify(equipment_data), 200
    except Exception as e:
        logging.error("Error fetching equipment details: %s", e)
        return jsonify({"error": "Error fetching equipment details"}), 500


@multi_control_bp.route('/equipment/', methods=['POST'])
def add_equipment():
    """POST /equipment/ - Add a new controller"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        required_fields = ['name', 'controller_id', 'field_id', 'account_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Check if controller_id is unique
        existing_equipment = Equipment.query.filter_by(controller_id=data['controller_id']).first()
        if existing_equipment:
            return jsonify({"error": "Controller ID already exists"}), 400

        new_equipment = Equipment(
            name=data['name'],
            controller_id=data['controller_id'],
            field_id=data['field_id'],
            account_id=data['account_id']
        )

        db.session.add(new_equipment)
        db.session.commit()

        return jsonify({
            "message": "Equipment added successfully",
            "id": new_equipment.id,
            "controller_id": new_equipment.controller_id
        }), 201
    except Exception as e:
        logging.error("Error adding equipment: %s", e)
        db.session.rollback()
        return jsonify({"error": "Error adding equipment"}), 500


@multi_control_bp.route('/equipment/<controller_id>', methods=['PUT'])
def update_equipment(controller_id):
    """PUT /equipment/<controller_id> - Update controller settings"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        equipment = Equipment.query.filter_by(controller_id=controller_id).first()
        if not equipment:
            return jsonify({"error": "Equipment not found"}), 404

        # Update allowed fields
        allowed_fields = ['name', 'field_id']
        for field in allowed_fields:
            if field in data:
                setattr(equipment, field, data[field])

        db.session.commit()

        return jsonify({
            "message": "Equipment updated successfully",
            "id": equipment.id,
            "controller_id": equipment.controller_id
        }), 200
    except Exception as e:
        logging.error("Error updating equipment: %s", e)
        db.session.rollback()
        return jsonify({"error": "Error updating equipment"}), 500


@multi_control_bp.route('/equipment/<controller_id>', methods=['DELETE'])
def delete_equipment(controller_id):
    """DELETE /equipment/<controller_id> - Remove controller"""
    try:
        equipment = Equipment.query.filter_by(controller_id=controller_id).first()
        if not equipment:
            return jsonify({"error": "Equipment not found"}), 404

        db.session.delete(equipment)
        db.session.commit()

        return jsonify({
            "message": "Equipment deleted successfully",
            "controller_id": controller_id
        }), 200
    except Exception as e:
        logging.error("Error deleting equipment: %s", e)
        db.session.rollback()
        return jsonify({"error": "Error deleting equipment"}), 500


# --- Zone Management Endpoints ---

@multi_control_bp.route('/zones/', methods=['GET'])
def list_zones():
    """GET /zones/ - List all irrigation zones"""
    try:
        zones = Zone.query.all()
        result = []
        for zone in zones:
            result.append({
                'id': zone.id,
                'name': zone.name,
                'equipment_id': zone.equipment_id,
                'application_rate': zone.application_rate,
                'area': zone.area,
                'created_at': zone.created_at.isoformat()
            })
        return jsonify(result), 200
    except Exception as e:
        logging.error("Error fetching zones list: %s", e)
        return jsonify({"error": "Error fetching zones list"}), 500


@multi_control_bp.route('/zones/<int:zone_id>', methods=['GET'])
def get_zone_details(zone_id):
    """GET /zones/<zone_id> - Get details of a specific zone"""
    try:
        zone = db.session.get(Zone, zone_id)
        if not zone:
            return jsonify({"error": "Zone not found"}), 404

        zone_data = {
            "id": zone.id,
            "name": zone.name,
            "equipment_id": zone.equipment_id,
            "account_id": zone.account_id,
            "application_rate": zone.application_rate,
            "area": zone.area,
            "created_at": zone.created_at.isoformat(),
            "kml_file_uploaded": bool(zone.kml_file),
            "shp_file_uploaded": bool(zone.shp_file)
        }
        return jsonify(zone_data), 200
    except Exception as e:
        logging.error("Error fetching zone details: %s", e)
        return jsonify({"error": "Error fetching zone details"}), 500


@multi_control_bp.route('/zones/', methods=['POST'])
def create_zone():
    """POST /zones/ - Create a new zone"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        required_fields = ['name', 'equipment_id', 'account_id', 'application_rate', 'area']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Verify equipment exists
        equipment = db.session.get(Equipment, data['equipment_id'])
        if not equipment:
            return jsonify({"error": "Equipment not found"}), 404

        new_zone = Zone(
            name=data['name'],
            equipment_id=data['equipment_id'],
            account_id=data['account_id'],
            application_rate=data['application_rate'],
            area=data['area']
        )

        db.session.add(new_zone)
        db.session.commit()

        return jsonify({
            "message": "Zone created successfully",
            "id": new_zone.id
        }), 201
    except Exception as e:
        logging.error("Error creating zone: %s", e)
        db.session.rollback()
        return jsonify({"error": "Error creating zone"}), 500


@multi_control_bp.route('/zones/<int:zone_id>', methods=['PUT'])
def update_zone(zone_id):
    """PUT /zones/<zone_id> - Update zone settings"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        zone = db.session.get(Zone, zone_id)
        if not zone:
            return jsonify({"error": "Zone not found"}), 404

        # Update allowed fields
        allowed_fields = ['name', 'application_rate', 'area']
        for field in allowed_fields:
            if field in data:
                setattr(zone, field, data[field])

        db.session.commit()

        return jsonify({
            "message": "Zone updated successfully",
            "id": zone.id
        }), 200
    except Exception as e:
        logging.error("Error updating zone: %s", e)
        db.session.rollback()
        return jsonify({"error": "Error updating zone"}), 500


@multi_control_bp.route('/zones/<int:zone_id>', methods=['DELETE'])
def delete_zone(zone_id):
    """DELETE /zones/<zone_id> - Remove a zone"""
    try:
        zone = db.session.get(Zone, zone_id)
        if not zone:
            return jsonify({"error": "Zone not found"}), 404

        db.session.delete(zone)
        db.session.commit()

        return jsonify({
            "message": "Zone deleted successfully",
            "id": zone_id
        }), 200
    except Exception as e:
        logging.error("Error deleting zone: %s", e)
        db.session.rollback()
        return jsonify({"error": "Error deleting zone"}), 500


@multi_control_bp.route('/zones/upload_kml', methods=['POST'])
def upload_zone_kml():
    """POST /zones/upload_kml - Upload KML file for a zone"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        if not allowed_file(file.filename, {'kml'}):
            return jsonify({"error": "Invalid file extension. Only KML files are allowed."}), 400
        
        zone_id = request.form.get('zone_id')
        if not zone_id:
            return jsonify({"error": "Zone ID is required"}), 400
            
        zone = db.session.get(Zone, zone_id)
        if not zone:
            return jsonify({"error": "Zone not found"}), 404
        
        filename = secure_filename(file.filename)
        file_data = file.read()
        zone.kml_file = file_data
        db.session.commit()
        return jsonify({"message": "KML file uploaded successfully"}), 200

    except Exception as e:
        logging.error("Error uploading zone KML file: %s", e)
        db.session.rollback()
        return jsonify({"error": "Error uploading KML file"}), 500


@multi_control_bp.route('/zones/upload_shp', methods=['POST'])
def upload_zone_shp():
    """POST /zones/upload_shp - Upload SHP file for a zone"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        if not allowed_file(file.filename, {'shp'}):
            return jsonify({"error": "Invalid file extension. Only SHP files are allowed."}), 400
        
        zone_id = request.form.get('zone_id')
        if not zone_id:
            return jsonify({"error": "Zone ID is required"}), 400
            
        zone = db.session.get(Zone, zone_id)
        if not zone:
            return jsonify({"error": "Zone not found"}), 404
        
        filename = secure_filename(file.filename)
        file_data = file.read()
        zone.shp_file = file_data
        db.session.commit()
        return jsonify({"message": "SHP file uploaded successfully"}), 200

    except Exception as e:
        logging.error("Error uploading zone SHP file: %s", e)
        db.session.rollback()
        return jsonify({"error": "Error uploading SHP file"}), 500


# --- Irrigation Plan Management Endpoints ---

@multi_control_bp.route('/plans/', methods=['GET'])
def list_plans():
    """GET /plans/ - List all irrigation plans"""
    try:
        account_id = request.args.get('account_id')
        if not account_id:
            return jsonify({"error": "Account ID is required"}), 400

        plans = IrrigationPlan.query.filter_by(account_id=account_id).all()
        result = []
        for plan in plans:
            result.append({
                'id': plan.id,
                'name': plan.name,
                'field_id': plan.field_id,
                'user_id': plan.user_id,
                'created_at': plan.created_at.isoformat(),
                'schedule_summary': {
                    'total_zones': len(plan.schedule.get('zones', [])) if plan.schedule else 0,
                    'frequency': plan.schedule.get('frequency', 'unknown')
                } if plan.schedule else None
            })
        return jsonify(result), 200
    except Exception as e:
        logging.error("Error fetching irrigation plans: %s", e)
        return jsonify({"error": "Error fetching irrigation plans"}), 500


@multi_control_bp.route('/plans/<int:plan_id>', methods=['GET'])
def get_plan_details(plan_id):
    """GET /plans/<plan_id> - Get details of a specific plan"""
    try:
        plan = db.session.get(IrrigationPlan, plan_id)
        if not plan:
            return jsonify({"error": "Irrigation plan not found"}), 404

        # Get associated field information
        field = db.session.get(Field, plan.field_id)
        field_info = {
            'id': field.id,
            'name': field.name
        } if field else None

        plan_data = {
            "id": plan.id,
            "name": plan.name,
            "field_id": plan.field_id,
            "field": field_info,
            "account_id": plan.account_id,
            "user_id": plan.user_id,
            "schedule": plan.schedule,
            "created_at": plan.created_at.isoformat()
        }
        return jsonify(plan_data), 200
    except Exception as e:
        logging.error("Error fetching plan details: %s", e)
        return jsonify({"error": "Error fetching plan details"}), 500


@multi_control_bp.route('/plans/', methods=['POST'])
def create_plan():
    """POST /plans/ - Create a new irrigation plan"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        required_fields = ['name', 'field_id', 'account_id', 'schedule']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Validate schedule format
        schedule = data['schedule']
        if not isinstance(schedule, dict):
            return jsonify({"error": "Schedule must be a JSON object"}), 400

        required_schedule_fields = ['zones', 'frequency']
        for field in required_schedule_fields:
            if field not in schedule:
                return jsonify({"error": f"Schedule missing required field: {field}"}), 400

        # Verify field exists
        field = db.session.get(Field, data['field_id'])
        if not field:
            return jsonify({"error": "Field not found"}), 404

        new_plan = IrrigationPlan(
            name=data['name'],
            field_id=data['field_id'],
            account_id=data['account_id'],
            user_id=data.get('user_id'),  # Optional
            schedule=data['schedule']
        )

        db.session.add(new_plan)
        db.session.commit()

        return jsonify({
            "message": "Irrigation plan created successfully",
            "id": new_plan.id
        }), 201
    except Exception as e:
        logging.error("Error creating irrigation plan: %s", e)
        db.session.rollback()
        return jsonify({"error": "Error creating irrigation plan"}), 500


@multi_control_bp.route('/plans/<int:plan_id>', methods=['PUT'])
def update_plan(plan_id):
    """PUT /plans/<plan_id> - Update irrigation plan"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        plan = db.session.get(IrrigationPlan, plan_id)
        if not plan:
            return jsonify({"error": "Irrigation plan not found"}), 404

        # Update allowed fields
        allowed_fields = ['name', 'schedule']
        for field in allowed_fields:
            if field in data:
                if field == 'schedule':
                    # Validate schedule format
                    schedule = data['schedule']
                    if not isinstance(schedule, dict):
                        return jsonify({"error": "Schedule must be a JSON object"}), 400
                    
                    required_schedule_fields = ['zones', 'frequency']
                    for req_field in required_schedule_fields:
                        if req_field not in schedule:
                            return jsonify({"error": f"Schedule missing required field: {req_field}"}), 400
                
                setattr(plan, field, data[field])

        db.session.commit()

        return jsonify({
            "message": "Irrigation plan updated successfully",
            "id": plan.id
        }), 200
    except Exception as e:
        logging.error("Error updating irrigation plan: %s", e)
        db.session.rollback()
        return jsonify({"error": "Error updating irrigation plan"}), 500


@multi_control_bp.route('/plans/<int:plan_id>', methods=['DELETE'])
def delete_plan(plan_id):
    """DELETE /plans/<plan_id> - Delete an irrigation plan"""
    try:
        plan = db.session.get(IrrigationPlan, plan_id)
        if not plan:
            return jsonify({"error": "Irrigation plan not found"}), 404

        db.session.delete(plan)
        db.session.commit()

        return jsonify({
            "message": "Irrigation plan deleted successfully",
            "id": plan_id
        }), 200
    except Exception as e:
        logging.error("Error deleting irrigation plan: %s", e)
        db.session.rollback()
        return jsonify({"error": "Error deleting irrigation plan"}), 500


# --- Alert Management Endpoints ---

@multi_control_bp.route('/alerts/', methods=['GET'])
def list_alerts():
    """GET /alerts/ - Get all active alerts"""
    try:
        account_id = request.args.get('account_id')
        if not account_id:
            return jsonify({"error": "Account ID is required"}), 400

        # Get active (unresolved) alerts by default
        alerts = Alert.query.filter_by(
            account_id=account_id,
            resolved=False
        ).order_by(Alert.created_at.desc()).all()

        result = []
        for alert in alerts:
            result.append({
                'id': alert.id,
                'field_id': alert.field_id,
                'alert_type': alert.alert_type,
                'message': alert.message,
                'created_at': alert.created_at.isoformat()
            })
        return jsonify(result), 200
    except Exception as e:
        logging.error("Error fetching alerts: %s", e)
        return jsonify({"error": "Error fetching alerts"}), 500


@multi_control_bp.route('/alerts/<int:alert_id>', methods=['GET'])
def get_alert_details(alert_id):
    """GET /alerts/<alert_id> - Get details of a specific alert"""
    try:
        alert = db.session.get(Alert, alert_id)
        if not alert:
            return jsonify({"error": "Alert not found"}), 404

        # Get associated field information
        field = db.session.get(Field, alert.field_id)
        field_info = {
            'id': field.id,
            'name': field.name
        } if field else None

        alert_data = {
            "id": alert.id,
            "field_id": alert.field_id,
            "field": field_info,
            "alert_type": alert.alert_type,
            "message": alert.message,
            "resolved": alert.resolved,
            "created_at": alert.created_at.isoformat()
        }
        return jsonify(alert_data), 200
    except Exception as e:
        logging.error("Error fetching alert details: %s", e)
        return jsonify({"error": "Error fetching alert details"}), 500


@multi_control_bp.route('/alerts/', methods=['POST'])
def create_alert():
    """POST /alerts/ - Create an alert (triggered by system events)"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        required_fields = ['field_id', 'account_id', 'alert_type', 'message']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        new_alert = Alert(
            field_id=data['field_id'],
            account_id=data['account_id'],
            alert_type=data['alert_type'],
            message=data['message'],
            resolved=False
        )

        db.session.add(new_alert)
        db.session.commit()

        return jsonify({
            "message": "Alert created successfully",
            "id": new_alert.id
        }), 201
    except Exception as e:
        logging.error("Error creating alert: %s", e)
        db.session.rollback()
        return jsonify({"error": "Error creating alert"}), 500


@multi_control_bp.route('/alerts/<int:alert_id>', methods=['PUT'])
def update_alert(alert_id):
    """PUT /alerts/<alert_id> - Acknowledge or resolve an alert"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        alert = db.session.get(Alert, alert_id)
        if not alert:
            return jsonify({"error": "Alert not found"}), 404

        if 'resolved' in data:
            alert.resolved = data['resolved']

        db.session.commit()

        return jsonify({
            "message": "Alert updated successfully",
            "id": alert.id,
            "resolved": alert.resolved
        }), 200
    except Exception as e:
        logging.error("Error updating alert: %s", e)
        db.session.rollback()
        return jsonify({"error": "Error updating alert"}), 500


@multi_control_bp.route('/alerts/<int:alert_id>', methods=['DELETE'])
@any_admin_required
def delete_alert(alert_id):
    """DELETE /alerts/<alert_id> - Remove an alert (admin only)"""
    try:
        alert = db.session.get(Alert, alert_id)
        if not alert:
            return jsonify({"error": "Alert not found"}), 404

        db.session.delete(alert)
        db.session.commit()

        return jsonify({
            "message": "Alert deleted successfully",
            "id": alert_id
        }), 200
    except Exception as e:
        logging.error("Error deleting alert: %s", e)
        db.session.rollback()
        return jsonify({"error": "Error deleting alert"}), 500


# --- Logs & Reports Endpoints ---

@multi_control_bp.route('/logs/', methods=['GET'])
def get_logs():
    """GET /logs/ - Get system logs with optional filtering"""
    try:
        account_id = request.args.get('account_id')
        if not account_id:
            return jsonify({"error": "Account ID is required"}), 400

        # Handle optional filters
        event_type = request.args.get('event_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = Log.query.filter_by(account_id=account_id)

        if event_type:
            query = query.filter_by(event_type=event_type)
        if start_date:
            query = query.filter(Log.timestamp >= start_date)
        if end_date:
            query = query.filter(Log.timestamp <= end_date)

        logs = query.order_by(Log.timestamp.desc()).all()
        
        result = []
        for log in logs:
            result.append({
                'id': log.id,
                'event_type': log.event_type,
                'event_data': log.event_data,
                'timestamp': log.timestamp.isoformat(),
                'field_id': log.field_id,
                'user_id': log.user_id
            })
        return jsonify(result), 200
    except Exception as e:
        logging.error("Error fetching logs: %s", e)
        return jsonify({"error": "Error fetching logs"}), 500


@multi_control_bp.route('/logs/<int:log_id>', methods=['GET'])
def get_log_details(log_id):
    """GET /logs/<log_id> - Get details of a specific log entry"""
    try:
        log = db.session.get(Log, log_id)
        if not log:
            return jsonify({"error": "Log entry not found"}), 404

        log_data = {
            "id": log.id,
            "event_type": log.event_type,
            "event_data": log.event_data,
            "timestamp": log.timestamp.isoformat(),
            "field_id": log.field_id,
            "user_id": log.user_id,
            "account_id": log.account_id
        }
        return jsonify(log_data), 200
    except Exception as e:
        logging.error("Error fetching log details: %s", e)
        return jsonify({"error": "Error fetching log details"}), 500


@multi_control_bp.route('/reports/water-usage', methods=['GET'])
def get_water_usage_report():
    """GET /reports/water-usage - Generate water usage report"""
    try:
        account_id = request.args.get('account_id')
        if not account_id:
            return jsonify({"error": "Account ID is required"}), 400

        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        field_id = request.args.get('field_id')  # Optional field filter

        # Query relevant logs and aggregate water usage data
        query = Log.query.filter_by(
            account_id=account_id,
            event_type='irrigation_event'
        )

        if field_id:
            query = query.filter_by(field_id=field_id)
        if start_date:
            query = query.filter(Log.timestamp >= start_date)
        if end_date:
            query = query.filter(Log.timestamp <= end_date)

        logs = query.order_by(Log.timestamp).all()

        # Process logs to generate water usage statistics
        report_data = {
            "total_water_usage": sum(log.event_data.get('water_volume', 0) for log in logs),
            "usage_by_field": {},
            "usage_by_date": {},
            "period_start": start_date,
            "period_end": end_date
        }

        return jsonify(report_data), 200
    except Exception as e:
        logging.error("Error generating water usage report: %s", e)
        return jsonify({"error": "Error generating water usage report"}), 500


@multi_control_bp.route('/reports/system-health', methods=['GET'])
def get_system_health_report():
    """GET /reports/system-health - Generate system health report"""
    try:
        account_id = request.args.get('account_id')
        if not account_id:
            return jsonify({"error": "Account ID is required"}), 400

        # Collect system health data
        equipment_status = Equipment.query.filter_by(account_id=account_id).all()
        active_alerts = Alert.query.filter_by(account_id=account_id, resolved=False).count()
        recent_errors = Log.query.filter_by(
            account_id=account_id,
            event_type='error'
        ).order_by(Log.timestamp.desc()).limit(10).all()

        report_data = {
            "equipment_summary": {
                "total": len(equipment_status),
                "online": sum(1 for eq in equipment_status if eq.status == 'ACTIVE'),
                "offline": sum(1 for eq in equipment_status if eq.status != 'ACTIVE')
            },
            "active_alerts": active_alerts,
            "recent_errors": [{
                "timestamp": log.timestamp.isoformat(),
                "error_type": log.event_data.get('error_type'),
                "message": log.event_data.get('message')
            } for log in recent_errors],
            "generated_at": datetime.utcnow().isoformat()
        }

        return jsonify(report_data), 200
    except Exception as e:
        logging.error("Error generating system health report: %s", e)
        return jsonify({"error": "Error generating system health report"}), 500


# --- Firmware Management Endpoints ---

@multi_control_bp.route('/firmware/', methods=['GET'])
def list_firmware():
    """GET /firmware/ - Get available firmware versions"""
    try:
        account_id = request.args.get('account_id')
        if not account_id:
            return jsonify({"error": "Account ID is required"}), 400

        firmware_list = Firmware.query.filter_by(
            account_id=account_id
        ).order_by(Firmware.release_date.desc()).all()

        result = []
        for fw in firmware_list:
            result.append({
                'id': fw.id,
                'version': fw.version,
                'equipment_id': fw.equipment_id,
                'release_date': fw.release_date.isoformat(),
                'changelog': fw.changelog
            })
        return jsonify(result), 200
    except Exception as e:
        logging.error("Error fetching firmware list: %s", e)
        return jsonify({"error": "Error fetching firmware list"}), 500


@multi_control_bp.route('/firmware/update/<controller_id>', methods=['POST'])
def update_firmware(controller_id):
    """POST /firmware/update/<controller_id> - Push firmware update to a controller"""
    try:
        data = request.json
        if not data or 'firmware_id' not in data:
            return jsonify({"error": "Firmware ID is required"}), 400

        # Verify equipment exists and is online
        equipment = Equipment.query.filter_by(controller_id=controller_id).first()
        if not equipment:
            return jsonify({"error": "Equipment not found"}), 404
        if equipment.status != 'ACTIVE':
            return jsonify({"error": "Equipment is offline"}), 400

        # Verify firmware exists
        firmware = db.session.get(Firmware, data['firmware_id'])
        if not firmware:
            return jsonify({"error": "Firmware not found"}), 404

        # Log the update attempt
        update_log = Log(
            account_id=equipment.account_id,
            field_id=equipment.field_id,
            event_type='firmware_update',
            event_data={
                'equipment_id': equipment.id,
                'controller_id': controller_id,
                'firmware_version': firmware.version,
                'status': 'initiated'
            }
        )
        db.session.add(update_log)
        db.session.commit()

        return jsonify({
            "message": "Firmware update initiated",
            "controller_id": controller_id,
            "firmware_version": firmware.version
        }), 200
    except Exception as e:
        logging.error("Error initiating firmware update: %s", e)
        db.session.rollback()
        return jsonify({"error": "Error initiating firmware update"}), 500


# --- System Status Endpoints ---

@multi_control_bp.route('/status/', methods=['GET'])
def get_system_status():
    """GET /status/ - Get system status"""
    try:
        account_id = request.args.get('account_id')
        if not account_id:
            return jsonify({"error": "Account ID is required"}), 400

        # Collect system status information
        total_equipment = Equipment.query.filter_by(account_id=account_id).count()
        active_equipment = Equipment.query.filter_by(account_id=account_id, status='ACTIVE').count()
        active_alerts = Alert.query.filter_by(account_id=account_id, resolved=False).count()
        recent_errors = Log.query.filter_by(
            account_id=account_id,
            event_type='error'
        ).filter(
            Log.timestamp >= datetime.utcnow() - timedelta(hours=24)
        ).count()

        status_data = {
            "status": "operational" if active_equipment > 0 else "degraded",
            "equipment": {
                "total": total_equipment,
                "active": active_equipment,
                "inactive": total_equipment - active_equipment
            },
            "alerts": {
                "active": active_alerts
            },
            "errors_24h": recent_errors,
            "last_updated": datetime.utcnow().isoformat()
        }

        return jsonify(status_data), 200
    except Exception as e:
        logging.error("Error fetching system status: %s", e)
        return jsonify({"error": "Error fetching system status"}), 500


@multi_control_bp.route('/ping', methods=['GET'])
def ping():
    """GET /ping - Basic API health check"""
    try:
        return jsonify({
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logging.error("Error in ping endpoint: %s", e)
        return jsonify({"status": "error"}), 500 