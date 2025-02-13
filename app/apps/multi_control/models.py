from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSONB
from app.extensions import db
from datetime import datetime
from enum import Enum


class ControlStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


def create_enum_type():
    """Create the controlstatus enum type if it doesn't exist"""
    try:
        db.session.execute('CREATE TYPE controlstatus AS ENUM (\'ACTIVE\', \'INACTIVE\')')
        db.session.commit()
    except Exception:
        db.session.rollback()  # Type might already exist


class MultiControl(db.Model):
    """Base MultiControl model that will be used as a template for account-specific tables"""
    __abstract__ = True

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(
        ENUM('ACTIVE', 'INACTIVE', name='controlstatus', create_type=True),
        default='ACTIVE',
        nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


def create_multi_control_model(account_id):
    """Dynamically create a MultiControl model for a specific account"""
    create_enum_type()  # Ensure enum type exists
    table_name = f"multi_controls_{account_id}"
    
    return type(
        f"MultiControl_{account_id}",
        (MultiControl,),
        {
            "__tablename__": table_name,
            "__table_args__": {"extend_existing": True}
        }
    )


# Irrigation Management System Models

class Field(db.Model):
    __tablename__ = 'fields'
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    pressure = db.Column(db.Float)
    flow_rate = db.Column(db.Float)
    current_zone = db.Column(db.String(100))
    kml_file = db.Column(db.LargeBinary)
    shp_file = db.Column(db.LargeBinary)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    equipments = db.relationship("Equipment", backref="field", cascade="all, delete", lazy=True)
    irrigation_plans = db.relationship("IrrigationPlan", backref="field", cascade="all, delete", lazy=True)
    alerts = db.relationship("Alert", backref="field", cascade="all, delete", lazy=True)
    logs = db.relationship("Log", backref="field", cascade="all, delete", lazy=True)


class Equipment(db.Model):
    __tablename__ = 'equipment'
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, nullable=False, index=True)
    field_id = db.Column(db.Integer, db.ForeignKey('fields.id', ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    controller_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    status = db.Column(db.String(50), nullable=False, default='INACTIVE')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    zones = db.relationship("Zone", backref="equipment", cascade="all, delete", lazy=True)
    firmwares = db.relationship("Firmware", backref="equipment", cascade="all, delete", lazy=True)


class Zone(db.Model):
    __tablename__ = 'zones'
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, nullable=False, index=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id', ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    application_rate = db.Column(db.Float)
    area = db.Column(db.Float)
    kml_file = db.Column(db.LargeBinary)
    shp_file = db.Column(db.LargeBinary)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class IrrigationPlan(db.Model):
    __tablename__ = 'irrigation_plans'
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, nullable=False, index=True)
    # Optional user_id if needed; remove foreign key if users table is external or managed elsewhere
    user_id = db.Column(db.Integer, nullable=True)
    field_id = db.Column(db.Integer, db.ForeignKey('fields.id', ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    schedule = db.Column(JSONB)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Alert(db.Model):
    __tablename__ = 'alerts'
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, nullable=False, index=True)
    field_id = db.Column(db.Integer, db.ForeignKey('fields.id', ondelete="CASCADE"), nullable=False, index=True)
    alert_type = db.Column(db.String(100), nullable=False, index=True)
    message = db.Column(db.Text)
    resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Log(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, nullable=False, index=True)
    user_id = db.Column(db.Integer, nullable=True)
    field_id = db.Column(db.Integer, db.ForeignKey('fields.id', ondelete="CASCADE"), nullable=False, index=True)
    event_type = db.Column(db.String(100), index=True)
    event_data = db.Column(JSONB)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Firmware(db.Model):
    __tablename__ = 'firmware'
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, nullable=False, index=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id', ondelete="CASCADE"), nullable=False, index=True)
    version = db.Column(db.String(50), nullable=False, index=True)
    release_date = db.Column(db.DateTime, nullable=False)
    changelog = db.Column(db.Text)
    file_data = db.Column(db.LargeBinary)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False) 