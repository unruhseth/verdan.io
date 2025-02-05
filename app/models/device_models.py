from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Table
from sqlalchemy.orm import relationship
from datetime import datetime

from app import db  # Import the database instance

class Device(db.Model):
    __tablename__ = 'devices'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    app_id = db.Column(db.Integer, db.ForeignKey('apps.id'), nullable=False)
    sim_card_id = db.Column(db.String(20), db.ForeignKey('sim_cards.id'), nullable=True)
    status = db.Column(db.String(50), default='inactive')
    extra_data = db.Column(db.JSON, nullable=True)  # Renamed from metadata

    app = db.relationship('App', back_populates='devices')
    sim_card = db.relationship('SIMCard', back_populates='device')

    # FIX: Ensure it matches DeviceGroup
    groups = db.relationship("DeviceGroup", secondary="device_group_association", back_populates="devices")


class SIMCard(db.Model):
    __tablename__ = 'sim_cards'
    
    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.Integer, db.ForeignKey("apps.id"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    iccid = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.String(50), default='inactive')
    extra_data = db.Column(db.JSON, nullable=True)  # Renamed from metadata

    user = db.relationship('User', back_populates='sim_cards')
    device = db.relationship('Device', back_populates='sim_card', uselist=False)
    app = db.relationship('App', back_populates='sim_cards')




class DeviceGroup(db.Model):
    __tablename__ = 'device_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    
    # FIX: Ensure it matches Device
    devices = db.relationship('Device', secondary='device_group_association', back_populates='groups')

    # ✅ FIX: Add Relationship to OTAUpdate
    ota_updates = db.relationship("OTAUpdate", back_populates="group")

    # FIX: Add association table
device_group_association = db.Table(
    'device_group_association',
    db.metadata,
    db.Column('device_id', db.Integer, db.ForeignKey('devices.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('device_groups.id'), primary_key=True),
    extend_existing=True  # This prevents duplicate definition errors
)



class OTAUpdate(db.Model):
    __tablename__ = 'ota_updates'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('device_groups.id'), nullable=False)
    version = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='pending')
    timestamp = db.Column(db.DateTime, default=db.func.now())

    group = db.relationship('DeviceGroup', back_populates='ota_updates')


# device_group_association = db.Table(
#     'device_group_association',
#     db.Column('device_id', db.Integer, db.ForeignKey('devices.id')),
#     db.Column('group_id', db.Integer, db.ForeignKey('device_groups.id'))
# )
