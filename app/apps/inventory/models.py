from app.extensions import db
from datetime import datetime
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSONB
from sqlalchemy import text


def create_enum_types():
    """Create the enum types needed for the inventory app."""
    try:
        # Create transaction type enum
        db.session.execute(text("""
            DO $$ BEGIN
                CREATE TYPE transaction_type AS ENUM ('purchase', 'sale', 'adjustment', 'transfer');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        
        # Create unit type enum
        db.session.execute(text("""
            DO $$ BEGIN
                CREATE TYPE unit_type AS ENUM ('piece', 'kg', 'g', 'l', 'ml', 'box', 'pack');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        
        db.session.commit()
    except Exception as e:
        print(f"Error creating enum types: {e}")
        db.session.rollback()


class Category(db.Model):
    """Category model for organizing inventory items"""
    __tablename__ = 'inventory_categories'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    account_id = db.Column(db.Integer, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    parent_id = db.Column(UUID(as_uuid=True), db.ForeignKey('inventory_categories.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'account_id': self.account_id,
            'name': self.name,
            'description': self.description,
            'parent_id': str(self.parent_id) if self.parent_id else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Item(db.Model):
    """Item model"""
    __tablename__ = 'inventory_items'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    account_id = db.Column(db.Integer, nullable=False, index=True)
    category_id = db.Column(UUID(as_uuid=True), db.ForeignKey('inventory_categories.id'), nullable=True)
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    sku = db.Column(db.String(50))  # Unique per account, not globally
    barcode = db.Column(db.String(50))
    unit_type = db.Column(ENUM('piece', 'kg', 'g', 'l', 'ml', 'box', 'pack', name='unit_type', create_type=False), nullable=False)
    
    quantity = db.Column(db.Float, default=0, nullable=False)
    min_quantity = db.Column(db.Float, default=0)
    max_quantity = db.Column(db.Float)
    reorder_point = db.Column(db.Float)
    
    cost_price = db.Column(db.Float)
    selling_price = db.Column(db.Float)
    
    location = db.Column(db.String(100))
    supplier = db.Column(db.String(100))
    notes = db.Column(db.Text)
    tags = db.Column(JSONB)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Add unique constraint for SKU per account
    __table_args__ = (
        db.UniqueConstraint('account_id', 'sku', name='uq_item_account_sku'),
    )

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'account_id': self.account_id,
            'category_id': str(self.category_id) if self.category_id else None,
            'name': self.name,
            'description': self.description,
            'sku': self.sku,
            'barcode': self.barcode,
            'unit_type': self.unit_type,
            'quantity': self.quantity,
            'min_quantity': self.min_quantity,
            'max_quantity': self.max_quantity,
            'reorder_point': self.reorder_point,
            'cost_price': self.cost_price,
            'selling_price': self.selling_price,
            'location': self.location,
            'supplier': self.supplier,
            'notes': self.notes,
            'tags': self.tags,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Transaction(db.Model):
    """Transaction model for tracking inventory changes"""
    __tablename__ = 'inventory_transactions'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    account_id = db.Column(db.Integer, nullable=False, index=True)
    item_id = db.Column(UUID(as_uuid=True), db.ForeignKey('inventory_items.id'), nullable=False)
    
    transaction_type = db.Column(ENUM('purchase', 'sale', 'adjustment', 'transfer', name='transaction_type', create_type=False), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float)
    
    reference = db.Column(db.String(100))
    notes = db.Column(db.Text)
    transaction_metadata = db.Column(JSONB)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'account_id': self.account_id,
            'item_id': str(self.item_id),
            'transaction_type': self.transaction_type,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'reference': self.reference,
            'notes': self.notes,
            'transaction_metadata': self.transaction_metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


def create_app_tables(account_id):
    """Get the models for the inventory app."""
    return {
        'inventory_categories': Category,
        'inventory_items': Item,
        'inventory_transactions': Transaction
    } 