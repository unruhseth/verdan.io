from app.extensions import db
from datetime import datetime
#from app.models.user_app import UserApp  # Ensure correct import

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    email = db.Column(db.String, unique=True, nullable=True)  # Now nullable
    phone_number = db.Column(db.String, unique=True, nullable=True)  # New column
    password_hash = db.Column(db.String, nullable=False)
    name = db.Column(db.String)
    role = db.Column(db.String, default="user")  # Roles: master_admin, account_admin, user
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    #user_apps = db.relationship("UserApp", back_populates="user", cascade="all, delete-orphan")
    #sim_cards = db.relationship('SIMCard', back_populates='user')

    #subscription_status = db.Column(db.String(20), default='Active')  # Active, Paused, Canceled
    #subscription_type = db.Column(db.String(10), default='Monthly')  # Monthly, Yearly
    
    # ✅ Add use_alter=True to resolve circular dependency
    #default_payment_method_id = db.Column(
    #     db.Integer,
    #     db.ForeignKey('payment_method.id', use_alter=True),
    #     nullable=True
    # )

    def __repr__(self):
        return f"<User {self.email}, Subscription: {self.subscription_status}>"
    
