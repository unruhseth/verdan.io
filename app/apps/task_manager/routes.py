from flask import Blueprint, request, jsonify
from app.extensions import db
from .models import create_task_model, TaskStatus
from .install import install_task_manager, uninstall_task_manager
from app.utils.auth_helpers import any_admin_required
from app.models.user_app import UserApp
from .services import TaskService
from flask_jwt_extended import jwt_required, get_jwt
from flask_cors import cross_origin

task_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

def get_task_model(account_id):
    """Helper function to get the correct task model for an account"""
    return create_task_model(account_id)

@task_bp.route("/add", methods=["POST"])
@cross_origin()
@jwt_required()
def add_task():
    """Add a new task"""
    data = request.json
    
    # Validate required fields
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    account_id = data.get("account_id")
    title = data.get("title")
    description = data.get("description")
    
    # Validate required fields
    if not account_id:
        return jsonify({"error": "Account ID is required"}), 400
    if not title:
        return jsonify({"error": "Title is required"}), 400
    if not title.strip():
        return jsonify({"error": "Title cannot be empty"}), 400
        
    # Check if app is installed
    user_app = UserApp.query.filter_by(
        account_id=account_id,
        app_name="task_manager",
        is_installed=True
    ).first()
    
    if not user_app:
        return jsonify({"error": "Task Manager is not installed for this account"}), 404
    
    # Use TaskService to create the task
    success, result = TaskService.create_task(
        account_id=account_id,
        title=title,
        description=description
    )
    
    if not success:
        return jsonify({"error": result.get("error", "Failed to create task")}), 500
        
    return jsonify({
        "message": "Task created successfully",
        "task": result
    }), 201

@task_bp.route("/list", methods=["GET"])
@cross_origin()
@jwt_required()
def list_tasks():
    """List all tasks for an account"""
    account_id = request.args.get("account_id")
    
    if not account_id:
        return jsonify({"error": "Account ID is required"}), 400
    
    # Check if app is installed
    user_app = UserApp.query.filter_by(
        account_id=account_id,
        app_name="task_manager",
        is_installed=True
    ).first()
    
    if not user_app:
        return jsonify({"error": "Task Manager is not installed for this account"}), 404
    
    TaskModel = get_task_model(account_id)
    tasks = TaskModel.query.all()
    
    return jsonify({
        "tasks": [{
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "created_at": task.created_at
        } for task in tasks]
    }), 200

@task_bp.route("/update", methods=["PATCH", "POST", "OPTIONS"])
@cross_origin(methods=["PATCH", "POST", "OPTIONS"])
@jwt_required()
def update_task():
    """Update a task's status"""
    if request.method == "OPTIONS":
        return jsonify({}), 200
        
    data = request.json
    account_id = data.get("account_id")
    task_id = data.get("task_id")
    new_status = data.get("status")
    
    if not all([account_id, task_id, new_status]):
        return jsonify({"error": "Account ID, task ID and status are required"}), 400
    
    # Verify user has access to this account
    claims = get_jwt()
    if int(claims.get("account_id")) != int(account_id):
        return jsonify({"error": "You do not have permission to update tasks for this account"}), 403
    
    # Check if app is installed
    user_app = UserApp.query.filter_by(
        account_id=account_id,
        app_name="task_manager",
        is_installed=True
    ).first()
    
    if not user_app:
        return jsonify({"error": "Task Manager is not installed for this account"}), 404
    
    TaskModel = get_task_model(account_id)
    task = TaskModel.query.get(task_id)
    
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    try:
        # Validate the status value against the TaskStatus enum
        if new_status.upper() not in TaskStatus.__members__:
            return jsonify({"error": f"Invalid status. Must be one of: {', '.join(TaskStatus.__members__.keys())}"}), 400
            
        task.status = new_status.upper()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    
    return jsonify({
        "message": "Task updated successfully",
        "task": {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "created_at": task.created_at.isoformat() if task.created_at else None
        }
    }), 200

@task_bp.route("/delete", methods=["DELETE"])
@cross_origin()
@jwt_required()
def delete_task():
    """Delete a task"""
    data = request.json
    account_id = data.get("account_id")
    task_id = data.get("task_id")
    
    if not all([account_id, task_id]):
        return jsonify({"error": "Account ID and task ID are required"}), 400
    
    # Check if app is installed
    user_app = UserApp.query.filter_by(
        account_id=account_id,
        app_name="task_manager",
        is_installed=True
    ).first()
    
    if not user_app:
        return jsonify({"error": "Task Manager is not installed for this account"}), 404
    
    TaskModel = get_task_model(account_id)
    task = TaskModel.query.get(task_id)
    
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({"message": "Task deleted successfully"}), 200

# App Installation Routes
@task_bp.route("/install", methods=["POST"])
@any_admin_required
def install_app():
    """Install the Task Manager app for an account"""
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    try:
        account_id = int(data.get("account_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "Account ID must be a valid integer"}), 400
    
    if not account_id:
        return jsonify({"error": "Account ID is required"}), 400
    
    # Check if already installed
    user_app = UserApp.query.filter_by(
        account_id=account_id,
        app_name="task_manager"
    ).first()
    
    if user_app and user_app.is_installed:
        return jsonify({"message": "Task Manager is already installed"}), 200
    
    success, message = install_task_manager(account_id)
    
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 500

@task_bp.route("/uninstall", methods=["POST"])
@any_admin_required
def uninstall_app():
    """Uninstall the Task Manager app for an account"""
    data = request.json
    account_id = data.get("account_id")
    
    if not account_id:
        return jsonify({"error": "Account ID is required"}), 400
    
    success, message = uninstall_task_manager(account_id)
    
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 500 