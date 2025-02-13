from app.extensions import db
from app.models.app_model import App

def seed_initial_apps():
    """Seed initial applications into the database"""
    initial_apps = [
        {
            "name": "Task Manager",
            "description": "Manage your tasks efficiently.",
            "icon_url": "http://localhost:5000/static/task_manager.png",
            "app_key": "task_manager",
            "monthly_price": 9.99,
            "yearly_price": 99.99
        },
        {
            "name": "Freezer Monitoring",
            "description": "Monitor freezer temperatures in real-time.",
            "icon_url": None,
            "app_key": "freezer_monitoring",
            "monthly_price": 19.99,
            "yearly_price": 199.99
        }
    ]

    for app_data in initial_apps:
        # Check if app already exists
        existing_app = App.query.filter_by(app_key=app_data["app_key"]).first()
        if not existing_app:
            app = App(**app_data)
            db.session.add(app)
        else:
            # Update existing app with new data
            for key, value in app_data.items():
                setattr(existing_app, key, value)
    
    try:
        db.session.commit()
        print("Successfully seeded initial apps")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding apps: {str(e)}")

if __name__ == "__main__":
    seed_initial_apps() 