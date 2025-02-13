from app.extensions import db
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID

class App(db.Model):
    """Model for available applications in the system"""
    __tablename__ = 'apps'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    icon_url = db.Column(db.String(512), nullable=True)
    app_key = db.Column(db.String(255), nullable=False, unique=True)  # Internal key for app identification
    is_active = db.Column(db.Boolean, default=True)
    monthly_price = db.Column(db.Numeric(10, 2), nullable=True)  # Price with 2 decimal places
    yearly_price = db.Column(db.Numeric(10, 2), nullable=True)  # Price with 2 decimal places

    def to_dict(self):
        """Convert app to dictionary for API responses"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "icon_url": self.icon_url,
            "monthly_price": float(self.monthly_price) if self.monthly_price is not None else None,
            "yearly_price": float(self.yearly_price) if self.yearly_price is not None else None
        }

    def to_admin_dict(self):
        """Convert app to dictionary for admin API responses"""
        return {
            "id": self.app_key,  # Use app_key as ID for admin interface
            "name": self.name,
            "description": self.description,
            "icon_url": self.icon_url,
            "monthly_price": float(self.monthly_price) if self.monthly_price is not None else None,
            "yearly_price": float(self.yearly_price) if self.yearly_price is not None else None,
            "is_active": self.is_active
        }
