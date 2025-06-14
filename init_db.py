from extensions import db
from models import User, Patient, Doctor, Receptionist, HR, Appointment, Prescription, Invoice, LabTech, LabResult
from werkzeug.security import generate_password_hash
import logging
from sqlalchemy import text

def init_db(app):
    """Initialize the database."""
    print("Starting database initialization...")
    with app.app_context():
        try:
            # Create all tables
            print("Creating all tables...")
            db.create_all()
            
            # Create default HR user if not exists
            print("Checking for default HR user...")
            if not User.query.filter_by(username='admin').first():
                print("Creating default HR user...")
                admin = User(
                    username='admin',
                    role='hr'
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                
                hr = HR(
                    name='Admin',
                    phone='1234567890',
                    email='admin@hospital.com',
                    user_id=admin.id
                )
                db.session.add(hr)
                db.session.commit()
                print("Default HR user created:")
                print("Username: admin")
                print("Password: admin123")
            else:
                print("Default HR user already exists")
            
            print("Database initialized successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing database: {str(e)}")
            print(f"Error type: {type(e)}")
            print(f"Error args: {e.args}")
            raise 