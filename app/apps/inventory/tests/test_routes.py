import pytest
import json
from app import create_app, db
from apps.inventory_tracker.models import InventoryItem

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

def test_get_items_empty(client, db_session):
    response = client.get('/api/inventory/')
    assert response.status_code == 200
    assert json.loads(response.data) == []

def test_create_item(client, db_session):
    data = {
        'name': 'Test Item',
        'description': 'Test Description',
        'quantity': 10,
        'unit_price': 9.99,
        'category': 'Test Category',
        'sku': 'TEST123',
        'location': 'Test Location'
    }
    
    response = client.post(
        '/api/inventory/',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert response_data['name'] == data['name']
    assert response_data['quantity'] == data['quantity']

def test_get_item(client, db_session):
    # Create an item first
    item = InventoryItem(name='Test Item', quantity=10)
    db_session.session.add(item)
    db_session.session.commit()
    
    response = client.get(f'/api/inventory/{item.id}')
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data['name'] == 'Test Item'
    assert response_data['quantity'] == 10

def test_update_item(client, db_session):
    # Create an item first
    item = InventoryItem(name='Test Item', quantity=10)
    db_session.session.add(item)
    db_session.session.commit()
    
    update_data = {
        'name': 'Updated Item',
        'quantity': 20
    }
    
    response = client.put(
        f'/api/inventory/{item.id}',
        data=json.dumps(update_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data['name'] == update_data['name']
    assert response_data['quantity'] == update_data['quantity']

def test_delete_item(client, db_session):
    # Create an item first
    item = InventoryItem(name='Test Item', quantity=10)
    db_session.session.add(item)
    db_session.session.commit()
    
    response = client.delete(f'/api/inventory/{item.id}')
    assert response.status_code == 204
    
    # Verify item is deleted
    response = client.get(f'/api/inventory/{item.id}')
    assert response.status_code == 404

def test_adjust_quantity(client, db_session):
    # Create an item first
    item = InventoryItem(name='Test Item', quantity=10)
    db_session.session.add(item)
    db_session.session.commit()
    
    # Test adding inventory
    adjust_data = {
        'quantity': 5,
        'transaction_type': 'in',
        'notes': 'Adding inventory'
    }
    
    response = client.post(
        f'/api/inventory/{item.id}/adjust',
        data=json.dumps(adjust_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data['quantity'] == 15
    
    # Test removing inventory
    adjust_data = {
        'quantity': 3,
        'transaction_type': 'out',
        'notes': 'Removing inventory'
    }
    
    response = client.post(
        f'/api/inventory/{item.id}/adjust',
        data=json.dumps(adjust_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data['quantity'] == 12 