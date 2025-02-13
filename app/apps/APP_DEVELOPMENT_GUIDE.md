# Verdan App Development Guide

## Overview
This guide explains how to develop apps for the Verdan platform. Apps are self-contained modules that provide specific functionality through backend APIs. Each app follows a standard structure and can be installed/uninstalled per account.

## Table of Contents
1. [App Structure](#app-structure)
2. [Backend Development](#backend-development)
3. [Database Models](#database-models)
4. [API Routes](#api-routes)
5. [Services Layer](#services-layer)
6. [Installation Handlers](#installation-handlers)
7. [Testing](#testing)
8. [Example App](#example-app)

## App Structure
```
app_name/
├── __init__.py          # App initialization
├── models.py            # Database models
├── routes.py            # API endpoints
├── services.py          # Business logic
├── install.py           # Installation handlers
├── app.yaml            # App configuration
└── tests/              # Test files
    ├── __init__.py
    ├── test_models.py
    ├── test_routes.py
    └── test_services.py
```

## Backend Development

### Configuration (app.yaml)
Every app must include an `app.yaml` file with the following structure:
```yaml
app:
  name: "app-name"           # Required: Unique identifier for the app
  title: "App Title"         # Required: Display name
  version: "1.0.0"          # Required: Semantic version
  description: "..."         # Optional: App description
  pricing:                   # Optional: Pricing information
    monthly: 0
    yearly: 0
```

### Database Models
- Use SQLAlchemy models with proper type annotations
- Always include `account_id` in models for multi-tenancy
- Use UUIDs for primary keys
- Include standard timestamps (`created_at`, `updated_at`)
- Add appropriate indexes for frequently queried fields

Example model:
```python
from uuid import uuid4
from app.extensions import db
from datetime import datetime

class YourModel(db.Model):
    __tablename__ = 'your_table'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    account_id = db.Column(db.Integer, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

### API Routes
- Use Flask blueprints with proper URL prefixes
- Include CORS configuration
- Implement proper authentication and authorization
- Use standard HTTP methods and status codes
- Include comprehensive error handling
- Document API endpoints with docstrings

Example route:
```python
from flask import Blueprint, request, jsonify
from app.utils.auth_helpers import any_admin_required
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin

app_name_bp = Blueprint("app_name", __name__, url_prefix="/app_name")

@app_name_bp.route("/resource", methods=["POST"])
@cross_origin()
@jwt_required()
@any_admin_required
def create_resource():
    """Create a new resource"""
    try:
        data = request.get_json()
        # Implementation
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### Services Layer
- Implement business logic in service classes
- Use type hints for better code clarity
- Return tuples of (success, result) for operations
- Handle database transactions properly

Example service:
```python
from typing import Tuple, Dict, Any

class YourService:
    @staticmethod
    def create_resource(account_id: int, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        try:
            # Implementation
            db.session.commit()
            return True, result
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}
```

### Installation Handlers
- Implement both install and uninstall functions
- Handle database table creation/deletion
- Update UserApp records
- Include proper error handling

Example handler:
```python
def install_app_name(account_id):
    """Install the app for a specific account"""
    try:
        # Create tables
        # Register in user_apps
        return True
    except Exception as e:
        db.session.rollback()
        return False

def uninstall_app_name(account_id):
    """Uninstall the app for a specific account"""
    try:
        # Cleanup data
        # Update user_apps record
        return True
    except Exception as e:
        db.session.rollback()
        return False
```

## Testing
- Write comprehensive tests for models, routes, and services
- Use pytest fixtures for database setup
- Test both success and error cases
- Include authentication/authorization tests
- Test installation/uninstallation process

Example test:
```python
def test_create_resource(client, init_database):
    response = client.post(
        '/app_name/resource',
        json={'name': 'Test'},
        headers={'Authorization': f'Bearer {test_token}'}
    )
    assert response.status_code == 201
    assert 'id' in response.json
```

## Example App
For a complete example, refer to the app template in `app/apps/app_template/`. You can use it as a starting point for new apps:

1. Copy the template directory:
```bash
cp -r app/apps/app_template app/apps/your_app_name
```

2. Update the app configuration in `app.yaml`

3. Customize the models, routes, and services for your app

4. Write tests for your functionality

5. Import the app using the import script:
```bash
python import_app.py /path/to/your_app
``` 