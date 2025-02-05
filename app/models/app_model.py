from app.extensions import db
from datetime import datetime
from app.models.user_app import UserApp  # Ensure correct import

class App(db.Model):
    __tablename__ = 'apps'  # Explicitly define table name if preferred

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_apps = db.relationship("UserApp", back_populates="app", cascade="all, delete-orphan")
    devices = db.relationship('Device', back_populates='app')
    sim_cards = db.relationship('SIMCard', back_populates='app')



    # Relationships or other attributes can be added here
    def to_dict(self):
        """Converts app model to dictionary for API responses."""
        return {"id": self.id, "name": self.name, "description": self.description}

    def __repr__(self):
        return f'<App {self.name}>'
