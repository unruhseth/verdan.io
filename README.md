# Verdan Platform Architecture

## Overview
Verdan is a modular, multi-tenant platform for building and managing IoT and irrigation control applications. The platform consists of a Flask-based backend API and a React-based admin panel frontend.

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Core Components](#core-components)
3. [Authentication & Authorization](#authentication--authorization)
4. [Database Design](#database-design)
5. [App System](#app-system)
6. [API Design](#api-design)
7. [Development Setup](#development-setup)
8. [App Development](#app-development)
9. [Deployment](#deployment)
10. [Contributing](#contributing)

## System Architecture

### High-Level Overview
```
Verdan Platform
├── Backend (Flask)
│   ├── Core System
│   │   ├── Authentication
│   │   ├── Multi-tenancy
│   │   ├── App Management
│   │   └── Database Migrations
│   │
│   ├── Apps
│   │   ├── App Generator
│   │   ├── Dynamic Models
│   │   └── API Endpoints
│   │
│   └── Services
│       ├── IoT Integration
│       ├── Payment Processing
│       └── Notification System
│
└── Frontend (React)
    ├── Admin Panel
    ├── App Registry
    ├── Dynamic UI Components
    └── State Management
```

### Key Features
- **Multi-tenancy**: Each account has isolated data and apps
- **Dynamic App Loading**: Apps can be installed/uninstalled per account
- **Automated App Generation**: Tools for rapid app development
- **Modular Architecture**: Easy to extend and customize

## Core Components

### 1. Database Layer
- **SQLAlchemy ORM**: Database abstraction and model management
- **Alembic**: Database migrations and schema versioning
- **Dynamic Tables**: Per-account table creation for apps

### 2. Authentication System
- **JWT-based**: Secure token-based authentication
- **Role-Based Access**: Granular permission control
- **Multi-tenant Security**: Account isolation

### 3. App Management
- **App Generator**: Automated app creation tools
- **App Installer**: Dynamic app installation/uninstallation
- **App Registry**: Central app management

### 4. API Layer
- **RESTful Design**: Consistent API patterns
- **OpenAPI/Swagger**: API documentation
- **Rate Limiting**: Request throttling

## Authentication & Authorization

### JWT Implementation
```python
# Token Structure
{
    "sub": "user_id",
    "account_id": "account_id",
    "role": "user_role",
    "exp": expiration_time
}
```

### Role Hierarchy
1. **master_admin**: Platform-wide access
2. **admin**: Cross-account access
3. **account_admin**: Single account management
4. **user**: Basic app access

### Security Measures
- CORS configuration
- Rate limiting
- Input validation
- SQL injection prevention
- XSS protection

## Database Design

### Core Tables
```sql
-- Accounts
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    subdomain VARCHAR(255) UNIQUE,
    created_at TIMESTAMP
);

-- Users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id),
    email VARCHAR(255),
    password_hash VARCHAR(255),
    role VARCHAR(50),
    created_at TIMESTAMP
);

-- Apps
CREATE TABLE apps (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    version VARCHAR(50),
    config JSONB
);

-- User Apps
CREATE TABLE user_apps (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id),
    app_name VARCHAR(255),
    is_installed BOOLEAN,
    installed_at TIMESTAMP
);
```

### Dynamic Tables
Each app creates account-specific tables:
```sql
CREATE TABLE {table_name}_{account_id} (
    id UUID PRIMARY KEY,
    account_id INTEGER,
    -- App-specific fields
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## App System

### App Generator
The app generator system automates the creation of:
1. Database models
2. API endpoints
3. Frontend components
4. Tests
5. Documentation

### App Import Tool
The platform includes a powerful import tool (`import_app.py`) that handles:
1. App validation and structure checking
2. Frontend and backend file copying
3. App registration in the system
4. Frontend registry updates
5. Database setup

Usage:
```bash
python import_app.py /path/to/your/app/directory [--api-dir PATH] [--frontend-dir PATH] [--force] [--dry-run] [--verbose]
```

### Configuration Options
```yaml
app:
  name: string          # Required: Unique app identifier
  title: string        # Required: Display name
  description: string  # Required: App description
  pricing:            # Required: App pricing
    monthly: float
    yearly: float
  models:             # Optional: Database models
    - name: string
      fields:
        - name: string
          type: string
          # field options
  frontend:           # Optional: Frontend configuration
    theme: object
    components: array
    routes:           # Optional: Additional routes
      - path: string
        component: string
```

### Installation Process
1. Validate app configuration
2. Create database tables
3. Register routes
4. Update app registry
5. Generate frontend components

## API Design

### RESTful Endpoints
```
/api/v1/
├── auth/
│   ├── login
│   ├── refresh
│   └── logout
├── accounts/
│   ├── create
│   ├── update
│   └── users/
├── apps/
│   ├── install
│   ├── uninstall
│   └── configure
└── {app_name}/
    └── {app_endpoints}
```

### Response Format
```json
{
    "success": boolean,
    "data": object | array,
    "error": string | null,
    "metadata": {
        "pagination": object,
        "version": string
    }
}
```

## Development Setup

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Node.js 14+
- Redis (optional)

### Frontend Dependencies
```json
{
  "dependencies": {
    "@ant-design/icons": "^5.6.1",
    "@tanstack/react-query": "^5.66.0",
    "antd": "^5.24.0",
    "axios": "^1.7.9",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^7.1.5"
  }
}
```

### Initial Setup
1. Clone the repository:
```bash
git clone https://github.com/your-org/verdan-api.git
cd verdan-api
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings:
# DATABASE_URL=postgresql://verda_user@localhost/verdan_db
# SECRET_KEY=your-secret-key
# JWT_SECRET_KEY=your-jwt-secret
```

5. Initialize database:
```bash
# Create database
createdb verdan_db

# Run migrations
flask db upgrade

# Create initial admin user
python create_initial_admin.py
```

### Running the Development Server
```bash
# Start Flask development server
flask run --debug

# Default credentials:
# Email: seth@verdan.io
# Password: verdan
```

## App Development

### Creating a New App
1. Use the app generator:
```bash
python manage.py create_app --name your_app_name
```

2. Or use the app template:
```bash
cp -r app/apps/app_template app/apps/your_app_name
```

3. Configure your app:
```yaml
# app.yaml
app:
  name: "your_app"
  title: "Your App"
  description: "Your app description"
  models:
    - name: "YourModel"
      fields:
        - name: "field_name"
          type: "string"
          # ... more fields
```

### Importing External Apps
Use the import_app script:
```bash
python import_app.py /path/to/your/app
```

The app directory should have this structure:
```
your_app/
├── app.yaml           # App configuration
├── backend/
│   ├── models.py     # Database models
│   ├── routes.py     # API endpoints
│   ├── services.py   # Business logic
│   └── install.py    # Installation handlers
├── frontend/
│   ├── pages/        # React pages
│   └── components/   # React components
└── tests/            # Test files
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_your_app.py

# Run with coverage
pytest --cov=app tests/
```

## Common Issues & Solutions

### App Installation Issues
1. **Enum Type Errors**: Add `create_type=False` to ENUM columns if types already exist
2. **Table Creation**: Use `extend_existing=True` in table args
3. **Missing Dependencies**: Check app.yaml for required packages

### Database Issues
1. **Migration Conflicts**: Reset migrations with `flask db stamp head`
2. **Table Exists**: Use `drop_all()` and recreate tables
3. **Connection Issues**: Verify DATABASE_URL in .env

### Authentication Issues
1. **Token Expired**: Re-login to get fresh token
2. **Permission Denied**: Check user role and account_id
3. **Missing Token**: Include Authorization header

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

For detailed development guides, see:
- [App Development Guide](app/apps/APP_DEVELOPMENT_GUIDE.md)
- [Frontend Development Guide](frontend/FRONTEND_DEVELOPMENT_GUIDE.md)

## Deployment

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis (for caching, optional)
- Node.js 16+ (for frontend)

### Environment Setup
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Update the environment variables in `.env` with your production values:
   - Set `FLASK_ENV=production`
   - Configure your production database URL
   - Set secure keys for JWT and application
   - Configure your production frontend URL
   - Set up your Stripe and Soracom credentials

### Database Setup
1. Create your production database:
   ```bash
   createdb verdan_db
   ```

2. Run database migrations:
   ```bash
   flask db upgrade
   ```

3. Create initial admin user:
   ```bash
   python create_initial_admin.py
   ```

### Production Server Setup
1. Install production dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure your web server (e.g., Nginx) to proxy requests to the application.

3. Set up SSL certificates for secure communication.

4. Configure your WSGI server (e.g., Gunicorn):
   ```bash
   gunicorn -w 4 -b 127.0.0.1:5000 'app:create_app()'
   ```

### App Installation
1. Use the import_app.py script to install new apps:
   ```bash
   python import_app.py /path/to/your/app
   ```

2. The script will:
   - Validate the app structure
   - Copy app files to the correct location
   - Register the app in the database
   - Update necessary configurations

### Monitoring and Maintenance
1. Set up logging to monitor application performance:
   ```python
   # In your production.py config
   LOGGING = {
       'version': 1,
       'handlers': {
           'file': {
               'class': 'logging.FileHandler',
               'filename': 'verdan.log'
           }
       },
       'root': {
           'level': 'INFO',
           'handlers': ['file']
       }
   }
   ```

2. Configure backup schedules for your database and uploaded files.

3. Set up monitoring for system health and performance.

### Security Considerations
1. Ensure all sensitive environment variables are properly secured
2. Configure proper firewall rules
3. Set up rate limiting for API endpoints
4. Regularly update dependencies for security patches
5. Implement proper backup and disaster recovery procedures

### Scaling
1. Configure database connection pooling
2. Set up caching with Redis if needed
3. Consider using a load balancer for multiple application instances
4. Implement proper horizontal scaling strategies

## Support and Resources

### Documentation
- API Documentation: `/docs/api`
- Frontend Documentation: `/docs/frontend`
- App Development Guide: `/docs/apps`

### Getting Help
- GitHub Issues
- Development Team Contact
- Community Forums

### Useful Commands
```bash
# Create new app
python manage.py create-app --name="my_app" --interactive

# Database operations
flask db migrate -m "description"
flask db upgrade

# Run development server
flask run

# Install app
python -c "from app_installer import AppInstaller; AppInstaller().install_app('app_name', account_id=1)"
```
