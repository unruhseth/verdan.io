from .models import create_task_model, TaskStatus
from app.extensions import db
from typing import Optional, Tuple, List, Dict, Any

class TaskService:
    @staticmethod
    def get_task_model(account_id: str):
        """Get the task model for a specific account"""
        return create_task_model(account_id)
    
    @staticmethod
    def create_task(account_id: str, title: str, description: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """Create a new task"""
        try:
            TaskModel = create_task_model(account_id)
            
            task = TaskModel(
                title=title,
                description=description,
                status='PENDING'  # Use string value directly
            )
            
            db.session.add(task)
            db.session.commit()
            
            return True, {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "created_at": task.created_at
            }
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}
    
    @staticmethod
    def get_tasks(account_id: str) -> List[Dict[str, Any]]:
        """Get all tasks for an account"""
        TaskModel = create_task_model(account_id)
        tasks = TaskModel.query.all()
        
        return [{
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "created_at": task.created_at
        } for task in tasks]
    
    @staticmethod
    def update_task_status(account_id: str, task_id: str, new_status: str) -> Tuple[bool, Dict[str, Any]]:
        """Update a task's status"""
        try:
            TaskModel = create_task_model(account_id)
            task = TaskModel.query.get(task_id)
            
            if not task:
                return False, {"error": "Task not found"}
            
            task.status = new_status.upper()  # Convert to uppercase
            db.session.commit()
            
            return True, {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "created_at": task.created_at
            }
        except ValueError:
            return False, {"error": "Invalid status value"}
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}
    
    @staticmethod
    def delete_task(account_id: str, task_id: str) -> Tuple[bool, str]:
        """Delete a task"""
        try:
            TaskModel = create_task_model(account_id)
            task = TaskModel.query.get(task_id)
            
            if not task:
                return False, "Task not found"
            
            db.session.delete(task)
            db.session.commit()
            
            return True, "Task deleted successfully"
        except Exception as e:
            db.session.rollback()
            return False, str(e) 