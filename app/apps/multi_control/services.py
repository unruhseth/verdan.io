from .models import create_multi_control_model, ControlStatus
from app.extensions import db
from typing import Optional, Tuple, List, Dict, Any


class MultiControlService:
    @staticmethod
    def get_control_model(account_id: str):
        """Get the multi control model for a specific account"""
        return create_multi_control_model(account_id)

    @staticmethod
    def create_control(account_id: str, title: str, description: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """Create a new control"""
        try:
            ControlModel = create_multi_control_model(account_id)
            
            control = ControlModel(
                title=title,
                description=description,
                status='ACTIVE'
            )
            
            db.session.add(control)
            db.session.commit()
            
            return True, {
                "id": str(control.id),
                "title": control.title,
                "description": control.description,
                "status": control.status,
                "created_at": control.created_at
            }
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def get_controls(account_id: str) -> List[Dict[str, Any]]:
        """Get all controls for an account"""
        ControlModel = create_multi_control_model(account_id)
        controls = ControlModel.query.all()
        
        return [{
            "id": str(control.id),
            "title": control.title,
            "description": control.description,
            "status": control.status,
            "created_at": control.created_at
        } for control in controls]

    @staticmethod
    def update_control_status(account_id: str, control_id: str, new_status: str) -> Tuple[bool, Dict[str, Any]]:
        """Update the status of a control"""
        try:
            ControlModel = create_multi_control_model(account_id)
            control = ControlModel.query.filter_by(id=control_id).first()
            if not control:
                return False, {"error": "Control not found"}
            control.status = new_status
            db.session.commit()
            
            return True, {
                "id": str(control.id),
                "title": control.title,
                "description": control.description,
                "status": control.status,
                "created_at": control.created_at
            }
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}
    
    @staticmethod
    def delete_control(account_id: str, control_id: str) -> Tuple[bool, str]:
        """Delete a control"""
        try:
            ControlModel = create_multi_control_model(account_id)
            control = ControlModel.query.filter_by(id=control_id).first()
            if not control:
                return False, "Control not found"
            db.session.delete(control)
            db.session.commit()
            return True, "Control deleted successfully"
        except Exception as e:
            db.session.rollback()
            return False, str(e) 