from app.extensions import db
from datetime import datetime


def create_app_tables(account_id):
    """
    Create the table models for a specific account.
    Return a dictionary of table_name: model pairs.
    """
    
    # Example of a dynamic table model
    class ExampleTable(db.Model):
        """Example table that will be created for each account"""
        __tablename__ = f"example_table_{account_id}"
        __table_args__ = {"extend_existing": True}

        id = db.Column(db.Integer, primary_key=True)
        account_id = db.Column(db.Integer, nullable=False, index=True)
        name = db.Column(db.String(100), nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Return a dictionary of all tables this app needs
    return {
        f"example_table_{account_id}": ExampleTable
    } 