from app.extensions import db

class UserApp(db.Model):
    __tablename__ = "user_apps"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    app_id = db.Column(db.Integer, db.ForeignKey("apps.id"), nullable=False)
    access_level = db.Column(db.String(50), default="read")  # Options: read, write, admin

    user = db.relationship("User", back_populates="user_apps")
    app = db.relationship('App', backref=db.backref('installed_by_users', lazy=True))

    def to_dict(self):
        """Converts user-app relationship to dictionary for API responses."""
        return {"user_id": self.user_id, "app_id": self.app_id, "app_name": self.app.name}

    def __repr__(self):
        return f"<UserApp user_id={self.user_id} app_id={self.app_id} access={self.access_level}>"
