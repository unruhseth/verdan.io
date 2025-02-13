from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID, ENUM
from app.extensions import db
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"

class Task(db.Model):
    """Base Task model that will be used as a template for account-specific tables"""
    __abstract__ = True  # This makes it a template model, not an actual table

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(ENUM('PENDING', 'COMPLETED', name='taskstatus', create_type=False), default='PENDING', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

def create_task_model(account_id):
    """Dynamically create a Task model for a specific account"""
    table_name = f"tasks_{account_id}"
    
    return type(
        f"Tasks_{account_id}",
        (Task,),
        {
            "__tablename__": table_name,
            "__table_args__": {"extend_existing": True}
        }
    ) 