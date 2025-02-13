import pytest
from datetime import datetime
from app import create_app, db
from apps.inventory_tracker.models import InventoryItem, InventoryTransaction

@pytest.fixture
def app():
    app = create_app('testing')
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db_session(app):
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

def test_create_inventory_item(db_session):
    item = InventoryItem(
        name='Test Item',
        description='Test Description',
        quantity=10,
        unit_price=9.99,
        category='Test Category',
        sku='TEST123',
        location='Test Location'
    )
    
    db_session.session.add(item)
    db_session.session.commit()
    
    assert item.id is not None
    assert item.name == 'Test Item'
    assert item.quantity == 10
    assert isinstance(item.created_at, datetime)
    assert isinstance(item.updated_at, datetime)

def test_create_inventory_transaction(db_session):
    # Create an item first
    item = InventoryItem(name='Test Item', quantity=10)
    db_session.session.add(item)
    db_session.session.commit()
    
    # Create a transaction
    transaction = InventoryTransaction(
        item_id=item.id,
        transaction_type='in',
        quantity=5,
        notes='Test transaction'
    )
    
    db_session.session.add(transaction)
    db_session.session.commit()
    
    assert transaction.id is not None
    assert transaction.item_id == item.id
    assert transaction.quantity == 5
    assert transaction.transaction_type == 'in'
    assert isinstance(transaction.transaction_date, datetime)

def test_inventory_item_to_dict(db_session):
    item = InventoryItem(
        name='Test Item',
        description='Test Description',
        quantity=10,
        unit_price=9.99,
        category='Test Category',
        sku='TEST123',
        location='Test Location'
    )
    
    db_session.session.add(item)
    db_session.session.commit()
    
    item_dict = item.to_dict()
    
    assert item_dict['name'] == 'Test Item'
    assert item_dict['quantity'] == 10
    assert item_dict['unit_price'] == 9.99
    assert isinstance(item_dict['created_at'], str)
    assert isinstance(item_dict['updated_at'], str) 