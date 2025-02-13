from app import create_app
from app.extensions import db
from app.models.account import Account
from app.models.user import User
from werkzeug.security import generate_password_hash
from datetime import datetime

app = create_app()

with app.app_context():
    # Check if account already exists
    account = Account.query.filter_by(name="Verdan").first()
    
    if not account:
        # Create a master account
        account = Account(
            name="Verdan",
            subdomain="verdan",
            created_at=datetime.utcnow()
        )
        db.session.add(account)
        db.session.commit()
        print(f"Created master account with ID: {account.id}")
    else:
        print(f"Using existing account with ID: {account.id}")

    # Check if user already exists
    user = User.query.filter_by(email="seth@verdan.io").first()
    
    if not user:
        # Create a master admin user with explicit method='pbkdf2:sha256'
        user = User(
            account_id=account.id,
            email="seth@verdan.io",
            password_hash=generate_password_hash("verdan", method='pbkdf2:sha256'),
            name="Seth Unruh",
            role="master_admin",
            created_at=datetime.utcnow()
        )
        db.session.add(user)
        db.session.commit()
        print(f"Created master admin user with ID: {user.id}")
    else:
        # Update existing user's password hash
        user.password_hash = generate_password_hash("verdan", method='pbkdf2:sha256')
        db.session.commit()
        print(f"Updated password for existing user with ID: {user.id}")

    print("\nMaster Admin Credentials:")
    print("Email: seth@verdan.io")
    print("Password: verdan")
    print("Role: master_admin") 