import os
import sys
import pytest
from flask import Flask
from app import create_app
from app.extensions import db

# Add the app directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('TEST_DATABASE_URL', 'postgresql://verda_user@localhost/verdan_db_test')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client() 