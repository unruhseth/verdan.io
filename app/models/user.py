from app.extensions import db
from datetime import datetime
from app.models.user_app import UserApp  # Ensure correct import

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    name = db.Column(db.String)
    role = db.Column(db.String, default="user")  # Roles: master_admin, account_admin, user
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_apps = db.relationship("UserApp", back_populates="user", cascade="all, delete-orphan")
    sim_cards = db.relationship('SIMCard', back_populates='user')
