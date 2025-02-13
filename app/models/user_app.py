from app.extensions import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

class UserApp(db.Model):
    """Model to track which apps are installed for which accounts"""
    __tablename__ = 'user_apps'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    app_name = db.Column(db.String(255), nullable=False)
    is_installed = db.Column(db.Boolean, default=False)
    installed_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    uninstalled_at = db.Column(db.DateTime, nullable=True)  # Track when app was uninstalled

    # Add relationship to Account model
    account = db.relationship('Account', backref=db.backref('installed_apps', lazy=True))

    __table_args__ = (
        db.UniqueConstraint('account_id', 'app_name', name='uix_account_app'),
    )

#     def to_dict(self):
#         """Converts user-app relationship to dictionary for API responses."""
#         return {"user_id": self.user_id, "app_id": self.app_id, "app_name": self.app.name}

#     def __repr__(self):
#         return f"<UserApp user_id={self.user_id} app_id={self.app_id} access={self.access_level}>"
